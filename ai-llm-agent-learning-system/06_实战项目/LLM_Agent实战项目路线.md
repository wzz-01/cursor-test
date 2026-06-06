# LLM Agent 实战项目路线

## 项目路线总览

建议做 4 个项目，从易到难形成作品集：

1. 本地知识库 RAG；
2. 工具调用 ReAct Agent；
3. 长期记忆个人助手；
4. 软件工程 Agent。

每个项目都必须有：

- README；
- 架构图；
- 运行方式；
- 测试集；
- trace 日志；
- 失败案例；
- 面试讲解稿。

---

# 项目 1：本地知识库 RAG

## 目标

让系统基于本地文档回答问题，并给出引用来源。

## 核心功能

- 加载 PDF/Markdown/TXT；
- 文档切分；
- embedding；
- 向量检索；
- rerank（可选）；
- 带引用生成；
- 拒答机制；
- 20 条测试集。

## 最小实现

```text
docs -> loader -> splitter -> vector index -> retriever -> prompt -> answer with citations
```

## 测试

必须测试：

- 问题答案在文档中；
- 问题答案不在文档中；
- 问题需要多个片段组合；
- 文档中存在相似但错误片段；
- 用户要求编造引用。

## 面试讲解重点

- 为什么要切分；
- 为什么要 rerank；
- 如何评估召回；
- 如何防止无依据回答；
- 如何做权限过滤。

---

# 项目 2：工具调用 ReAct Agent

## 目标

实现一个能调用搜索、计算、文件读取工具的 Agent。

## 核心功能

- ReAct loop；
- 工具 schema；
- 参数校验；
- 最大步数；
- 工具异常处理；
- trajectory JSON；
- 成功率统计。

## 最小实现

```text
User Goal
  -> Agent State
  -> Thought/Action
  -> Tool Dispatcher
  -> Observation
  -> Continue or Finish
```

## 测试

必须测试：

- 简单直接回答；
- 需要计算；
- 需要检索；
- 工具返回错误；
- 恶意输入诱导越权；
- 超过最大步数。

## 面试讲解重点

- ReAct 与普通 function calling 的区别；
- 工具安全；
- trace 如何排查失败；
- 为什么要有停止条件；
- 如何控制成本。

---

# 项目 3：长期记忆个人助手

## 目标

让 Agent 记住用户偏好、历史事实，并能在冲突时更新。

## 核心功能

- 记忆抽取；
- 记忆 schema；
- 记忆存储；
- 记忆检索；
- 记忆更新；
- 用户确认；
- 删除机制。

## 推荐 schema

```json
{
  "id": "memory_id",
  "user_id": "user_001",
  "type": "preference|fact|task|constraint",
  "content": "用户更喜欢中文回答",
  "source": "conversation_id",
  "confidence": 0.9,
  "created_at": "2026-06-06T00:00:00Z",
  "updated_at": "2026-06-06T00:00:00Z",
  "status": "active|expired|deleted"
}
```

## 测试

必须测试：

- 用户明确偏好；
- 用户隐含偏好；
- 用户偏好改变；
- 用户要求删除记忆；
- 错误记忆纠正；
- 多个用户隔离。

## 面试讲解重点

- 长上下文与长期记忆区别；
- 记忆污染；
- 冲突更新；
- 隐私删除；
- 记忆对任务成功率的影响。

---

# 项目 4：软件工程 Agent

## 目标

让 Agent 根据 bug 描述读取代码、定位问题、生成补丁、运行测试、输出报告。

## 核心工具

- list_files；
- search_code；
- read_file；
- propose_patch；
- apply_patch；
- run_tests；
- git_diff。

## 工作流

```text
Issue
  -> understand problem
  -> search relevant files
  -> inspect code
  -> propose fix
  -> apply patch
  -> run tests
  -> analyze failures
  -> final report
```

## 安全限制

- 禁止执行危险 shell 命令；
- 限制可读写目录；
- patch 必须最小化；
- 修改前后保存 diff；
- 测试失败不能强行宣称成功。

## 测试

必须测试：

- 小 bug；
- 多文件 bug；
- 测试失败后修复；
- issue 描述模糊；
- 无关文件诱导；
- 恶意 issue 要求删除文件。

## 面试讲解重点

- Agent-Computer Interface；
- CodeAct；
- 测试反馈；
- 最小补丁；
- 如何降低误改风险。

---

# 综合项目：个人 AI 研究助手

如果只想做一个最终大项目，建议做“个人 AI 研究助手”。

## 功能

1. 输入论文 PDF 或博客链接；
2. 自动提取标题、摘要、核心方法；
3. 生成中文精读；
4. 建立本地知识库；
5. 支持问答和引用；
6. 记录你读过什么；
7. 每周生成趋势报告；
8. 输出面试题。

## 架构

```text
PDF/Blog
  -> Parser
  -> RAG Index
  -> Paper Summarizer
  -> Agent Planner
  -> Memory Store
  -> Interview Generator
  -> Weekly Report
```

## 评估

- 摘要是否覆盖问题、方法、实验、局限；
- 问答是否引用正确；
- 周报是否按主题分类；
- 面试题是否可回答；
- 生成内容是否有幻觉。

## 简历描述示例

```text
设计并实现个人 AI 研究助手，支持论文解析、RAG 问答、长期阅读记忆、Agent 工具调用和周报生成。系统使用向量检索与结构化记忆管理，将论文精读流程自动化，并通过 50 条测试集评估引用准确率、任务成功率和平均 token 成本。
```

## 项目答辩结构

1. 为什么做；
2. 用户痛点；
3. 系统架构；
4. Agent loop；
5. RAG 和记忆；
6. 工具调用；
7. 评估指标；
8. 失败案例；
9. 下一步优化。
