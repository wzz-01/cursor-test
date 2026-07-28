# ⑥拜访底表优化说明

源 SQL 基于 `hive.dw.dwd_sales_hds_visit_detail`。完整可跑脚本见 `07_visit_base_etl.sql`。

## 建议改什么

| 问题 | 风险 | 改法 |
|------|------|------|
| `c_code` 的 CASE 在 SELECT + 两个 JOIN ON 里写了 3 遍 | 难维护、易改漏、重复计算 | CTE `visit_store` 只算一次，后面一律 `v.c_code` |
| `LEFT JOIN md` 后在 WHERE 写 `md.store_cooperate_status=1` 等 | 实质变 INNER，且误导读 SQL 的人 | 改成 `INNER JOIN`，过滤放在 `ON`/`WHERE` 意图一致处 |
| `DATE(vs.visit_date) >= …` | 可能无法分区裁剪，全表扫 | `visit_date >= d AND visit_date < d+1`（全量用 `>= '2024-07-01'`） |
| `J = DISTINCT 大区,省区,销售组` 再按销售组关联 | 同一销售组多省区时**行数放大** | `GROUP BY 销售组` 压成 1 行（或业务指定主省区规则） |
| 每次出结论都跨 `jdbc_sqlserve` | 慢、不稳定 | **先物化底表**，智能体只读 `market_db.dwd_sales_visit_detail` |
| 缺「是否负责人」 | ⑥样句「负责人拜访数量」不好算 | 底表加 `is_leader`（岗位关键字可后再改） |

## 建议落表字段（给智能体）

智能体算⑥时优先用这些，不要回源表重算 JOIN：

- 过滤：`c_shengqu = 省区` 且 `riqi = 昨天`（月累计覆盖用当月 `riqi`）
- 客户数：`COUNT(DISTINCT c_code)`（经销客户；若业务要门店客户另说）
- 门店数：`COUNT(DISTINCT mendian_code)`
- 人数：`COUNT(DISTINCT ry_code)`
- 明细：`ry_name | COUNT(DISTINCT c_code) | COUNT(DISTINCT mendian_code)` 按人聚合
- 负责人：`is_leader=1` 再按销售组汇总

覆盖率分母（应拜访客户/门店）**本底表没有**，需另表或暂标「暂无法计算」。

## 仍建议你确认的 3 点

1. **客户数用 `c_code` 还是 `mendian_code`？** 样句「拜访客户」更像经销客户 `c_code`；「拜访门店」用 `mendian_code`。
2. **`is_leader` 岗位规则**是否用「负责/主管/经理」关键字，还是人事表有正式字段。
3. **同销售组多省区**时，兜底维 `MAX(省区)` 是否可接受；不可则改指定规则。
