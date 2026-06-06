# 大模型发展史与 AI 工具体系全景图谱

> 这是一个全新的独立目录，不放入之前两个学习计划文件夹。

## 目标

系统梳理大模型从 Transformer 到 Agentic AI 的发展史，并覆盖：

1. 主流模型公司及其模型发展路线；
2. 每半年一次的行业阶段总结；
3. 每个阶段的领先模型、优势、缺点和关键指标；
4. AI 插件、AI 编辑器、CLI Agent、Cloud Agent、开发者工具生态；
5. 模型选型、工具选型和未来趋势判断。

## 目录结构

| 目录 | 文件 | 内容 |
| --- | --- | --- |
| `00_总览` | `大模型发展史总览.md` | 大模型发展主线、阶段划分、核心指标 |
| `01_按公司分类的大模型发展史` | `全球主要公司模型发展史.md` | 按公司梳理模型家族、历史、优势、短板 |
| `02_半年阶段时间线` | `2017-2026每半年大模型发展总结.md` | 每半年总结一次关键模型、领先者、技术主题 |
| `03_领先模型与指标对比` | `领先模型能力指标与优缺点分析.md` | 领先模型、指标、能力维度、适用场景 |
| `04_AI插件编辑器与CLI_Agent生态` | `AI工具生态全景.md` | 插件、编辑器、CLI Agent、云端 Agent、框架 |
| `05_趋势判断与选型建议` | `模型与工具选型指南.md` | 企业、个人、研发团队如何选模型和工具 |

## 覆盖范围

### 模型公司

国外：

- OpenAI
- Anthropic
- Google / DeepMind
- Meta
- xAI
- Microsoft
- Amazon
- Apple
- NVIDIA
- Mistral AI
- Cohere
- AI21 Labs
- Perplexity
- Stability AI

国内：

- 阿里巴巴 / 通义千问 Qwen
- DeepSeek
- 百度 / 文心 ERNIE
- 腾讯 / 混元 Hunyuan
- 字节跳动 / 豆包 Doubao
- 智谱 AI / GLM
- 月之暗面 / Kimi
- MiniMax
- 百川智能 Baichuan
- 零一万物 01.AI / Yi
- 商汤 / 日日新 SenseNova
- 科大讯飞 / 星火 Spark
- 华为 / 盘古 Pangu
- 阶跃星辰 StepFun
- 上海 AI Lab / InternLM

### 工具生态

- AI 插件：ChatGPT Plugins、GPTs、Claude Artifacts、Gemini Extensions、MCP 工具等；
- AI 编辑器：Cursor、Windsurf、GitHub Copilot、Continue、Cline、Roo Code、Zed、Replit Agent、Kiro 等；
- CLI Agent：Claude Code、Codex CLI、Gemini CLI、Aider、OpenHands、Plandex、OpenCode 等；
- 云端 Agent：Devin、Jules、Codex Cloud Agents、Cursor Background Agents、GitHub Copilot Coding Agent 等；
- 应用生成工具：v0、Bolt.new、Lovable、Replit、Galileo 等；
- Agent 框架：LangChain、LangGraph、LlamaIndex、AutoGen、CrewAI、Semantic Kernel、OpenAI Agents SDK、MCP。

## 阅读方式

1. 如果你想了解行业历史：先读 `02_半年阶段时间线`。
2. 如果你想了解每家公司：读 `01_按公司分类的大模型发展史`。
3. 如果你要做模型选型：读 `03_领先模型与指标对比` 和 `05_趋势判断与选型建议`。
4. 如果你关注 AI 编程工具：读 `04_AI插件编辑器与CLI_Agent生态`。

## 总体判断

大模型发展可以概括为 7 条主线：

1. **架构主线**：RNN/CNN -> Transformer -> MoE -> Long Context -> Multimodal -> Agentic System。
2. **训练主线**：预训练 -> 指令微调 -> RLHF/DPO -> 推理强化 -> Agent 行为优化。
3. **能力主线**：补全文本 -> 对话 -> 工具调用 -> 代码生成 -> 长任务执行 -> 电脑操作。
4. **产品主线**：API -> Chatbot -> Copilot -> AI IDE -> CLI Agent -> Cloud Agent。
5. **商业主线**：模型收费 -> 平台生态 -> 企业工作流 -> Agent 自动化。
6. **开源主线**：BERT/T5 -> LLaMA -> Mistral/Qwen/DeepSeek -> 高性能开放权重模型。
7. **安全主线**：内容安全 -> 对齐 -> 工具权限 -> 记忆隐私 -> Agent 审计。

## 注意

AI 模型更新非常快。本资料库按 2026 年 6 月前后的公开资料整理，部分 2026 年模型信息来自公开网页和行业资料，建议用于趋势学习与体系梳理；如果要做商业采购或生产部署，需要再核对官方文档、价格页、系统卡和 API 文档。
