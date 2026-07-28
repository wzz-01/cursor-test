# ⑥拜访底表：子查询优化（保持原稿形式）

相对你原稿只动两处：

1. **内层子查询 `vs`**：把门店 JOIN + `c_code` CASE 收进去，外层用 `vs.c_code` 关联 `c` / `dim_cust`（不再复制三遍 CASE）
2. **子查询 `J`**：`DISTINCT 大区,省区,销售组` 改为 `GROUP BY 销售组` + `MAX(大区/省区)`，避免同组多省区撑行

其余：字段别名、过滤条件、`DATE(visit_date)`、`LEFT JOIN` 顺序、注释风格均按你原写法。

完整 SQL：`07_visit_base_etl.sql`
