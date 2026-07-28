# 飞书智能体：文字结论 → PNG 经营简报

目标：智能体继续产出你现在的文字结论，但**最终发给用户的是一张 PNG 简报**（类似销售经营晨报），数字必须准确，不能靠文生图“画”出来。

## 推荐链路（最稳）

```
原始数据/SQL结论
    ↓
智能体整理成「简报 JSON」（固定字段）
    ↓
调用出图服务 / 代码节点（HTML 模板截图）
    ↓
上传飞书图片 → 发送 PNG
```

本仓库已提供：

| 文件 | 作用 |
|------|------|
| `briefing/data.example.json` | 用你给的辽宁结论填好的示例数据 |
| `briefing/template.html` | 晨报风格版式模板 |
| `briefing/render_pillow.py` | JSON → PNG（推荐，Pillow 直绘，数字不变形） |
| `briefing/render.py` | JSON → HTML → Chrome 截图（可选） |
| `briefing/template.html` | HTML 版式（Chrome 方案用） |
| `briefing/AGENT_PROMPT.md` | 可直接贴进智能体的提示词 |

本地试跑：

```bash
python3 briefing/render_pillow.py \
  --data briefing/data.example.json \
  --out briefing/output/liaoning-2026-07-27.png
```

## 扣子 / 飞书智能体怎么接

### 1. 改智能体提示词

要求模型**只输出 JSON**（或先输出 JSON，再由工作流取用），字段对齐 `data.example.json`。  
完整提示词见 `AGENT_PROMPT.md`。

### 2. 增加「出图」节点

任选其一：

**A. 代码节点（推荐）**  
把 `render_pillow.py` 部署成小服务 / 工作流代码节点：

```bash
python3 render_pillow.py --data /tmp/input.json --out /tmp/out.png
```

**B. HTTP 请求节点**  
`POST /render-briefing`，body 为简报 JSON，返回 PNG 二进制或可访问 URL。

**C. 不要用**  
纯「图像生成 / 即梦 / 文生图」节点写 KPI——百分比和排名很容易画错。

### 3. 发到飞书

1. 调用开放接口上传图片，拿到 `image_key`
2. 消息类型选 `image`，或把图嵌进消息卡片
3. 可选：同时附一段极短文字摘要（1～2 句），方便检索

## 你的四段结论如何映射到版式

| 原文段落 | 简报区块 |
|----------|----------|
| ① 销售额/达成/排名/分区高低 | 顶部 4 个 KPI + `01 销售组达成对比` |
| ② 连续三月下滑城市/组/客户、后20% | `02 连续三月同比下滑` + 预警 |
| ③ 年累计进度/排名 | `03 年累计进度` |
| ④ 昨日订单与客户明细 | `04 昨日订单` + 今日动作 |

缺数值的销售组（仅有「后20%」描述）在图里显示为 `—`，并用备注标明，避免假数字。

## 最小改造清单

1. 智能体输出改为严格 JSON（可用本仓库示例字段）
2. 工作流增加「渲染 PNG」一步
3. 提示词末尾加：`最终必须发送 PNG 简报，不要只发长文`
4. 固定每日同一模板，只替换 JSON，保证风格稳定
