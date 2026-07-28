INSERT INTO market_db.dwd_sales_hds_visit_base

SELECT
-- KEY 前缀（与建表 DUPLICATE KEY 顺序一致）
DATE(vs.visit_date) AS 'riqi',
COALESCE(dim_cust.province_region_name, c.省区 ,J.省区 ) AS c_shengqu,
vs.customer_code AS 'mendian_code',
ry.emp_code AS 'ry_code',

-- 时间相关
DATE_FORMAT(vs.visit_date, '%Y-%m-01') AS 'yuefen',
vs.visit_type AS 'vs_visit_type',

-- 门店相关
vs.customer_name AS 'mendian_name', COALESCE(vs.store_type,'未知') AS 'mendian_type',
vs.c_code AS 'c_code',

-- 架构相关
COALESCE(dim_cust.region_name, c.大区, J.大区) AS c_daqu,
COALESCE(dim_cust.sales_group_name, c.销售组, vs.store_dept_name) AS c_xiaoshouzu,
c.直营经销 AS c_qudao, c.核心客户标签a AS is_hexin1, c.核心客户标签 AS c_hexin1_type, c.客户类型 AS c_kehu_type,

-- 人员相关
ry.emp_name AS 'ry_name', vs.emp_position AS 'vs_emp_position' , ry.org_name AS 'org_name',
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
