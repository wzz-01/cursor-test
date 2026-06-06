# AI 插件、AI 编辑器与 CLI Agent 生态全景

## 一、工具生态从 Copilot 到 Agent 的演进

AI 开发工具大致经历了 5 个阶段：

1. **补全阶段**：GitHub Copilot 代表，AI 主要做代码补全。
2. **聊天阶段**：ChatGPT、Copilot Chat、Claude，AI 能解释代码和回答问题。
3. **多文件编辑阶段**：Cursor、Windsurf、Cline，AI 能修改多个文件。
4. **Agent 阶段**：Claude Code、Codex CLI、Aider、OpenHands，AI 能规划、编辑、运行测试、迭代。
5. **云端自动执行阶段**：Devin、Jules、Codex Cloud Agents、Cursor Background Agents，AI 在后台处理任务并提交 PR。

## 二、AI 插件与平台扩展

## 1. ChatGPT Plugins / GPTs / Actions

### 定位

OpenAI 早期通过 Plugins 让 ChatGPT 连接外部服务，后续转向 GPTs 和 Actions，让用户构建定制助手。

### 优势

- 用户门槛低；
- 分发入口强；
- 可接 API；
- 适合轻量业务助手。

### 缺点

- 插件生态曾存在质量不稳定；
- 工具权限和安全需要谨慎；
- 复杂企业流程仍需后端系统。

### 适合

- 查询类助手；
- 内部工具入口；
- 轻量客服；
- 文档问答。

## 2. Claude Desktop + MCP

### 定位

Anthropic 推动 MCP，让模型以标准方式连接工具、文件、数据库和服务。

### 优势

- 标准化工具协议；
- 本地工具和企业系统接入更清晰；
- Claude Code/Claude Desktop 生态强；
- 适合开发者和企业内部工具。

### 缺点

- MCP 不自动解决权限和安全；
- 工具质量由 server 实现决定；
- 需要治理和审计。

### 适合

- 本地开发工具；
- 企业内部系统；
- 数据库查询；
- 文件和知识库访问。

## 3. Gemini Extensions / Google Workspace AI

### 定位

Google 将 Gemini 接入 Gmail、Docs、Sheets、Drive、Meet、Search、Android。

### 优势

- 办公和搜索生态；
- 多模态；
- 长上下文；
- 适合知识工作者。

### 缺点

- 深度依赖 Google 生态；
- 企业权限配置复杂；
- 不一定适合非 Google 技术栈。

## 4. Microsoft Copilot 插件体系

### 定位

围绕 Microsoft 365、Teams、Windows、GitHub 和 Azure 构建 Copilot。

### 优势

- 企业入口强；
- Office、Teams、GitHub 深度集成；
- 权限和合规能力强；
- Copilot Studio 支持企业工作流。

### 缺点

- 产品线复杂；
- 不同 Copilot 能力差异大；
- 定制复杂场景需要平台经验。

## 三、AI 编辑器 / IDE

## 1. Cursor

### 定位

AI-native IDE，基于 VS Code 体验，强调 Composer、Chat、多文件编辑和背景 Agent。

### 优势

- 使用体验好；
- 多文件上下文理解强；
- 适合日常开发；
- 支持多模型；
- 背景 Agent 适合并行任务。

### 缺点

- 闭源；
- 依赖订阅和模型额度；
- 企业治理需额外配置；
- 大规模重构仍需人工 review。

### 适合

- 日常功能开发；
- 快速原型；
- 代码解释；
- 多文件修改；
- 个人和小团队。

## 2. Windsurf

### 定位

Codeium/Windsurf 系 AI IDE，强调 Cascade agentic workflow。

### 优势

- Agent 流程体验好；
- 原型开发快；
- 价格和企业方案有竞争力；
- 多文件编辑能力强。

### 缺点

- 公司归属和产品路线曾有变化；
- 企业长期选型需关注供应商风险；
- 与 Cursor/Copilot 竞争激烈。

### 适合

- 快速开发；
- 前端/全栈原型；
- Agent IDE 体验；
- 成本敏感团队。

## 3. GitHub Copilot

### 定位

最广泛采用的 IDE 插件和 GitHub 生态 AI 助手。

### 优势

