# 完整落地步骤（按顺序做）

目标：你对智能体说  
`给我河南经销省区截至到昨日的销售简报`  
→ 它查数 → 填 JSON → 出 PNG → 在飞书里把图发给你。

下面按 **准备环境 → 挂提示词 → 做出图技能 → 串工作流 → 联调验收** 执行。  
平台以「飞书智能体 / 扣子工作流」为主；若你用的是自建 Bot，节点名不同但顺序一样。

---

## 总览（你最终会得到的链路）

```
① 用户发话
② 总控提示词：判断要不要出图，抽出 省区 / 日期 / 报告类型
③ 现有查数技能：拿到河南（或任意省区）文字/结构化结论
④ 填模提示词：结论 → 日销售简报 JSON
⑤ 出图技能：JSON → PNG（render_pillow 或 /render）
⑥ 发飞书图片消息
```

---

## 第 0 步：本机先确认渲染能跑（10 分钟）

在能跑 Python 的机器上（你的电脑、或一台小服务器）：

```bash
cd <本仓库根目录>
pip install -r briefing/requirements.txt

# 用辽宁示例验证出图
python3 briefing/render_pillow.py \
  --data briefing/data.example.json \
  --out /tmp/liaoning.png

# 看图：标题应是「辽宁省区经营简报」
```

可选：启动 HTTP 服务（给扣子「HTTP 请求」节点用）：

```bash
cd briefing
python3 server.py
# 默认 http://0.0.0.0:8787
```

本机测接口：

```bash
curl -X POST http://127.0.0.1:8787/render \
  -H 'Content-Type: application/json' \
  --data-binary @data.example.json \
  --output /tmp/from-api.png
```

> 若扣子云端要调你的服务，这台机器需要有**公网 HTTPS 地址**（或内网穿透）。  
> 没有公网时：把 `render_pillow.py` 做成扣子「代码节点 / 自定义插件」在云端跑也可以。

**本步完成标准：** 本地能稳定产出 PNG。

---

## 第 1 步：挂总控提示词（路由）

打开你的飞书/扣子智能体 → **人设与回复逻辑 / 系统提示词**。

1. 保留你原来的业务说明（查数口径、工具用法等），不要删。
2. 在开头或单独「路由」区块，**整段粘贴**仓库里的：

   - `briefing/AGENT_ORCHESTRATOR.md` 的正文

3. 再补一句你自己的工具名映射（改成真实名称），例如：

```text
你可用的工具：
- query_sales：按省区+日期查询销售结论（已有）
- render_daily_sales_briefing：传入日销售简报 JSON，返回 PNG（下一步会建）
```

4. 明确写死：

```text
用户提到「简报 / 晨报 / PNG / 一图」时：必须走 查数→填JSON→调用 render_daily_sales_briefing→发图。
只问数字、未要简报时：只查数，文字回答。
```

**本步完成标准：** 你问「河南昨天卖了多少」仍走文字；问「要销售简报」会尝试走出图分支（此时出图技能可能还没接好，属正常）。

---

## 第 2 步：简报分支——查询结果转 JSON

有两种配法，选一种即可。

### 做法 A（推荐，工作流更稳）：单独一个「填模」大模型节点

在工作流里，查数节点后面加一个 **大模型节点**：

| 配置项 | 怎么填 |
|--------|--------|
| 系统提示词 | 粘贴 `briefing/AGENT_PROMPT.md` 全文 |
| 用户输入 | 上游查数结论原文 + 一行：`region=河南经销省区；as_of_date=YYYY-MM-DD` |
| 输出 | 只要 JSON（可开 JSON 模式） |

把该节点输出变量命名为：`briefing_json`。

### 做法 B：仍由主智能体一次做完

在总控提示词里写：走出图时，先调用 `query_sales`，再按 `AGENT_PROMPT.md` 规则自己生成 JSON，再调用渲染技能。  
适合 Agent 模式；调试略难一点。

**本步完成标准：** 任意一次河南查询结论，能产出一份含  
`meta.region = "河南经销省区"`、`meta.title = "河南经销省区经营简报"` 的 JSON（数字与查询一致）。

可用辽宁 `data.example.json` 当格式对照；河南真实数据以你查询结果为准。

---

## 第 3 步：做出图技能（核心）

你要新增一个技能/插件，名称建议：`render_daily_sales_briefing`。

### 3.1 技能定义（给智能体看的）

- **名称：** `render_daily_sales_briefing`
- **描述：** 将日销售简报 JSON 渲染为 PNG 图片
- **入参：**
  - `data`（object，必填）：日销售简报 JSON  
  - 或直接把整个 JSON 作为 body
- **出参：** PNG 二进制 / 图片 URL / 飞书 `image_key`（看你怎么实现）

### 3.2 实现方式（三选一）

#### 方案 ① HTTP 插件（最常见）

1. 把 `briefing/server.py` 部署到可访问地址，例如：`https://your-host/render`
2. 在扣子/飞书里新建插件：
   - 方法：`POST`
   - URL：`https://your-host/render`
   - Header：`Content-Type: application/json`
   - Body：`{{briefing_json}}`  
     或：

