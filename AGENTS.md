# AutoPilot Code Team

22 AI-native role configurations (Markdown) for AI IDEs — Cursor, Claude Code, Kimi Code, Trae, etc. Covers trend research → product definition → prototyping → development → testing → deployment → docs. All roles registered as Reasonix skills for automated invocation.

## Project

- **Stack**: Python 3 (`scripts/`), Markdown (role files), HTML (docs site), CI via GitHub Actions
- **Languages**: Chinese primary, English translations in `en/`, Chinese mirror in `zh-CN/`
- **Entry points**: `/vibe-project-manager` is the single user entry (inline skill); files in `product/` (6 roles) and `engineering/` (16 roles) are registered as subagent skills
- **Repo root** is the working directory for all commands

## Commands

| Action | Command |
|--------|---------|
| Validate all role files | `python scripts/validate.py` |
| Build GitHub Pages site | `python scripts/build-site.py` (output: `docs/index.html`) |
| Parse relay plan (dependency graph) | `python scripts/relay-parser.py --plan docs/examples/relay-plan-example.json` |
| Validate relay plan format | `python scripts/relay-parser.py --validate docs/examples/relay-plan-example.json` |
| Start relay execution state | `python scripts/relay-runner.py --plan docs/examples/relay-plan-example.json --init` |
| Get next batch instructions | `python scripts/relay-runner.py --plan docs/examples/relay-plan-example.json --next` |
| Mark batch completed | `python scripts/relay-runner.py --plan docs/examples/relay-plan-example.json --complete <phase:batch>` |
| Check relay progress | `python scripts/relay-runner.py --status` |
| Run pre-hook checks for a relay | `python scripts/relay-hooks.py --pre <relay-id> --plan docs/examples/relay-plan-example.json` |
| Run post-hook checks for a relay | `python scripts/relay-hooks.py --post <relay-id> --plan docs/examples/relay-plan-example.json` |
| List available hook checks | `python scripts/relay-hooks.py --list-checks` |
| Self-check a relay (goal mode) | `python scripts/relay-hooks.py --self-check <relay-id> --plan <plan.json>` |
| Run goal self-check loop | `python scripts/relay-goal.py --checks '[...]' --max-retry 3` |
| Run goal check for a feature | `python scripts/relay-goal.py --feature feature_list.json <feature-id>` |
| Create git worktree for relay | `python scripts/relay-worktree.py --create <name>` |
| List active worktrees | `python scripts/relay-worktree.py --list` |
| Merge worktree back to main | `python scripts/relay-worktree.py --merge <name>` |
| Remove worktree | `python scripts/relay-worktree.py --remove <name>` |
| Merge all relay worktrees | `python scripts/relay-worktree.py --merge-all` |
| Cleanup all relay worktrees | `python scripts/relay-worktree.py --cleanup-all` |
| Record memory entry | `python scripts/relay-memory.py --record <relay-id> role=xxx actual_effort=4.5 ...` |
| Recall role history | `python scripts/relay-memory.py --recall <role>` |
| Memory summary | `python scripts/relay-memory.py --summary` |
| Memory report (Markdown) | `python scripts/relay-memory.py --render` |
| Clear all memory | `python scripts/relay-memory.py --clear` |
| Initialize feature list with locks | `python scripts/relay-lock.py --init` |
| View lock/feature status | `python scripts/relay-lock.py --status` |
| Acquire feature lock | `python scripts/relay-lock.py --lock <feature-id> <owner>` |
| Release feature lock | `python scripts/relay-lock.py --unlock <feature-id>` |
| List available (unlocked) features | `python scripts/relay-lock.py --available` |

### Skill Invocation (Reasonix)

All 22 roles are registered as Reasonix skills. Use `/` commands to invoke them:

**Entry Point (user-facing):**

| Command | Description |
|---------|-------------|
| `/vibe-project-manager "我想做..."` | **项目经理 — 唯一入口。** 解析需求、输出接力计划，通过 subagent skills 派发工作并验收。用户只需和它对话。 |

**Product-side skills (called by PM for relay):**

| Command | Description |
|---------|-------------|
| `/vibe-trend-researcher "<task>"` | 趋势研究员 — 市场/技术趋势分析，输出可执行 Spec |
| `/product-manager "<task>"` | 产品经理 — 可执行产品 Spec、验证循环设计 |
| `/vibe-behavioral-designer "<task>"` | 体验设计师 — Agent 交互体验、提示词工程 |
| `/vibe-feedback-analyst "<task>"` | 反馈分析师 — 用户反馈聚类分析、洞察报告 |
| `/vibe-priority-orchestrator "<task>"` | 优先级调度器 — RICE-V 评分、动态优先级 |

