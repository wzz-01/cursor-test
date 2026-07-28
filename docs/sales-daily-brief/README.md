# 销售管理日简报 - 每日基础表方案

面向《销售管理日简报》：先文字结论（①～⑥），宽表/PDF 为后续可选。

## 当前结论模块

| 编号 | 模块 | 数据源 | 状态 |
|------|------|--------|------|
| ① | 区域销售进度（当月） | `dwd_sales_fiveyears` | 已锁定 |
| ② | 业绩预警（近3月） | `dwd_sales_fiveyears` | 已锁定 |
| ③ | 年度目标 | `dwd_sales_fiveyears` | 已锁定 |
| ④ | 昨日订单 | `dwd_sales_daily_detail` | 已锁定 |
| ⑤ | 费用使用情况 | 待探表（见 `06_…`） | 对接中 |
| ⑥ | 昨日拜访情况 | 源 `dwd_sales_hds_visit_detail` → 底表制作中 | 对接中 |

## 表清单（中间层，可选）

| 表名 | 粒度 | 用途 |
|------|------|------|
| `market_db.ads_sales_daily_brief` | 统计日 + 省区 | 主宽表，正文大部分指标 |
| `market_db.ads_sales_daily_brief_visit_person` | 日 + 省区 + 人 | 拜访个人明细表 |
| `market_db.ads_sales_daily_brief_order_customer` | 日 + 省区 + 客户 | 昨日下单客户清单 |
| `market_db.ads_sales_daily_brief_no_order_customer` | 日 + 省区 + 客户 | 当月未下单客户 |

## 文件

- `省区销售管理日简报_智能体训练说明.md`：**给智能体的主训练说明（推荐）**，含①～⑥
- `06_hermes_探表_费用拜访.md`：**对接⑤⑥ 新数据源**——探表话术 + 锁定口径话术
- `07_visit_base_etl.sql` / `07_visit_base_optimize.md`：**⑥拜访底表**优化 ETL 与说明
- `01_ads_sales_daily_brief.sql`：主宽表 DDL
- `02_detail_tables.sql`：三张明细表 DDL
- `03_field_dictionary.md`：字段字典与口径待确认项
- `04_agent_prompt_read_table.md`：宽表就绪后给智能体的取数出 PDF 指令
- `05_new_agent_brief.md`：历史详细版说明书（含纠偏过程，可作归档）

## 推荐落地顺序

1. 用主训练说明稳定产出①②③④（直连 Doris `market`）
2. 按 `06_hermes_探表_费用拜访.md` 探表，锁定费用/拜访源表后产出⑤⑥
3. （可选）信息部按 DDL 建宽表，把已锁定口径灌进 ADS
4. （可选）再出 PDF；当前默认只要文字结论

## 取数示例

```sql
SELECT *
FROM market_db.ads_sales_daily_brief
WHERE stat_date = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND region_name = 'XX省区'
  AND data_ready_flag = 1;
```

## 待业务确认（⑤⑥ 探表前/后）

1. 费用使用额：当月累计 vs 昨日当日  
2. 有效拜访定义  
3. 覆盖率分母（应拜访客户/门店）来源  
4. 负责人识别字段  
5. （历史项，①已定）大单品清单、连续3月下滑同比口径等 — 见主训练说明
