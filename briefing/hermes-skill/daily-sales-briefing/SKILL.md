---
name: daily-sales-briefing
description: 把省区日销售查询结论渲染成经营晨报 PNG（支持辽宁/河南等任意省区）
version: 1.1.0
author: cursor-test
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [Sales, Briefing, PNG, Feishu]
---

# 省区日销售简报 PNG

当用户要「销售简报 / 经营晨报 / PNG / 一图」时使用本 skill。  
普通问数（只要文字结论）不要使用本 skill。

## When to Use

- 给我河南经销省区截至到昨日的销售简报
- 输出辽宁省区日销售简报 PNG
- 按晨报模板出一张某某省区销售简报

不要用于：只问销售额/排名、不要图片的普通查询。

## Procedure

1. **解析**：`region`、`as_of_date`、`report_type=daily_sales_briefing`
2. **查数**：按省区+日期取结论（口径不变）
3. **填 JSON**：禁止编造；缺值用 `""` / `null` / `[]`
4. **出图**：

```bash
python "${HERMES_SKILL_DIR}/scripts/render_pillow.py" --data <json> --out <png>
```

5. **发送**：主体必须是 PNG；必要时加 `[[as_document]]`

## 输出规格

- 固定 **793×1983**（手机竖版一张图看全）
- 页脚固定：左 `数据源：CRM | SFA | 终端巡检系统 | 市场活动平台`，右 `制作部门：数据组`（无【】）

## JSON 结构（模板模块）

| 模块 | 字段 |
|------|------|
| 顶栏 | `meta.*` / `focus` |
| 01 业绩追踪 | `performance.overall` / `performance.base`（预算/销额/达成/订单进度/增长） |
| 01 销售组表 | `section_groups.rows`（兼容旧 `section_01`） |
| 01 后10客户 | `section_bottom10.rows`（name/budget/actual/forecast/order_progress） |
| 02 拜访执行 | `section_visit.metrics[6]` + `section_visit.alert` |
| 03 推广执行 | `section_promo.metrics[6]` + `trend_7d` + `structure` |
| 04 经营预警 | `section_warn.blocks`（A/B/C） |

兼容：若无新字段，渲染器会尽量从旧 `section_02`/`section_04`/`warnings` 回退拼装预警块。

`performance` 示例：

```json
"performance": {
  "overall": {"budget": "582万", "sales": "587万", "achieve_rate": "100.8%", "order_progress": "", "growth_rate": "+20.9%"},
  "base": {"budget": "450万", "sales": "481万", "achieve_rate": "106.8%", "order_progress": "", "growth_rate": "+20.3%"}
}
```

## Pitfalls

- 不要用文生图模型手写 KPI 数字
- 无数据必须留空，不要填假数
- Windows 优先用 `python`，不要用坏掉的 `py -3`