**Engineering-side skills (called by PM for relay):**

| Command | Description |
|---------|-------------|
| `/vibe-architect "<task>"` | 系统架构师 — 技术架构 Spec、MCP 生态设计 |
| `/vibe-prototyper "<task>"` | 原型工程师 — Hours 级别可交互原型 |
| `/vibe-frontend-engineer "<task>"` | 前端工程师 — AI 辅助前端开发 |
| `/vibe-backend-engineer "<task>"` | 后端工程师 — AI 辅助后端开发 |
| `/vibe-ai-llm-engineer "<task>"` | LLM 工程师 — 模型选型、RAG、Agent 设计 |
| `/vibe-mobile-engineer "<task>"` | 移动端工程师 — 跨平台移动开发 |
| `/vibe-git-master "<task>"` | Git 大师 — 分支策略、提交规范、发布管理 |
| `/vibe-code-reviewer "<task>"` | 代码审查员 — 自动化代码审查、安全扫描 |
| `/vibe-minimal-change-engineer "<task>"` | 最小变更工程师 — 精准小范围改动 |
| `/vibe-qa-automation-engineer "<task>"` | QA 自动化工程师 — 测试自动化体系 |
| `/vibe-security-engineer "<task>"` | 安全工程师 — 提示注入防护、合规检查 |
| `/vibe-devops-engineer "<task>"` | DevOps 工程师 — IaC、CI/CD、可观测性 |
| `/vibe-database-engineer "<task>"` | 数据库工程师 — Schema 设计、查询优化 |
| `/vibe-data-engineer "<task>"` | 数据工程师 — 数据管道、ETL、训练数据 |
| `/vibe-onboarding-engineer "<task>"` | 入职工程师 — 新人自动化入职流程 |
| `/vibe-tech-writer "<task>"` | 技术文档工程师 — API 文档、知识库 |

CI runs `validate.py` on push/PR targeting `.md` files, `scripts/validate.py`, or the workflow file.

## Architecture

```
├── product/               # 6 product-side roles (Chinese, primary)
│   ├── product-manager.md
│   ├── vibe-behavioral-designer.md
│   ├── vibe-feedback-analyst.md
│   ├── vibe-priority-orchestrator.md
│   ├── vibe-project-manager.md  ← Entry point (inline skill)
│   └── vibe-trend-researcher.md
├── engineering/           # 16 engineering-side roles (Chinese, primary)
│   ├── vibe-ai-llm-engineer.md … vibe-tech-writer.md
├── .reasonix/skills/      # Auto-registered Reasonix skills (22 roles)
├── en/                    # English translations mirroring product/ + engineering/
├── zh-CN/                 # Chinese mirror (identical to root product/ + engineering/)
├── scripts/               # Utility scripts
│   ├── validate.py        # Validates frontmatter, emoji, persona, required sections
│   └── build-site.py      # Reads frontmatter + summary, emits docs/index.html
├── docs/                  # GitHub Pages site (index.html, ppt/)
├── examples/              # End-to-end ai-note-assistant example (8 stages)
└── .github/workflows/     # validate.yml CI
```

Each role file is self-contained: YAML frontmatter + sections (core mission, principles, deliverables, workflow, success metrics, communication style). Designed to be pasted as a system prompt into an AI IDE.

## Conventions

- **Frontmatter**: Every `.md` in `product/` and `engineering/` must have YAML frontmatter with `name`, `description`, `color`. Example:
  ```yaml
  ---
  name: vibe-backend-engineer
  description: AI-Native backend engineer...
  color: green
  ---
  ```
- **No emoji** anywhere in role files.
- **No role-playing**: no "You are Alex", "10 years experience", "前Google工程师". Define by capability, not persona.
- **Required sections** in every role file: 核心使命, 关键原则, 技术交付物, 工作流程, 成功指标, 沟通风格.
- **Toolchain declaration**: each file must list its modern AI toolchain (Cursor, v0, LangChain, etc.).
- **AI observability** (hallucination rate, TTFT, token cost, HITL rate) is recommended but optional.
- **Filenames**: kebab-case, prefixed `vibe-` for all roles except `product-manager.md`.
- **Line endings**: LF; encoding UTF-8.

## Notes

(Add project-specific notes here as they arise.)
