# Vibe Coding Agent Team

<div align="center">

<p align="center">
  <strong>22 个 AI-Native 角色配置，覆盖产品定义到工程实现的完整链路</strong><br>
  可直接导入 Cursor / Claude Code / Kimi Code / Trae 等 AI IDE 使用
</p>

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/Agents-22-blue.svg" alt="Agents: 22">
  <a href="../CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
</p>
  <img src="https://img.shields.io/badge/Vibe%20Coding-AI%20Native-green.svg" alt="Vibe Coding: AI Native">
  <a href="../README.md"><img src="https://img.shields.io/badge/English-README-blue.svg" alt="English"></a>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> ·
  <a href="#项目结构">项目结构</a> ·
  <a href="#使用示例">使用示例</a> ·
  <a href="#贡献指南">贡献指南</a> ·
  <a href="../README.md">English</a> ·
  <a href="#许可证">许可证</a>
</p>

</div>

---

## 项目简介

Vibe Coding Agent Team 是一套面向 **Vibe Coding 时代** 的 AI-Native 智能体角色配置库，共包含 **21 个专业角色**，覆盖从趋势研究、产品定义、原型验证到开发、测试、部署运维的完整链路。

每个角色文件均包含：
- 完整的 System Prompt 配置（可直接导入 AI IDE）
- 可执行的 Spec 模板（非静态文档，可被 AI 直接消费）
- 标准化工作流程（Step-by-Step 操作指南）
- 成功指标与 AI 可观测性指标
- 现代工具链声明（Cursor, v0, Lovable, MCP, LangChain 等）

### 核心设计原则

| 原则 | 说明 |
|------|------|
| **零 Emoji** | 所有文件不含 emoji，保持专业 |
| **零角色扮演** | 去除 "你是 Alex"、"10 年经验" 等虚假人格，以能力定义身份 |
| **可执行 Spec** | 交付物是可被 AI IDE 直接执行的 Prompt 模板和代码配置，而非静态文档 |
| **RICE-V 评分** | 引入 Vibe Speed 和 Model Risk 评估，数据驱动优先级决策 |
| **AI 可观测性** | 每个角色包含幻觉率、TTFT、Token 成本、人工接管率等指标 |

---

## 快速开始

### 1. 选择角色

根据你当前的项目阶段，选择对应的角色文件：

```
项目启动阶段    →  vibe-trend-researcher + vibe-prototyper
产品定义阶段    →  product-manager + vibe-behavioral-designer
技术架构阶段    →  vibe-architect + vibe-priority-orchestrator
开发阶段        →  vibe-frontend-engineer / vibe-backend-engineer / vibe-mobile-engineer + vibe-ai-llm-engineer
质量保证阶段    →  vibe-qa-automation-engineer + vibe-code-reviewer + vibe-security-engineer
部署运维阶段    →  vibe-devops-engineer + vibe-database-engineer + vibe-data-engineer
文档交付阶段    →  vibe-tech-writer
团队扩展阶段    →  vibe-onboarding-engineer
反馈迭代阶段    →  vibe-feedback-analyst
```

### 2. 导入 AI IDE

**Cursor**：
1. 打开 Cursor Settings → Rules
2. 创建新 Rule，将 `.md` 文件内容粘贴到 System Prompt 中
3. 保存后，在对话中 @ 该角色即可调用

**Claude Code**：
1. 在项目根目录创建 `CLAUDE.md`
2. 将角色文件内容追加到 `CLAUDE.md` 中
3. 运行 `claude` 时自动加载角色配置

**Kimi Code / Trae / Roo Code**：
将 `.md` 文件内容作为 System Prompt 或角色配置导入即可。

### 3. 开始协作

每个角色文件包含完整的工作流程。例如，调用 `vibe-prototyper`：

> "请按照你的工作流程，帮我把这个需求转化为可交互原型。需求是：一个 AI 驱动的待办应用，用户可以用自然语言添加任务。"

角色会自动执行：需求理解 → AI 生成原型 → 用户测试设计 → 洞察分析 → 原型到代码迁移。

---

## 项目结构

```
├── autopilot-code-team/               # 项目根目录
│   ├── LICENSE                         # MIT 许可证
│   ├── README.md                       # 英文版（默认展示）
│   ├── zh-CN/README.md                 # 中文版（本文件）
│
├── product/                             # 中文产品侧角色（5个）
│   ├── product-manager.md
│   ├── vibe-behavioral-designer.md
│   ├── vibe-feedback-analyst.md
│   ├── vibe-priority-orchestrator.md
│   └── vibe-trend-researcher.md
│
├── engineering/                         # 中文工程侧角色（16个）
│   ├── vibe-ai-llm-engineer.md
│   ├── vibe-architect.md
│   ├── vibe-backend-engineer.md
│   ├── vibe-code-reviewer.md
│   ├── vibe-database-engineer.md
│   ├── vibe-data-engineer.md
│   ├── vibe-devops-engineer.md
│   ├── vibe-frontend-engineer.md
│   ├── vibe-git-master.md
│   ├── vibe-minimal-change-engineer.md
│   ├── vibe-mobile-engineer.md
│   ├── vibe-onboarding-engineer.md
│   ├── vibe-prototyper.md
│   ├── vibe-qa-automation-engineer.md
│   ├── vibe-security-engineer.md
│   └── vibe-tech-writer.md
│
├── zh-CN/                               # 中文版本
│   ├── product/                           # 中文产品侧角色（5）
│   └── engineering/                       # 中文工程侧角色（16）
│
├── en/                                  # 英文版本
│   ├── product/                           # 英文产品侧角色（5）
│   └── engineering/                       # 英文工程侧角色（16）
│
├── examples/                            # 示例项目
│   └── ai-note-assistant/                 # 端到端示例（8个阶段）
│
├── scripts/                             # 构建和验证脚本
│   ├── validate.py
│   └── build-site.py
│
└── docs/                                # GitHub Pages 站点
    └── index.html
```

