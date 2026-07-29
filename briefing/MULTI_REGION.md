# 多省区 × 多报告：飞书智能体怎么接 PNG 简报

你的智能体已经会查数。接下来不要为「辽宁 / 河南」各做一套，而是做成：

```
用户一句话
  → 识别：报告类型 + 省区 + 截止日期
  → 调用现有查询能力拿原始结论
  → 映射成「对应模板」的 JSON
  → 渲染 PNG
  → 发回飞书
```

例如：

> 给我河南经销省区截至到昨日的销售简报

应解析为：

| 字段 | 值 |
|------|------|
| `report_type` | `daily_sales_briefing`（日销售简报） |
| `region` | `河南经销省区` |
| `as_of_date` | 昨天（按系统日期推算） |
| `output` | `png` |

辽宁、河南、其他省区**共用同一张日销售模板**，只换 JSON 里的 `meta.region` 和查询结果。

---

## 一、智能体内部怎么拆（推荐）

把能力拆成 4 段，而不是写死在一个超长提示词里：

### 1）意图路由（总控）

识别用户要什么。输出一个小 JSON 即可：

```json
{
  "intent": "render_report",
  "report_type": "daily_sales_briefing",
  "region": "河南经销省区",
  "as_of_date": "2026-07-27",
  "output_format": "png"
}
```

若用户只是问「河南昨天卖了多少」，可不走出图，直接文字回答。  
只有明确要「简报 / 晨报 / PNG / 一图」时，才走渲染。

常见 `report_type` 可先定这几类（后续可加）：

| report_type | 说明 | 模板 |
|-------------|------|------|
| `daily_sales_briefing` | 省区日销售简报 | 本仓库现有晨报模板 |
| `weekly_sales_briefing` | 周报（以后做） | 另建模板 |
| `order_alert` | 未下单预警（以后做） | 另建模板 |
| `text_only` | 普通问答 | 不出图 |

### 2）数据查询（你已有）

把路由结果传给现有查数工具 / SQL / 知识库，得到和现在一样的文字结论或结构化结果。  
**这一步不要改口径**，继续用你验证过的查询。

### 3）结构化填模（新增）

把查询结果填进固定 schema（见 `schema.daily_sales.json` / `AGENT_PROMPT.md`）。  
注意：

- `meta.title` = `{region}经营简报`
- `meta.region` = 用户要的省区名（河南经销省区 / 辽宁省区 …）
- 缺字段就留空数组或 `null`，禁止编造

### 4）出图发送（新增）

调用渲染服务：

```bash
python3 briefing/render_pillow.py --data /tmp/briefing.json --out /tmp/out.png
```

或 HTTP：

```http
POST /render
Content-Type: application/json

{ "report_type": "daily_sales_briefing", "data": { ...简报JSON... } }
```

返回 PNG → 上传飞书 → 发图片。

---

## 二、在扣子 / 飞书里怎么配节点

建议工作流：

```
开始
 └─ 大模型：意图解析（region / date / report_type）
      └─ 条件分支
           ├─ text_only → 走原有问答
           ├─ daily_sales_briefing
           │     ├─ 查询节点（复用现有查数）
           │     ├─ 大模型：结论 → 简报 JSON（用 AGENT_PROMPT）
           │     ├─ 代码/HTTP：render_pillow 出 PNG
           │     └─ 发图片消息
           └─ 其他报告类型 → 对应模板（同样三步：查→填→渲）
```

关键点：

1. **查询与出图分离**：查询仍用老逻辑；出图只吃 JSON。  
2. **模板按 report_type 选**，不要按省区选。  
3. **最终回复以 PNG 为主**，文字最多附 1 句摘要。

---

## 三、你怎么跟智能体说话（用法约定）

把这些说法教给用户 / 写进提示词示例：

- `给我河南经销省区截至到昨日的销售简报`
- `输出辽宁省区日销售简报 PNG，数据截至昨天`
- `按晨报模板出一张山东经销省区销售简报`

智能体应自动：

1. 解析省区名（与你主数据里的省区名称对齐，建议做别名表）  
2. 「昨日」→ 换成具体日期  
3. 查数 → 填模 → 出 PNG

省区别名表示例（放进提示词或配置表）：

| 用户说法 | 标准 region |
|----------|-------------|
| 河南 / 河南省区 / 河南经销 | 河南经销省区 |
| 辽宁 / 辽宁省区 | 辽宁省区 |
| 辽 | 辽宁省区 |

---

## 四、兼顾其他报告时怎么扩展

以后加「周报」「未下单预警」时，只加三样东西：

1. 新 schema（如 `schema.weekly_sales.json`）  
2. 新渲染模板 / 函数（或同一渲染器按 `report_type` 分支）  
3. 路由表里登记新的 `report_type`

日销售简报链路不用动。河南、辽宁继续共用 `daily_sales_briefing`。

---

## 五、最小落地清单（按这个做就行）

1. 保留现有查数能力，不要重写。  
2. 在智能体里加「意图解析」：抽出 `report_type / region / as_of_date`。  
3. 当 `report_type=daily_sales_briefing` 时：查数 → 用 `AGENT_PROMPT.md` 转 JSON → 调 `render_pillow.py`。  
4. 配置飞书发图。  
5. 用河南、辽宁各测一句：确认省区名进了标题，数字与查询一致。  
6. 其他报告类型先继续文字输出；需要出图时再加模板。

---

## 六、本仓库对应文件

| 文件 | 用途 |
|------|------|
| `AGENT_ORCHESTRATOR.md` | 总控提示词（多报告 / 多省区） |
| `AGENT_PROMPT.md` | 日销售简报：查询结论 → JSON |
| `schema.daily_sales.json` | 日销售简报字段说明 |
| `render_pillow.py` | 通用渲染（读 JSON，不绑死辽宁） |
| `data.example.json` | 辽宁示例 |
| `data.henan.example.json` | 河南占位示例（演示多省区） |
