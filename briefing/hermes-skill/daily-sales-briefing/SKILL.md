---
name: daily-sales-briefing
description: 把省区日销售查询结论渲染成经营晨报 PNG（支持辽宁/河南等任意省区）
version: 1.0.0
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

按顺序执行：

1. **解析**：`region`（标准省区名）、`as_of_date`（昨日→具体 YYYY-MM-DD）、`report_type=daily_sales_briefing`
2. **查数**：用你现有的销售查询能力，按该省区+日期取①～⑤类结论（口径不变）
3. **填 JSON**：把结论填进日销售简报结构（见下方）。禁止编造数字；缺值用 `null` 或 `[]`
4. **出图**：把 JSON 写入临时文件，运行渲染脚本。

Windows 优先用 `python`（不要用可能指向坏掉安装的 `py -3`）：

```bash
python "${HERMES_SKILL_DIR}/scripts/render_pillow.py" --data <json路径> --out <输出png路径>
```

Linux/macOS：

```bash
python3 "${HERMES_SKILL_DIR}/scripts/render_pillow.py" --data <json路径> --out <输出png路径>
```

若缺少 Pillow：Windows（Python 3.8）用  
`python -m pip install "pillow>=10.0.0,<11"`；  
更高版本 Python 可用  
`python -m pip install -r "${HERMES_SKILL_DIR}/scripts/requirements.txt"`。

脚本会自动使用 Windows 自带中文字体（微软雅黑/黑体）。若仍乱码，检查是否存在 `C:\Windows\Fonts\msyh.ttc`。

5. **发送**：把生成的 PNG 发给用户（飞书/当前会话）。可附一句摘要，但主体必须是图片。  
   若平台对高清图有压缩，在回复末尾加：`[[as_document]]`

## JSON 必填字段

对照 `${HERMES_SKILL_DIR}/scripts/data.example.json` 与 `schema.daily_sales.json`。

最少包含：

- `meta.brand_title`：顶栏大标题，默认 `销售经营晨报`
- `meta.scope`：副标题左侧，默认 `省区经营管理`
- `meta.region` / `meta.title`：省区名（如河南经销省区）
- `meta.as_of_date` / `meta.generated_at` / `meta.data_cutoff` / `meta.report_time`：日期与时点
- `headline`
- `kpis`（4 个）
- `section_01` 销售组达成对比
- `section_02` 连续三月同比下滑
- `section_03` 年累计进度
- `section_04` 昨日订单
- `warnings` / `actions` / `footer`

文字结论映射：

| 原文 | JSON |
|------|------|
| ① 销售额/达成/排名/分区高低 | `kpis` + `section_01` |
| ② 下滑城市/组/客户、后20% | `section_02` + `warnings` |
| ③ 年累计进度 | `section_03` |
| ④ 昨日订单 | `section_04` |
| ⑤ 门店拜访等扩展 | 暂写入 `warnings` 或 `footer.note` |

## Pitfalls

- 不要用文生图模型手写 KPI 数字
- 不要把辽宁数据套到河南；只共用版式
- 查询失败时不要出假数据 PNG，先文字说明
- Windows 中文路径注意用引号包住文件路径

## Verification

- PNG 文件存在且可打开
- 图标题省区与用户要求一致
- 关键数字与查询结论一致
