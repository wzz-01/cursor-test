-- ⑥拜访底表：按原稿形式，子查询优化
-- 改动：①内层先算出 c_code 只写一遍 ②J 用 GROUP BY 防销售组一对多撑行

SELECT
-- 时间相关
DATE_FORMAT(vs.visit_date, '%Y-%m-01') AS 'yuefen', DATE(vs.visit_date) AS 'riqi',
vs.vs_visit_type AS 'vs_visit_type',

-- 门店相关
vs.mendian_code AS 'mendian_code', vs.mendian_name AS 'mendian_name', vs.mendian_type AS 'mendian_type',
vs.c_code AS 'c_code',

COALESCE(dim_cust.region_name, c.大区, J.大区) AS c_daqu,
COALESCE(dim_cust.province_region_name, c.省区, J.省区) AS c_shengqu,
COALESCE(dim_cust.sales_group_name, c.销售组, vs.store_dept_name) AS c_xiaoshouzu,
c.直营经销 AS c_qudao,
c.核心客户标签a AS is_hexin1, c.核心客户标签 AS c_hexin1_type, c.客户类型 AS c_kehu_type,

-- 人员相关
ry.emp_code AS 'ry_code', ry.emp_name AS 'ry_name', vs.vs_emp_position AS 'vs_emp_position', ry.org_name AS 'org_name',
ry.person_belong AS 'ry_positiontype', COALESCE(ry.emp_position, vs.vs_emp_position, ry.emp_job) AS 'ry_position_new',
vs.vs_is_finished AS 'vs_is_finished'

FROM (
    -- 子查询1：拜访+门店，c_code 只算一次
    SELECT
        vs0.visit_date,
        vs0.visit_type AS vs_visit_type,
        vs0.customer_code AS mendian_code,
        vs0.customer_name AS mendian_name,
        COALESCE(md.store_type, '未知') AS mendian_type,
        md.store_dept_name,
        vs0.visitor,
        vs0.emp_position AS vs_emp_position,
        CASE
            WHEN md.dealer_id LIKE '19%' THEN CONCAT('10', RIGHT(md.dealer_id, 6))
            WHEN vs0.customer_code LIKE '2%' THEN vs0.customer_code
            WHEN md.dealer_id IS NULL THEN '99999999'
            ELSE md.dealer_id
        END AS c_code,
        CASE WHEN vs0.is_finished = '1' THEN 1 ELSE 0 END AS vs_is_finished
    FROM hive.dw.dwd_sales_hds_visit_detail vs0
    LEFT JOIN hive.dw.dim_sales_hds_store md ON vs0.customer_code = md.store_code
    WHERE vs0.status = '1' AND vs0.is_finished = '1'
      AND vs0.approval_status = '1' AND vs0.visit_status = '1'
      AND md.store_cooperate_status = '1'
      AND md.store_dept_name NOT LIKE '香港%'
      AND md.store_code NOT LIKE 'T%'
      -- AND FIND_IN_SET(md.store_type, @store_types)
      AND DATE(vs0.visit_date) >= '2024-07-01'
) vs

LEFT JOIN hive.dw.dim_cust_sales_base ry ON vs.visitor = ry.id

LEFT JOIN jdbc_sqlserve.dbo.Customers_ph c ON vs.c_code = c.客户编码

LEFT JOIN hive.dw.dim_cust dim_cust ON vs.c_code = dim_cust.cust_code

LEFT JOIN (
    -- 子查询2：销售组兜底维，每组一行，避免 DISTINCT 后一对多放大
    SELECT 销售组, MAX(大区) AS 大区, MAX(省区) AS 省区
    FROM jdbc_sqlserve.dbo.Customers_ph
    WHERE 销售组 IS NOT NULL AND 销售组 <> ''
    GROUP BY 销售组
) J ON J.销售组 = vs.store_dept_name
;
