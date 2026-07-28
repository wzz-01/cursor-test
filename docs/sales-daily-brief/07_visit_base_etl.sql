-- 拜访底表：建表 + 按当前查询灌数
-- 建表人：xj

-- ---------- 1）建表 ----------
CREATE TABLE IF NOT EXISTS market_db.dwd_sales_hds_visit_base (
    -- 时间相关
    yuefen              VARCHAR(10)    NULL COMMENT '业务月（月初，yyyy-MM-01）',
    riqi                DATE           NOT NULL COMMENT '拜访业务日',
    vs_visit_type       VARCHAR(64)    NULL COMMENT '拜访类型',

    -- 门店相关
    mendian_code        VARCHAR(64)    NULL COMMENT '门店编码',
    mendian_name        VARCHAR(256)   NULL COMMENT '门店名称',
    mendian_type        VARCHAR(64)    NULL COMMENT '门店类型',
    c_code              VARCHAR(64)    NULL COMMENT '经销客户编码（映射后）',

    -- 架构相关
    c_daqu              VARCHAR(128)   NULL COMMENT '大区',
    c_shengqu           VARCHAR(128)   NULL COMMENT '省区',
    c_xiaoshouzu        VARCHAR(128)   NULL COMMENT '销售组',
    c_qudao             VARCHAR(64)    NULL COMMENT '直营经销',
    is_hexin1           VARCHAR(64)    NULL COMMENT '核心客户标签a',
    c_hexin1_type       VARCHAR(128)   NULL COMMENT '核心客户标签',
    c_kehu_type         VARCHAR(64)    NULL COMMENT '客户类型',

    -- 人员相关
    ry_code             VARCHAR(64)    NULL COMMENT '人员编码',
    ry_name             VARCHAR(128)   NULL COMMENT '人员姓名',
    vs_emp_position     VARCHAR(128)   NULL COMMENT '拜访表岗位',
    org_name            VARCHAR(256)   NULL COMMENT '组织名称',
    ry_positiontype     VARCHAR(128)   NULL COMMENT '人员归属',
    ry_position_new     VARCHAR(128)   NULL COMMENT '岗位（合并）',
    vs_is_finished      TINYINT        NULL COMMENT '是否完成拜访：1是0否',

    etl_time            DATETIME       NULL COMMENT '写入时间'
)
DUPLICATE KEY(riqi, c_shengqu, mendian_code, ry_code)
COMMENT '拜访底表-有效已完成拜访；建表人:xj'
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


-- ---------- 2）灌数（字段顺序与建表一致；末列 etl_time） ----------
INSERT INTO market_db.dwd_sales_hds_visit_base
SELECT
-- 时间相关
DATE_FORMAT(vs.visit_date, '%Y-%m-01') AS 'yuefen', DATE(vs.visit_date) AS 'riqi',
vs.visit_type AS 'vs_visit_type',

-- 门店相关
vs.customer_code AS 'mendian_code', vs.customer_name AS 'mendian_name', COALESCE(vs.store_type,'未知') AS 'mendian_type',
vs.c_code AS 'c_code',

-- 架构相关
COALESCE(dim_cust.region_name, c.大区, J.大区) AS c_daqu,
COALESCE(dim_cust.province_region_name, c.省区 ,J.省区 ) AS c_shengqu,
COALESCE(dim_cust.sales_group_name, c.销售组, vs.store_dept_name) AS c_xiaoshouzu,
c.直营经销 AS c_qudao, c.核心客户标签a AS is_hexin1, c.核心客户标签 AS c_hexin1_type, c.客户类型 AS c_kehu_type,

-- 人员相关
ry.emp_code AS 'ry_code', ry.emp_name AS 'ry_name', vs.emp_position AS 'vs_emp_position' , ry.org_name AS 'org_name',
ry.person_belong AS 'ry_positiontype', COALESCE(ry.emp_position, vs.emp_position, ry.emp_job) AS 'ry_position_new',
CASE WHEN vs.is_finished='1' THEN 1 ELSE 0 END AS 'vs_is_finished',

NOW() AS etl_time

FROM (
    -- 拜访底表
    SELECT
        vs0.visit_date, vs0.visit_type, vs0.customer_code, vs0.customer_name,
        vs0.visitor, vs0.emp_position, vs0.is_finished,

        -- 门店相关
        md.store_type, md.store_dept_name,
        CASE WHEN md.dealer_id like '19%' THEN CONCAT('10',RIGHT(md.dealer_id,6) )
             WHEN vs0.customer_code like '2%' THEN vs0.customer_code
             WHEN md.dealer_id IS NULL THEN '99999999' ELSE md.dealer_id END AS c_code
    FROM hive.dw.dwd_sales_hds_visit_detail vs0
    LEFT JOIN hive.dw.dim_sales_hds_store md on vs0.customer_code = md.store_code
    WHERE vs0.status = '1' AND vs0.is_finished = '1'
      AND vs0.approval_status='1' AND vs0.visit_status='1'
      AND md.store_cooperate_status='1'
      AND DATE(vs0.visit_date) >= '2025-07-01'
) vs

-- 人员表
LEFT JOIN hive.dw.dim_cust_sales_base ry on vs.visitor = ry.id
-- 客户表
LEFT JOIN hive.dw.dim_cust dim_cust ON vs.c_code = dim_cust.cust_code
LEFT JOIN jdbc_sqlserve.dbo.Customers_ph c ON vs.c_code = c.客户编码
LEFT JOIN (
                    SELECT 销售组, MAX(大区) AS 大区, MAX(省区) AS 省区 FROM jdbc_sqlserve.dbo.Customers_ph GROUP BY 销售组
                    ) J ON J.销售组 = vs.store_dept_name
WHERE COALESCE(dim_cust.region_name, c.大区, J.大区) IS NOT NULL
;
