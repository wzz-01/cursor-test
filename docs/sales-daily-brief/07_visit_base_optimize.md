# ⑥拜访底表优化说明

源 SQL 基于 `hive.dw.dwd_sales_hds_visit_detail`。完整脚本见 `07_visit_base_etl.sql`（**保持原稿子查询写法**）。

## 相对原稿改了什么

| 问题 | 改法（子查询形式） |
|------|-------------------|
| `c_code` CASE 写 3 遍 | 内层子查询 `vs` 算一次，外层 `vs.c_code` 关联 `c` / `dim_cust` |
| `J = DISTINCT 大区,省区,销售组` 易撑行 | 子查询 `J` 改为 `GROUP BY 销售组` + `MAX(大区/省区)` |
| 其余过滤、字段别名、LEFT JOIN 顺序 | **保持你原形式** |

## 建议落表字段（给智能体）

智能体算⑥时优先用这些，不要回源表重算 JOIN：

- 过滤：`c_shengqu = 省区` 且 `riqi = 昨天`（月累计覆盖用当月 `riqi`）
- 客户数：`COUNT(DISTINCT c_code)`（经销客户；若业务要门店客户另说）
- 门店数：`COUNT(DISTINCT mendian_code)`
- 人数：`COUNT(DISTINCT ry_code)`
- 明细：`ry_name | COUNT(DISTINCT c_code) | COUNT(DISTINCT mendian_code)` 按人聚合
- 负责人：底表暂无 `is_leader`，后续用 `ry_position_new` 规则另加

覆盖率分母（应拜访客户/门店）**本底表没有**，需另表或暂标「暂无法计算」。

## 仍建议你确认的 2 点

1. **客户数用 `c_code` 还是 `mendian_code`？** 样句「拜访客户」更像经销客户 `c_code`；「拜访门店」用 `mendian_code`。
2. **同销售组多省区**时，兜底维 `MAX(省区)` 是否可接受；不可则改指定规则。
