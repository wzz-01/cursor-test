# 销售管理日简报 - 每日基础表方案

面向《销售管理日简报》一页纸 PDF：先落每日固定基础数据，再由智能体/脚本读表填模板。

## 表清单

| 表名 | 粒度 | 用途 |
|------|------|------|
| `market_db.ads_sales_daily_brief` | 统计日 + 省区 | 主宽表，正文大部分指标 |
| `market_db.ads_sales_daily_brief_visit_person` | 日 + 省区 + 人 | 拜访个人明细表 |
| `market_db.ads_sales_daily_brief_order_customer` | 日 + 省区 + 客户 | 昨日下单客户清单 |
| `market_db.ads_sales_daily_brief_no_order_customer` | 日 + 省区 + 客户 | 当月未下单客户 |

## 文件

- `省区销售管理日简报_智能体训练说明.md`：**给新智能体的精简训练说明（推荐）**
- `01_ads_sales_daily_brief.sql`：主宽表 DDL
- `02_detail_tables.sql`：三张明细表 DDL
- `03_field_dictionary.md`：字段字典与口径待确认项
- `04_agent_prompt_read_table.md`：宽表就绪后给智能体的取数出 PDF 指令
- `05_new_agent_brief.md`：历史详细版说明书（含纠偏过程，可作归档）

## 推荐落地顺序

1. 信息部按 DDL 建表（复制数 `replication_num` 按集群实际改）
2. 用智能体阶段 2/3 把源表字段映射补进字典
3. 先只灌主宽表核心字段（销售进度 + 订单 + 年度），能出第一版 PDF
4. 再补拜访 / 预警 / 费用
5. 调度：每天早上跑 T+1，写完后把 `data_ready_flag=1`
6. 智能体每天只读宽表生成 PDF

## 取数示例

```sql
SELECT *
FROM market_db.ads_sales_daily_brief
WHERE stat_date = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
  AND region_name = 'XX省区'
  AND data_ready_flag = 1;
```

## 待业务确认（建 ETL 前必须定）

1. 销售额主口径：经销商发货 / 到店订单 / 其他
2. 「销售额」是昨日当日，还是截至昨日的月累计（样例句式偏「截至X月X日实现销售额」）
3. 达成率分母：月目标还是年目标滚动
4. 增长率：同比去年同日，还是月累计同比
5. 大单品如何圈定
6. 有效拜访定义
7. 连续 3 个月下滑用哪个月度指标
