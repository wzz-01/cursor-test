# 飞书智能体：多省区日销售简报 → PNG

智能体继续负责查数；要简报时，把任意省区的结论填进**同一模板**再出 PNG。

详细架构见：[`MULTI_REGION.md`](MULTI_REGION.md)

## 推荐链路

```
用户：给我河南经销省区截至到昨日的销售简报
    ↓
意图解析：report_type + region + as_of_date
    ↓
现有查询能力（河南 / 辽宁 / …）
    ↓
填模：日销售简报 JSON（不绑死某一省）
    ↓
render_pillow / HTTP /render → PNG
    ↓
飞书发图
```

## 文件

| 文件 | 作用 |
|------|------|
| `MULTI_REGION.md` | 多省区 × 多报告接入说明（先看这个） |
| `AGENT_ORCHESTRATOR.md` | 总控提示词 |
| `AGENT_PROMPT.md` | 查询结论 → 日销售 JSON |
| `schema.daily_sales.json` | 字段定义 |
| `data.example.json` | 辽宁真实示例 |
| `data.henan.example.json` | 河南占位示例（演示换省区） |
| `render_pillow.py` | JSON → PNG |
| `server.py` | 可选 HTTP 出图服务 |
| `template.html` / `render.py` | Chrome 截图备选 |

## 本地试跑

```bash
# 辽宁示例
python3 briefing/render_pillow.py \
  --data briefing/data.example.json \
  --out briefing/output/liaoning.png

# 河南占位（上线前换成真实查询 JSON）
python3 briefing/render_pillow.py \
  --data briefing/data.henan.example.json \
  --out briefing/output/henan.png
```

可选服务：

```bash
pip install flask pillow
python3 briefing/server.py
# POST http://host:8787/render
```

## 你要改智能体的最少三步

1. 加上总控提示词：识别「简报」意图，并抽出省区、日期  
2. 简报分支：查数 → 填 JSON → 调渲染  
3. 普通问答分支：保持你现在的文字查数逻辑不变

其他报告类型先文字输出；要出图时再加新 `report_type` + 新模板，日销售链路不用重做。