**总计：21 个智能体角色（中英双语）**

---

## 使用示例

### 场景：快速验证一个产品假设

```
Step 1: 调用 vibe-trend-researcher
  "研究 2026 年 AI 待办应用的市场趋势，输出可执行趋势 Spec"

Step 2: 调用 vibe-prototyper
  "基于趋势 Spec，用 v0 生成可交互原型，目标：2 小时内完成"

Step 3: 调用 vibe-priority-orchestrator
  "对原型验证结果做 RICE-V 评分，决定是否进入开发"

Step 4: 调用 product-manager + vibe-behavioral-designer
  "输出可执行产品 Spec，包含设计 Token 和组件规范"

Step 5: 调用 vibe-architect + vibe-frontend-engineer + vibe-backend-engineer
  "按 Spec 进行开发，使用 Cursor 辅助编码"

Step 6: 调用 vibe-qa-automation-engineer + vibe-code-reviewer
  "自动化测试 + 代码审查 + 安全扫描"

Step 7: 调用 vibe-devops-engineer
  "部署到 Vercel，配置可观测性"

Step 8: 调用 vibe-tech-writer
  "同步更新文档，确保代码与文档一致"
```

---

## 角色能力速查

| 角色 | 核心能力 | 关键工具链 | Vibe Speed |
|------|---------|-----------|------------|
| vibe-trend-researcher | AI 驱动趋势研究 | Perplexity, Deep Research, Kimi Research | Days |
| vibe-prototyper | Hours 级原型验证 | v0, Lovable, Bolt, Cursor | Hours |
| vibe-priority-orchestrator | RICE-V 动态优先级 | PostHog, Amplitude, Langfuse | Days |
| vibe-behavioral-designer | Agent 体验设计 | System Prompt 工程, MCP 工具设计 | Days |
| vibe-feedback-analyst | LLM 语义反馈分析 | 向量数据库, RAG pipeline | Days |
| vibe-architect | MCP 生态架构设计 | Terraform, Kubernetes, Vercel | Weeks |
| vibe-ai-llm-engineer | LLM 应用开发 | LangChain, Vercel AI SDK, Langfuse | Days |
| vibe-frontend-engineer | AI 辅助前端开发 | Cursor, v0 Dev Mode, Tailwind | Days |
| vibe-backend-engineer | AI 辅助后端开发 | Cursor, Claude Code, Supabase | Days |
| vibe-qa-automation-engineer | AI 驱动质量门禁 | 智能测试生成, 视觉回归, 安全扫描 | Days |
| vibe-security-engineer | AI 安全审计 | 提示注入检测, 零信任架构 | Days |
| vibe-devops-engineer | AI 部署与可观测性 | Terraform, Kubernetes, Helicone | Days |
| vibe-database-engineer | 数据库设计与优化 | Supabase, Pinecone, Qdrant | Days |
| vibe-data-engineer | 数据管道与 RAG | ETL, 向量数据库, 数据质量 | Weeks |
| vibe-git-master | AI 时代 Git 工作流 | Conventional Commits, 自动化合并 | Hours |
| vibe-onboarding-engineer | 新人 Day 1 上手 | Dev Container, AI 辅助导览 | Days |
| vibe-tech-writer | 活文档与知识库 | 文档即代码, 示例可运行 | Days |
| vibe-code-reviewer | AI 代码审查 | 代码质量, 安全漏洞, 性能 | Hours |
| vibe-mobile-engineer | AI 移动开发 | Cursor, React Native, Flutter | Days |
| vibe-minimal-change-engineer | 精细化改动 | 最小变更原则, 影响面评估 | Hours |
| product-manager | 产品定义与决策 | RICE-V, 可执行 Spec | Days |

---

## 贡献指南

我们欢迎所有贡献！无论是：
- 新增角色
- 改进现有角色的 Prompt 或工作流程
- 修正工具链或链接
- 补充使用示例

### 提交前检查清单

- [ ] 文件使用 YAML Frontmatter，包含 `name`, `description`, `color` 字段
- [ ] 文件内容不含 emoji
- [ ] 不含虚假角色扮演（"你是 Alex"、"10 年经验" 等）
- [ ] 包含核心使命、关键原则、技术交付物、工作流程、成功指标、沟通风格
- [ ] 包含现代 AI 工具链声明
- [ ] 包含 AI 可观测性指标（至少覆盖幻觉率、TTFT、Token 成本）
- [ ] 本地验证通过：`python scripts/validate.py` 无错误

### 提交方式

1. Fork 本仓库
2. 创建你的分支 (`git checkout -b feature/new-role`)
3. 提交更改 (`git commit -am 'Add vibe-xxx role'`)
4. 推送到分支 (`git push origin feature/new-role`)
5. 创建 Pull Request

详见 [CONTRIBUTING.md](../CONTRIBUTING.md)。

---

## 许可证

本项目采用 [MIT License](../LICENSE) 开源。

你可以自由使用、修改、分发，包括商业用途。只需保留原始版权声明即可。

---

## 致谢

本项目的角色设计灵感来源于 Vibe Coding 生态的最新实践，包括 Cursor、v0、 Lovable, Claude Code、Kimi Code 等 AI 工具的使用经验，以及 MCP 协议、RICE-V 评分框架等前沿方法论。

特别感谢所有贡献者和使用者的反馈，让这套智能体团队持续进化。

---

<div align="center">

**用 AI 团队，做 Vibe 产品。**

</div>
