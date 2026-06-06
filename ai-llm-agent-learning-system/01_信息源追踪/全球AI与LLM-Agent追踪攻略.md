# 全球 AI 与 LLM Agent 最新进展追踪攻略

## 目标

你要建立一套长期稳定的信息系统，而不是靠偶然刷到的文章学习。追踪 AI 进展时，建议把信息分为四类：

1. **研究进展**：论文、benchmark、开源代码。
2. **工程进展**：框架、工具、最佳实践、生产事故。
3. **产品进展**：OpenAI、Anthropic、Google、Meta、阿里、腾讯、字节、百度等产品能力变化。
4. **产业进展**：投融资、应用落地、监管、安全、人才需求。

重点关注 LLM Agent 时，优先看这些方向：

- Agentic Reasoning；
- Tool Use / Function Calling / CodeAct；
- Memory / Long-term Personalization；
- Planning / Search / Reflection；
- Multi-Agent Collaboration；
- Agentic RAG；
- Software Engineering Agent；
- Web / Computer Use Agent；
- Agent Evaluation；
- Agent Safety。

## 每日 10 分钟追踪流程

### 第 1 步：看 1 个主信息源，3 分钟

从下面列表中每天选一个，不要全看。

国内优先：

- 机器之心：https://www.jiqizhixin.com/
- 量子位：https://www.qbitai.com/
- 36Kr AI：https://www.36kr.com/
- InfoQ 中文站：https://www.infoq.cn/
- 腾讯云开发者社区：https://cloud.tencent.com/developer
- 阿里云开发者社区：https://developer.aliyun.com/
- 火山引擎开发者社区：https://developer.volcengine.com/
- 百度智能云千帆社区：https://cloud.baidu.com/qianfandev
- Zilliz 中文博客：https://zilliz.com.cn/blog
- Datawhale：https://www.datawhale.cn/

可作为补充，但国内访问可能不稳定：

- arXiv：https://arxiv.org/
- Papers with Code：https://paperswithcode.com/
- Hugging Face Papers：https://huggingface.co/papers
- GitHub Trending：https://github.com/trending
- OpenReview：https://openreview.net/

### 第 2 步：记录 1 条信息，3 分钟

记录格式：

```text
日期：
标题：
链接：
方向：模型 / RAG / Agent / Memory / Multi-Agent / Eval / Safety / Product
一句话总结：
为什么重要：
我需要验证什么：
```

### 第 3 步：判断优先级，2 分钟

用下面的 5 分制：

| 分数 | 判断标准 | 行动 |
| --- | --- | --- |
| 5 | 新范式、新 benchmark、顶会/大厂、可复现、与 Agent 强相关 | 加入周末精读 |
| 4 | 工程实践价值高，有代码或清晰案例 | 加入实战项目 |
| 3 | 有启发，但还不确定影响 | 放入观察清单 |
| 2 | 产品新闻或二手观点 | 只做摘要 |
| 1 | 标题党、无数据、无代码、无清晰来源 | 忽略 |

### 第 4 步：写一个面试化表达，2 分钟

把新进展转成一句能面试表达的话：

```text
最近我关注到 XXX，它解决的是 YYY 问题。它的关键思路是 ZZZ。
如果落地到生产系统，我会重点验证 A/B/C 三个指标。
```

## 每周 1 小时深度追踪流程

每周选择一个主题做深入整理：

1. 找 1 篇原论文；
2. 找 1 篇中文解读；
3. 找 1 个开源仓库；
4. 找 1 个工程博客；
5. 写一页总结：
   - 问题是什么；
   - 方法是什么；
   - 指标是什么；
   - 局限是什么；
   - 是否值得加入自己的项目。

## 推荐长期订阅主题

### 1. LLM Agent 论文关键词

建议在搜索时组合这些关键词：

- `LLM Agent survey`
- `agentic reasoning`
- `tool use large language models`
- `code action LLM agent`
- `memory LLM agents`
- `long-term memory agents`
- `multi-agent LLM`
- `agent evaluation benchmark`
- `software engineering agent`
- `web agent benchmark`
- `computer use agent`
- `agentic RAG`
- `prompt injection agent tools`

中文关键词：

- 大模型智能体
- LLM Agent
- Agentic Reasoning
- 工具调用
- 智能体记忆
- 多智能体协作
- Agent 评估
- 软件工程智能体
- Agent 安全
- 上下文工程

### 2. 重点会议与期刊

AI/ML：

- NeurIPS
- ICML
- ICLR
- AAAI
- IJCAI

NLP：

- ACL
- EMNLP
- NAACL
- COLING

系统与软件工程：

- ICSE
- FSE
- OSDI/SOSP
- VLDB/SIGMOD

人机交互与机器人：

- CHI
- IROS
- ICRA

建议方式：

- 不必完整追会；
- 每次会议只看关键词搜索结果；
- 优先看 `agent`、`tool use`、`memory`、`RAG`、`evaluation`。

### 3. 重点机构

国外：

