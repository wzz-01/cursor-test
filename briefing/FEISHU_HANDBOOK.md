# 飞书智能体用户操作手册（从你现在的文字结论开始）

你现在的情况：智能体已经能查出类似下面的文字结论（①～⑤）。  
你要的结果：对它说「给我某某省区销售简报」时，**发一张 PNG 图**，而不是一大段字。

---

## 先记住一句话

> 飞书智能体本身不会跑 Python 画图。  
> 所以你要准备两样东西：  
> 1）提示词：让它把①～⑤整理成固定 JSON  
> 2）出图技能：把 JSON 交给外面的出图服务，换回 PNG，再发到飞书

本地第 0 步（跑 `render_pillow.py`）只是验证出图代码能用，**可以后做**；真正接到飞书，关键是下面 A → B → C。

---

## A. 准备出图服务（做一次）

找一台能长期开机、有公网访问的电脑/云服务器（或让 IT 帮忙）。

### A1. 把本仓库代码放到那台机器

```bash
git clone https://github.com/wzz-01/cursor-test.git
cd cursor-test
git checkout cursor/liaoning-briefing-png-c78d
pip install -r briefing/requirements.txt
```

### A2. 启动出图接口

```bash
cd briefing
python server.py
```

默认地址：`http://服务器IP:8787/render`

### A3. 用浏览器或 Postman 测一下

`POST` 到 `/render`，Body 用 `data.example.json` 的内容。  
能返回一张图片 = 出图服务 OK。

> 若暂时没有公网服务器：先完成本机出图验证，同时找 IT 部署；  
> 飞书云端智能体**调不到你家里的 localhost**。

把最终地址记下来，例如：

`https://xxx.yourcompany.com/render`

---

## B. 改智能体提示词（在飞书里做）

打开你的飞书智能体 → **人设与回复逻辑 / 提示词**。

### B1. 保留你原来的查数规则

（财年不足 3 个月怎么算、后 20% 怎么算等，都不要删。）

### B2. 在提示词末尾追加下面整段

```text
【简报出图规则】
当用户要求「简报 / 晨报 / PNG / 一图 / 销售简报」时，按下面流程：
1. 先按现有口径查询，得到①～⑤文字结论（可含门店拜访等扩展段）
2. 把结论整理成「日销售简报 JSON」（字段见下方），禁止编造数字
3. 调用技能 render_daily_sales_briefing，传入完整 JSON
4. 把返回的 PNG 发给用户；不要只发长文

当用户只是问数字、没提简报/图片时：只返回文字结论，不调用出图技能。

省区：用户说河南/辽宁等，查询与 JSON 的 meta.region、meta.title 必须对应该省区。
日期：「昨日」「截至昨日」换成具体 YYYY-MM-DD。

日销售简报 JSON 必须包含：
meta（title/subtitle/region/as_of_date/generated_at/owner）、
headline、kpis（4个）、section_01、section_02、section_03、section_04、
warnings、actions、footer。

映射关系：
① → kpis + section_01（销售组高低）
② → section_02（下滑城市/组/客户/后20%）
③ → section_03（年累计进度）
④ → section_04（昨日订单）
⑤ → 写入 warnings 或 footer.note（当前模板暂无独立门店区块，先文字进预警/备注）
```

更完整的字段样例可打开仓库 `briefing/AGENT_PROMPT.md` / `data.example.json` 对照粘贴。

---

## C. 在飞书/扣子里加「出图技能」

### C1. 新建技能/插件

- 名称：`render_daily_sales_briefing`
- 类型：HTTP 请求 / 自定义插件
- 方法：`POST`
- URL：你在 A3 记下的地址，例如 `https://xxx.yourcompany.com/render`
- Header：`Content-Type: application/json`
- 请求体：智能体生成的整份简报 JSON  
  （或 `{ "report_type":"daily_sales_briefing", "data": { ... } }`）

### C2. 把技能授权给智能体

在智能体「技能 / 工具」里勾选启用 `render_daily_sales_briefing`。

### C3. 若你用的是工作流模式

节点顺序固定为：

```
用户输入
 → 查数（你现有的）
 → 大模型整理 JSON（可用 AGENT_PROMPT.md）
 → HTTP 调用 /render
 → 发送图片消息
```

---

## D. 怎么验收（就测这两句）

### 测简报（应出图）

```text
给我辽宁省区截至到昨日的销售简报
```

或：

```text
给我河南经销省区截至到昨日的销售简报
```

通过标准：

1. 先查数（内容类似你现在的①～⑤）
2. 最终你收到一张 PNG
3. 图标题是对应省区（辽宁/河南）
4. 图上 310万、65.9%、排名等与文字结论一致

### 测普通问答（不应出图）

```text
辽宁省区截至7月27日销售额是多少？
```

应只回文字，不强制出 PNG。

---

## 和你现在这段结论怎么对应到图上

你贴的这段，进图时大致是：

| 你的文字 | 图上位置 |
|----------|----------|
| ① 310万、达成65.9%、排名、大连/沈阳 | 顶部 KPI + 01 条形对比 |
| ② 下滑城市/组/客户、后20%组 | 02 区块 + 经营预警 |
| ③ 年累计进度 2.5% vs 3.0% | 03 年累计 |
| ④ 昨日订单 17920元、两家客户 | 04 昨日订单 |
| ⑤ 拜访覆盖率 1.6% | 暂放预警或页脚（模板以后可加第 05 区块） |

注意：你最新结论里昨日下单额是 **17920元**（不是早期的约 2 万元口径展示问题），填 JSON 时以智能体当次查询为准。

---

## 你现在立刻可以做的顺序（打勾）

1. [ ] 有没有一台能部署 `briefing/server.py` 的机器/同事？没有就先找 IT。  
2. [ ] 部署并测通 `POST /render` 能出图。  
3. [ ] 飞书智能体提示词追加「简报出图规则」。  
4. [ ] 新建并启用 HTTP 技能 `render_daily_sales_briefing`。  
5. [ ] 对智能体说：「给我辽宁省区截至到昨日的销售简报」。  
6. [ ] 核对 PNG 标题和数字。

---

## 如果你卡在某一环

| 你卡在 | 说明 |
|--------|------|
| 不会部署服务器 | 这是目前唯一硬门槛；飞书里无法直接跑本仓库 Python。把本手册 A 节给 IT。 |
| 技能调不通 | 检查 URL 是否公网 HTTPS、Body 是否完整 JSON、技能是否已发布。 |
| 还是只回文字 | 提示词是否写了「必须调用出图技能」；技能是否已挂到该智能体。 |
| 数字不对 | 填 JSON 时禁止模型估算；必须原样用①～⑤里的数。 |