- 用户规模最大；
- VS Code、JetBrains 等 IDE 集成；
- GitHub PR、Issue、Actions 生态；
- 企业采购和治理相对成熟；
- 补全体验强。

### 缺点

- Agent 深度长期弱于 Claude Code/Cursor 等专门工具；
- 多文件自主修改能力取决于具体版本；
- 对非 GitHub 工作流优势下降。

### 适合

- 企业研发团队；
- GitHub 工作流；
- 代码补全；
- PR review；
- 低摩擦普及。

## 4. Continue.dev

### 定位

开源 AI 编程插件，可接多种模型和本地模型。

### 优势

- 开源；
- BYOK；
- 可接本地模型；
- 适合自定义和私有化。

### 缺点

- 产品体验不如商业 IDE；
- 需要配置；
- Agent 能力取决于模型和集成。

### 适合

- 开源爱好者；
- 私有化团队；
- 本地模型实验；
- 需要模型自由切换的团队。

## 5. Cline / Roo Code / Kilo Code

### 定位

VS Code Agent 插件，强调自动编辑、工具调用、终端执行和 BYOK。

### 优势

- 开源或社区活跃；
- 模型选择自由；
- 可执行命令和编辑文件；
- 适合 Agent 实验。

### 缺点

- 安全风险更高；
- 需要人工监督；
- 体验和稳定性取决于配置；
- 成本由所选模型决定。

### 适合

- 开发者实验；
- 私有模型；
- 小团队自动化；
- Agent workflow 学习。

## 6. Zed AI

### 定位

高性能编辑器 Zed 中的 AI 功能。

### 优势

- 编辑器性能好；
- 协作体验好；
- AI 集成逐步增强。

### 缺点

- 生态不如 VS Code；
- Agent 能力不是最成熟。

## 7. Replit Agent

### 定位

云端在线 IDE + Agent，适合从自然语言生成应用。

### 优势

- 环境开箱即用；
- 适合教学、原型、Web 应用；
- 生成、运行、部署一体。

### 缺点

- 复杂工程和企业代码库不一定适合；
- 平台绑定；
- 自主生成代码仍需 review。

## 8. Kiro / Amazon Q Developer

### 定位

面向规范驱动开发、AWS 生态或企业研发的 AI 开发工具。

### 优势

- 企业和云平台结合；
- 适合 AWS 用户；
- 强调规范、任务和工作流。

### 缺点

- 生态心智不如 Cursor/Copilot；
- 使用体验依赖具体云服务。

## 四、CLI Agent

CLI Agent 是 2025-2026 最重要的开发者工具形态之一。它们运行在终端中，能读仓库、编辑文件、运行测试、提交变更。

## 1. Claude Code

### 定位

Anthropic 的终端代码 Agent，强在复杂推理、代码理解和长任务。

### 优势

- 深度代码理解；
- 复杂重构能力强；
- 适合大型仓库；
- 可运行命令和测试；
- 与 Claude 模型能力结合紧密。

### 缺点

- 闭源；
- 成本可能高；
- 需要严格 review；
- 企业权限需要治理。

### 适合

- 架构重构；
- 复杂 bug；
- 代码审查；
- 大型仓库理解；
- 高价值工程任务。

## 2. OpenAI Codex CLI

### 定位

OpenAI 生态的 CLI coding agent，可结合 GPT/Codex 模型和 Agents SDK。

### 优势

- OpenAI 模型生态；
- 工具调用和代码能力；
- 与 ChatGPT/Codex/Cloud Agent 生态衔接；
- 适合并行任务和自动化。

### 缺点

- 依赖 OpenAI 模型；
- 成本和权限需管理；
- 自主修改仍需审查。

### 适合

- OpenAI 用户；
- 软件工程自动化；
- 终端工作流；
- issue 到 patch。

## 3. Gemini CLI

### 定位

Google Gemini 生态的 CLI Agent。

### 优势

- 长上下文；
- Google 模型和云生态；
- 适合大仓库上下文；
- 成本/速度可能有优势。

### 缺点

- 工具生态成熟度需看版本；
- 非 Google 用户采用成本较高。

## 4. Aider

### 定位

开源、Git-native 的 CLI coding assistant。

### 优势

