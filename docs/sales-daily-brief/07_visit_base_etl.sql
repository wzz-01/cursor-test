-- ============================================================
-- ⑥拜访底表 ETL（优化稿）
-- 源：hive.dw.dwd_sales_hds_visit_detail + 门店/人员/客户维
-- 目标建议：market_db.dwd_sales_visit_detail（按实际权限改库名）
-- 粒度：1 次有效拜访 × 门店 × 人员（过滤后）
-- ============================================================

-- ---------- 优化要点（相对原稿） ----------
-- 1. c_code CASE 只算一次（CTE），避免 JOIN ON 里复制三遍
-- 2. 对 md 的过滤在 WHERE 中会把 LEFT JOIN 变成实质 INNER → 改成 INNER JOIN，意图更清晰
-- 3. DATE(vs.visit_date) 包一层易伤分区裁剪 → 用范围谓词
-- 4. J 按「销售组」DISTINCT 大区/省区 可能一对多放大行 → 销售组维单独去重保 1 行
-- 5. jdbc_sqlserve 跨源 JOIN 贵 → 底表一次物化后，智能体只读本表
-- 6. WHERE 已限定 is_finished=1，vs_is_finished 恒为 1，仍保留便于与源对齐核对
-- 7. 补齐⑥常用衍生：是否负责人、经销编码/门店编码便于 COUNT DISTINCT

CREATE TABLE IF NOT EXISTS market_db.dwd_sales_visit_detail
DUPLICATE KEY(riqi, c_shengqu, mendian_code, ry_code)
COMMENT '省区日简报-拜访明细底表；有效已完成拜访'
PARTITION BY RANGE(riqi) ()
DISTRIBUTED BY HASH(c_shengqu) BUCKETS 16
PROPERTIES (
    "replication_num" = "3",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "DAY",
    "dynamic_partition.start" = "-400",
    "dynamic_partition.end" = "3",
    "dynamic_partition.prefix" = "p",
    "dynamic_partition.buckets" = "16"
);

-- 日常增量：按业务日重刷（示例：刷昨天；首次全量把 start 改成 2024-07-01）
-- DELETE FROM market_db.dwd_sales_visit_detail WHERE riqi >= '${biz_date}' AND riqi < DATE_ADD('${biz_date}', 1);
-- 或 INSERT OVERWRITE 分区（按集群语法）

INSERT INTO market_db.dwd_sales_visit_detail
WITH
-- ① 拜访 + 门店：先收窄事实，并只算一次经销客户编码
visit_store AS (
    SELECT
        vs.visit_date,
        DATE(vs.visit_date) AS riqi,
        DATE_FORMAT(vs.visit_date, '%Y-%m-01') AS yuefen,
        vs.visit_type AS vs_visit_type,
        vs.customer_code AS mendian_code,
        vs.customer_name AS mendian_name,
        COALESCE(md.store_type, '未知') AS mendian_type,
        md.dealer_id,
        md.store_dept_name,
        vs.visitor,
        vs.emp_position AS vs_emp_position,
        /* 经销客户编码映射：只在这里写一遍 */
        CASE
            WHEN md.dealer_id LIKE '19%' THEN CONCAT('10', RIGHT(md.dealer_id, 6))
            WHEN vs.customer_code LIKE '2%' THEN vs.customer_code
            WHEN md.dealer_id IS NULL THEN '99999999'
            ELSE md.dealer_id
        END AS c_code,
        CASE WHEN vs.is_finished = '1' THEN 1 ELSE 0 END AS vs_is_finished
    FROM hive.dw.dwd_sales_hds_visit_detail vs
    INNER JOIN hive.dw.dim_sales_hds_store md
        ON vs.customer_code = md.store_code
       AND md.store_cooperate_status = '1'
       AND md.store_dept_name NOT LIKE '香港%'
       AND md.store_code NOT LIKE 'T%'
    WHERE vs.status = '1'
      AND vs.is_finished = '1'
      AND vs.approval_status = '1'
      AND vs.visit_status = '1'
      /* 分区友好：尽量别包 DATE()；若 visit_date 为 DATETIME 用半开区间 */
      AND vs.visit_date >= '${biz_date}'          -- 例：'2024-07-01' 或昨天
      AND vs.visit_date <  DATE_ADD('${biz_date}', INTERVAL 1 DAY)
      -- 全量首次：AND vs.visit_date >= '2024-07-01'
),

-- ② 销售组 → 大区/省区 兜底维：每个销售组只留 1 行，避免 DISTINCT 后一对多撑爆
sales_group_fallback AS (
    SELECT
        销售组,
        MAX(大区) AS 大区,   -- 若同组多区，改成业务指定规则（如按主省区）
        MAX(省区) AS 省区
    FROM jdbc_sqlserve.dbo.Customers_ph
    WHERE 销售组 IS NOT NULL AND 销售组 <> ''
    GROUP BY 销售组
)

SELECT
    v.yuefen,
    v.riqi,
    v.vs_visit_type,

    v.mendian_code,
    v.mendian_name,
    v.mendian_type,
    v.c_code,

    COALESCE(dim_cust.region_name, c.大区, j.大区) AS c_daqu,
    COALESCE(dim_cust.province_region_name, c.省区, j.省区) AS c_shengqu,
    COALESCE(dim_cust.sales_group_name, c.销售组, v.store_dept_name) AS c_xiaoshouzu,
    c.直营经销 AS c_qudao,
    c.核心客户标签a AS is_hexin1,
    c.核心客户标签 AS c_hexin1_type,
    c.客户类型 AS c_kehu_type,

    ry.emp_code AS ry_code,
    ry.emp_name AS ry_name,
    v.vs_emp_position,
    ry.org_name,
    ry.person_belong AS ry_positiontype,
    COALESCE(ry.emp_position, v.vs_emp_position, ry.emp_job) AS ry_position_new,
    v.vs_is_finished,

    /* ⑥简报衍生：负责人（按岗位关键字，落表后可按业务改） */
    CASE
        WHEN COALESCE(ry.emp_position, v.vs_emp_position, ry.emp_job) LIKE '%负责%'
          OR COALESCE(ry.emp_position, v.vs_emp_position, ry.emp_job) LIKE '%主管%'
          OR COALESCE(ry.emp_position, v.vs_emp_position, ry.emp_job) LIKE '%经理%'
        THEN 1 ELSE 0
    END AS is_leader

FROM visit_store v
LEFT JOIN hive.dw.dim_cust_sales_base ry
    ON v.visitor = ry.id
LEFT JOIN jdbc_sqlserve.dbo.Customers_ph c
    ON v.c_code = c.客户编码
LEFT JOIN hive.dw.dim_cust dim_cust
    ON v.c_code = dim_cust.cust_code
LEFT JOIN sales_group_fallback j
    ON j.销售组 = v.store_dept_name
;