- OpenAI
- Anthropic
- Google DeepMind
- Meta AI
- Microsoft Research
- Stanford
- UC Berkeley
- UIUC
- CMU
- Princeton

国内：

- 阿里通义
- 腾讯混元
- 百度文心/千帆
- 字节豆包/火山引擎
- 智谱 AI
- 月之暗面
- DeepSeek
- MiniMax
- 复旦 NLP
- 清华 NLP / KEG
- 上海 AI Lab

## LLM Agent 领域技术雷达

### A. 模型层趋势

关注问题：

- 推理模型是否更适合 Agent？
- 长上下文是否降低了外部记忆需求？
- 多模态模型是否能增强 computer use？
- 小模型是否能作为廉价 executor/critic？

典型资料：

- 各大模型发布报告；
- 推理模型 benchmark；
- Function calling 能力测试；
- 多模态 Agent demo。

判断标准：

- 不只看 benchmark 分数；
- 要看工具调用稳定性、JSON 有效率、长任务一致性、成本和延迟。

### B. Agent 架构趋势

关注问题：

- ReAct、Plan-and-Execute、CodeAct 各适合什么场景？
- Agent loop 如何避免无限循环？
- 状态机/图编排是否比自由循环更可靠？
- MCP、A2A、Computer Use 会如何改变工具生态？

典型资料：

- LangGraph 官方案例；
- AutoGen 多 Agent 案例；
- Anthropic / OpenAI / Google 的 Agent 工程博客；
- Manus、Cursor、Claude Code 等产品经验复盘。

### C. 记忆系统趋势

关注问题：

- 如何写入长期记忆？
- 如何处理历史事实冲突？
- 向量记忆、摘要记忆、图记忆各有什么优劣？
- 记忆是否真的提高任务成功率？

重点指标：

- 召回准确率；
- 时间推理；
- 冲突更新；
- token 成本；
- 隐私和权限。

### D. 评估趋势

关注问题：

- Agent 成功率如何定义？
- LLM-as-judge 是否可靠？
- 如何评估多轮任务？
- 如何复现生产环境里的失败？

建议关注：

- SWE-bench；
- WebArena；
- AgentBench；
- ToolBench；
- LoCoMo；
- LongMemEval；
- MemoryAgentBench；
- STATE-Bench。

### E. 安全趋势

关注问题：

- prompt injection 如何让 Agent 调错工具？
- 外部网页/文档里的恶意指令如何隔离？
- 工具调用权限如何最小化？
- Agent 是否会泄露用户记忆？

必须形成的工程意识：

- 工具白名单；
- 参数 schema 校验；
- 权限隔离；
- 审计日志；
- 人类确认高风险操作；
- 对外部内容做 instruction/data 分离。

## 国内网络环境下的资料获取策略

### 1. 论文

优先使用本资料库已经下载的 PDF：

```text
03_论文精读/papers_en/
```

如果需要补充论文：

1. 先搜索论文标题 + `PDF`；
2. 优先找 arXiv PDF；
3. 如果 arXiv 访问不稳定，尝试：
   - Hugging Face Papers 页面；
   - 作者主页；
   - 机构主页；
   - GitHub 仓库 README 中的 paper link；
   - 国内博客中的 PDF 镜像或研报附件。

### 2. 博客

国内优先顺序：

1. 腾讯云开发者社区；
2. 阿里云开发者社区；
3. 火山引擎开发者社区；
4. 百度智能云；
5. Zilliz 中文博客；
6. Datawhale；
7. 机器之心；
8. 量子位；
9. InfoQ 中文站。

国外博客如果打不开，建议搜索：

```text
文章标题 + 中文
文章标题 + 解读
文章标题 + 腾讯云
文章标题 + 阿里云
文章标题 + 机器之心
```

### 3. 开源代码

国内访问 GitHub 可能不稳定时：

- 先读本地 README 或论文；
- 搜索项目名 + Gitee；
- 搜索项目名 + 中文教程；
- 只下载 release/source zip；
- 对关键代码做小规模复刻，不依赖完整仓库。

## 每月趋势报告模板

每个月最后一天，写一页：

```text
# YYYY-MM LLM Agent 趋势报告

## 本月最重要的 5 条进展
1.
2.
3.
4.
5.

## 技术方向归类
- 模型：
- RAG：
- Agent 架构：
- 记忆：
- 多 Agent：
- 评估：
- 安全：

## 我认为最值得学习的一篇论文
- 标题：
- 原因：
- 我学到的关键点：

## 我认为最值得复现的一个项目
- 项目：
- 目标：
- 计划：

## 面试可用表达
- 最近我关注到：
- 它解决：
- 它的方法：
- 它的指标：
- 它的局限：
```

## 最重要的原则

1. **先建分类，再看新闻**：否则信息会碎片化。
2. **先看问题，再看方法**：论文的价值取决于它解决的问题是否重要。
3. **先看指标，再看结论**：没有评估的 Agent 方案不适合生产。
4. **先做小实验，再谈掌握**：Agent 能力必须通过运行轨迹验证。
5. **先能讲清楚，再追下一篇**：面试能力来自复述和结构化表达。