- 开源；
- Git diff 工作流清晰；
- 支持多模型；
- BYOK；
- 适合本地开发和成本控制。

### 缺点

- 体验不如商业 IDE；
- 需要终端习惯；
- 复杂任务效果依赖模型。

### 适合

- 开源开发者；
- 终端党；
- 私有化模型；
- 可控 diff 流程。

## 5. OpenHands

### 定位

开源软件工程 Agent 平台，可本地/云端运行。

### 优势

- 开源；
- 可自托管；
- Agent 环境完整；
- 适合研究和企业自建。

### 缺点

- 部署和维护复杂；
- 效果依赖模型；
- 需要安全沙箱。

## 6. Plandex

### 定位

面向大任务规划和多文件修改的 CLI Agent。

### 优势

- 计划式工作流；
- 适合跨文件大改；
- 可审查计划。

### 缺点

- 学习成本；
- 社区和生态不如主流工具。

## 7. OpenCode / Kimi Code CLI / GitHub Copilot CLI / Cursor CLI

### 定位

不同模型和平台推出的终端 Agent，目标都是将 AI 编程从 IDE 扩展到命令行。

### 共同优势

- 贴近开发者真实工作流；
- 能运行测试；
- 能处理多文件；
- 适合自动化任务。

### 共同风险

- 误执行命令；
- 误改文件；
- 泄露代码；
- 成本失控；
- 缺少审计。

## 五、云端 Agent

## 1. Devin

### 定位

云端自主软件工程 Agent，接受任务后在远程环境中执行。

### 优势

- 更接近“AI 工程师”形态；
- 可异步执行任务；
- 适合 issue 级别工作；
- 能运行环境和测试。

### 缺点

- 成本；
- 代码安全；
- 自主性仍需审核；
- 复杂需求仍可能失败。

## 2. OpenAI Codex Cloud Agents

### 定位

OpenAI 云端代码 Agent，面向后台任务、代码修改和 PR。

### 优势

- 与 OpenAI/Codex 生态结合；
- 适合后台并行任务；
- 可与 ChatGPT 和 GitHub 工作流衔接。

### 缺点

- 供应商锁定；
- 权限和代码访问需谨慎。

## 3. GitHub Copilot Coding Agent

### 定位

GitHub 原生 coding agent，可处理 issue、生成代码、提交 PR。

### 优势

- GitHub 集成最强；
- 企业采用容易；
- 和 issue/PR/actions 流程自然结合。

### 缺点

- 灵活性取决于 GitHub 平台；
- 对非 GitHub 工作流不占优势。

## 4. Cursor Background Agents

### 定位

Cursor 中的后台 Agent，可并行处理任务。

### 优势

- IDE 内体验好；
- 可并行；
- 适合日常开发任务拆分。

### 缺点

- 需要管理多个 Agent 的输出；
- 合并冲突和质量控制需要人工。

## 5. Google Jules

### 定位

Google 的异步 coding agent，面向 GitHub 任务和代码修改。

### 优势

- Google/Gemini 生态；
- 异步任务；
- 适合代码维护。

### 缺点

- 生态成熟度和可用性需持续观察。

## 六、应用生成工具

## 1. v0 by Vercel

### 定位

从自然语言生成前端 UI 和 React/Next.js 代码。

### 优势

- 前端原型快；
- UI 质量好；
- 与 Vercel/Next.js 生态结合。

### 缺点

- 复杂业务逻辑仍需工程师；
- 容易生成 demo 级代码；
- 需要设计和代码 review。

## 2. Bolt.new

### 定位

浏览器内生成和运行 Web 应用。

### 优势

- 快速原型；
- 环境集成；
- 适合 MVP。

### 缺点

- 大型工程不适合全靠生成；
- 平台绑定；
- 代码质量需审查。

## 3. Lovable

### 定位

面向产品原型和全栈应用生成。

### 优势

- 非工程师也能快速做产品；
- 适合 SaaS 原型；
- UI/产品流程生成快。

### 缺点

- 复杂后端和安全需工程师接管；
- 生成代码可维护性不稳定。

## 4. Galileo / Uizard / Figma AI

### 定位

设计稿、UI、原型生成。

### 优势

- 设计效率；
- 快速视觉探索；
- 产品早期验证。