```json
{
  "report_type": "daily_sales_briefing",
  "data": {{briefing_json}}
}
```

3. 响应类型选 **文件/图片**；若平台只能收 URL，就改服务端先存对象存储再返回 URL（可后续加）。

#### 方案 ② 代码节点（无公网时）

在扣子「代码节点」里调用 Pillow 逻辑（需平台支持安装 `pillow` 与写文件）。  
把 `render_pillow.py` 的 `render(data, out_path)` 拷进节点，入参 JSON，出参图片。

#### 方案 ③ 自建 Bot 开放接口

Bot 收到 JSON → 调 `render()` → 调飞书上传图片 API → 发消息。

飞书上传图片（示意）：

1. `POST https://open.feishu.cn/open-apis/im/v1/images`，拿到 `image_key`
2. 发消息：`msg_type = image`，`content = {"image_key":"..."}`

**本步完成标准：** 手动把 `data.example.json` POST 给技能，能返回一张可打开的 PNG。

---

## 第 4 步：把工作流串起来

在扣子/飞书工作流（或 Agent 工具编排）里按这个顺序连：

```
[开始]
  → [大模型：意图解析]
       输出：report_type, region, as_of_date, output_format
  → [条件分支]
       ├─ output_format != png 或 report_type == text_only
       │     → [现有查数] → [文字回复] → 结束
       └─ report_type == daily_sales_briefing 且要 png
             → [现有查数：传入 region + as_of_date]
             → [大模型填模：AGENT_PROMPT → briefing_json]
             → [技能 render_daily_sales_briefing]
             → [发送图片消息]（可附一句 headline）
             → 结束
```

意图解析节点可用很短的提示词，强制输出：

```json
{
  "report_type": "daily_sales_briefing",
  "region": "河南经销省区",
  "as_of_date": "2026-07-27",
  "output_format": "png"
}
```

「昨日」在这里换算成具体日期（用系统当天减 1 天）。

**本步完成标准：** 工作流能从头跑到「发图片」节点，中间变量能在调试面板里看到。

---

## 第 5 步：飞书侧发图（若技能只返回 PNG 文件）

若渲染技能返回的是图片文件/二进制，还要保证会话能发出去：

1. 使用平台自带的「发送图片」节点；或  
2. 用飞书开放能力：上传图片 → `image_key` → 发 IM 消息。

建议最终用户看到的是：

- 一张 PNG 简报（主内容）
- 可选一行字：`河南经销省区经营简报（截至 2026-07-27）已生成`

**不要**再把整篇长文结论贴一遍（除非用户额外要文字版）。

---

## 第 6 步：联调验收（就测这一句）

对智能体发送：

```text
给我河南经销省区截至到昨日的销售简报
```

按清单打勾：

| # | 检查项 | 通过标准 |
|---|--------|----------|
| 1 | 路由 | 走进了简报/出图分支，而不是纯文字长文 |
| 2 | 省区 | 查询参数是河南经销省区（不是辽宁） |
| 3 | 日期 | `as_of_date` = 昨天 |
| 4 | JSON | `meta.title` = `河南经销省区经营简报`，`meta.region` = `河南经销省区` |
| 5 | 数字 | KPI/排名/订单与查数原文一致，无编造 |
| 6 | 出图 | 收到 PNG；图上标题为河南 |
| 7 | 对照 | 再测一句「辽宁…销售简报」，标题与数据应换成辽宁 |

再测一句负例（确认不误伤）：

```text
河南经销省区昨天销售额是多少？
```

应只回文字，不出 PNG。

---

## 第 7 步：出问题怎么查

| 现象 | 优先查 |
|------|--------|
| 一直回长文、不出图 | 总控提示词是否要求「简报必须调渲染技能」；技能是否已发布并授权给智能体 |
| 图是辽宁的 | JSON 的 `meta.region/title` 是否仍写死辽宁；查数是否传错省区 |
| 数字是错的/假的 | 填模节点是否允许编造；应改为「只能用查询原文」 |
| HTTP 出图失败 | 服务是否公网可达、HTTPS、Body 是否为合法 JSON |
| 飞书收不到图 | 是否完成「上传图片 → image_key → 发消息」；机器人是否有发图权限 |
| 其他报告也被出图 | 路由条件是否过宽；仅「简报/晨报/PNG/一图」触发 |

---

## 你的执行顺序（一张清单）

- [ ] 0. 本机 `render_pillow.py` 跑通辽宁示例
- [ ] 1. 总提示词挂上 `AGENT_ORCHESTRATOR.md`
- [ ] 2. 查数后增加填模（`AGENT_PROMPT.md`）→ 得到 `briefing_json`
- [ ] 3. 部署/注册 `render_daily_sales_briefing` 技能（HTTP 或代码节点）
- [ ] 4. 工作流按「路由 → 查数 → 填模 → 渲染 → 发图」连接
- [ ] 5. 飞书发图通路打通
- [ ] 6. 用河南那句话验收；再用辽宁对照；再用纯问数负例

全部勾完，这条完整链路就落地了。其他报告类型先继续文字；要出图时复制第 2～3 步换一套 schema/模板即可。
