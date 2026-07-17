# 宽表就绪后：给智能体的取数出 PDF 指令

> 等 `ads_sales_daily_brief` 每日有数且 `data_ready_flag=1` 后使用。

```text
【任务】生成《XX省区销售管理日简报》一页 PDF 发给我。

【取数规则】
1. 只读以下表，禁止改写，禁止从 ODS 临时重算（除非宽表缺字段且我明确允许）：
   - market_db.ads_sales_daily_brief
   - market_db.ads_sales_daily_brief_visit_person
   - market_db.ads_sales_daily_brief_order_customer
   - market_db.ads_sales_daily_brief_no_order_customer
2. 条件：
   - stat_date = 昨天
   - region_name = 【填写省区名】
   - data_ready_flag = 1
3. 若查不到就绪数据：停止并告诉我，不要编造。

【版式】
严格按样例《销售管理日简报》模块顺序与句式填充：
区域销售进度 → 昨日订单 → 费用 → 昨日拜访（含个人表）→ 预警 → 年度目标 → 页脚。
费用字段为空时写「本版暂无费用数据」。

【交付】
文件名：销售日报_YYYY-MM-DD.pdf
一页纸，发给我。
先输出将要填入的关键数字预览，我确认后再生成 PDF。
```