### 缺点

- 不是完整工程交付；
- 设计一致性和业务逻辑需人工。

## 七、Agent 框架

## 1. LangChain / LangGraph

### 定位

LangChain 是 LLM 应用框架，LangGraph 是状态图 Agent 框架。

### 优势

- 生态大；
- 工具多；
- LangGraph 适合可控 Agent；
- 适合生产级状态管理。

### 缺点

- 抽象多，学习成本；
- 版本迭代快；
- 简单项目可能过重。

## 2. LlamaIndex

### 定位

RAG 和数据连接框架。

### 优势

- 文档索引；
- 数据连接；
- Agentic RAG；
- 企业知识库。

### 缺点

- 复杂项目需理解内部抽象；
- 性能和效果仍需自测。

## 3. AutoGen

### 定位

Microsoft 多 Agent 会话框架。

### 优势

- 多角色协作；
- 研究和原型快；
- 适合多 Agent 实验。

### 缺点

- 生产治理需额外设计；
- 多 Agent 成本高。

## 4. CrewAI

### 定位

角色 + 任务 + 流程的多 Agent 框架。

### 优势

- 上手快；
- 适合业务流程原型；
- 角色化清晰。

### 缺点

- 复杂状态和严格控制需要额外工程；
- 容易变成“多个 prompt 串联”。

## 5. Semantic Kernel

### 定位

Microsoft 面向企业集成的 AI 编排框架。

### 优势

- .NET/企业生态；
- 插件和 planner；
- 与 Azure/Microsoft 生态适配。

### 缺点

- 非 Microsoft 技术栈吸引力下降。

## 6. OpenAI Agents SDK

### 定位

OpenAI 官方 Agent 开发工具。

### 优势

- 与 OpenAI 模型和工具调用深度集成；
- 适合快速构建 OpenAI 生态 Agent；
- 支持 tracing、tools、handoffs 等能力。

### 缺点

- 供应商绑定；
- 多模型自由度较低。

## 7. MCP

### 定位

模型上下文协议，用于标准化工具和资源接入。

### 优势

- 工具接入标准化；
- IDE/CLI/桌面 Agent 可复用工具；
- 促进生态互通。

### 缺点

- 不自动提供安全；
- 工具 server 质量参差；
- 权限和审计仍需自己做。

## 八、工具选型建议

### 个人开发者

推荐组合：

- 日常：Cursor 或 Windsurf；
- 复杂任务：Claude Code 或 Codex CLI；
- 开源/低成本：Aider + 本地/开源模型；
- 原型：v0 / Bolt / Lovable；
- 学习 Agent：Cline / OpenHands / LangGraph。

### 企业研发团队

推荐组合：

- IDE 插件：GitHub Copilot 或 Cursor Enterprise；
- 高级重构：Claude Code / Codex CLI；
- 云端任务：GitHub Copilot Coding Agent / Devin / Codex Cloud；
- 内部 Agent 框架：LangGraph / Semantic Kernel / AutoGen；
- 工具协议：MCP；
- 评估治理：固定测试集 + trace + 权限审计。

### 私有化团队

推荐组合：

- 模型：Qwen / DeepSeek / Llama / Mistral；
- IDE：Continue / Cline / Roo Code；
- CLI：Aider / OpenHands；
- RAG：LlamaIndex / LangChain；
- 部署：vLLM / TGI / TensorRT-LLM；
- 监控：自建 trace 和日志。

## 九、主要风险

1. AI 工具误改代码；
2. Agent 执行危险命令；
3. 工具调用越权；
4. 代码或数据泄露；
5. 生成代码不可维护；
6. 成本失控；
7. 过度依赖单一供应商；
8. 缺少测试集；
9. 团队没有 review 规范；
10. 安全策略落后于 Agent 能力。

## 十、结论

AI 工具生态正在从“补全工具”变成“研发自动化平台”。未来团队的最佳实践不是选择一个工具，而是形成组合：

```text
AI IDE 负责日常开发
CLI Agent 负责复杂重构
Cloud Agent 负责异步任务
RAG/Memory 负责项目知识
MCP/Tool Registry 负责工具接入
Trace/Evaluation 负责治理
Human Review 负责最终质量
```
