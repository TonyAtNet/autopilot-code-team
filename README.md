# AutoPilot Code Team

<div align="center">

<p align="center">
  <strong>22 AI-Native Agent Roles for Vibe Coding Workflows</strong><br>
  One team, every agent tool — Reasonix · Claude Code · Codex CLI · OpenCode · Cursor
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/Agents-22-blue.svg" alt="Agents: 22">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python 3.11+">
  <a href="https://github.com/TonyAtNet/autopilot-code-team/actions/workflows/ci.yml"><img src="https://github.com/TonyAtNet/autopilot-code-team/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
  <a href="zh-CN/README.md"><img src="https://img.shields.io/badge/中文文档-README-red.svg" alt="中文文档"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#project-structure">Project Structure</a> ·
  <a href="#usage-example">Usage Example</a> ·
  <a href="#contribution-guide">Contribution Guide</a> ·
  <a href="zh-CN/README.md">中文文档</a> ·
  <a href="#license">License</a>
</p>

</div>

---

## Project Introduction

AutoPilot Code Team is a set of **AI-Native agent role configurations** for the **Vibe Coding era**, containing **22 professional roles** covering the complete chain from trend research, product definition, prototype validation to development, testing, deployment, and operations.

### Why AutoPilot Code Team?

**One conversation, one team.** You don't need to know which of the 22 roles does what. Just talk to the **project manager** (`vibe-project-manager`) — it automatically breaks down your requirements, dispatches tasks to the right subagents, tracks progress across the relay pipeline, and delivers finished results. The team truly works *as a team* behind the scenes. Perfect for beginners and solo developers: describe what you want, and the agents figure out the rest.

---

Each role file contains:
- Complete System Prompt configuration (directly importable into AI IDEs)
- Executable spec templates (not static documents, directly consumable by AI)
- Standardized workflows (step-by-step operation guides)
- Success metrics and AI observability metrics
- Modern toolchain declarations (Cursor, v0, Lovable, MCP, LangChain, etc.)

### Core Design Principles

| Principle | Description |
|-----------|-------------|
| **Zero Emoji** | All files contain no emoji, maintaining professionalism |
| **Zero Role-Playing** | Remove "You are Alex", "10 years experience" and other false personas; define identity by capability |
| **Executable Specs** | Deliverables are prompt templates and code configurations that AI IDEs can directly execute, not static documents |
| **RICE-V Scoring** | Introduce Vibe Speed and Model Risk assessment for data-driven priority decisions |
| **AI Observability** | Every role includes hallucination rate, TTFT, token cost, human-in-the-loop rate |

---

## Quick Start

### 0. Automated Mode (Reasonix)

All 22 roles are registered as **Reasonix skills**. You only need to talk to one role — the **project manager**.

1. Open Reasonix with this project
2. Type: `/vibe-project-manager "I want to build an AI note-taking assistant"`
3. The PM handles everything

---

### 1. Clone & Install (All Platforms)

Clone the repo and run the install script to set up all supported agent tools:

```bash
git clone https://github.com/TonyAtNet/autopilot-code-team.git
cd autopilot-code-team
python scripts/install.py --all
```

This generates configurations for 4 platforms. See the platform-specific guides below.

---

### 2. Platform-Specific Usage

**Reasonix** (auto-detected):
- Open Reasonix in this directory
- Use `/vibe-project-manager "..."` as the entry point
- All 22 roles available as subagent skills via `.reasonix/skills/`

**Claude Code** (`.claude/agents/`):
- Run `claude` in the project directory
- Claude Code auto-loads `CLAUDE.md` and discovers subagents in `.claude/agents/`
- Subagents are invoked automatically based on task context
- 22 subagents: `vibe-trend-researcher`, `product-manager`, `vibe-frontend-engineer`, etc.
- Manual command: `claude --agent vibe-project-manager "I want to build an AI note assistant"`

**Codex CLI** (`AGENTS.md`):
- Run `codex` in the project directory
- Codex auto-loads `AGENTS.md` for project context
- The AGENTS.md contains instructions on how to use each role
- Use natural language prompts like "Work as vibe-backend-engineer, help me implement..."

**OpenCode** (`.opencode/commands/`):
- Run `opencode` in the project directory
- Press Ctrl+K to open the command dialog
- Select a custom command by category: `product:` or `engineering:`
- Example: select `product:vibe-project-manager` to start a PM session
- OpenCode.md is loaded as project memory automatically

**Cursor** (`.cursor/rules/`):
- Open this project in Cursor
- Rules in `.cursor/rules/` are auto-loaded
- Use `@` to mention roles: `@vibe-frontend-engineer implement this component`
- 22 rules available matching each role

---

### 3. Select a Role (Manual Mode)

Choose the corresponding role file based on your current project stage:

```
Project Initiation    →  vibe-trend-researcher + vibe-prototyper
Product Definition    →  product-manager + vibe-behavioral-designer
Technical Architecture →  vibe-architect + vibe-priority-orchestrator
Development Phase     →  vibe-frontend-engineer / vibe-backend-engineer / vibe-mobile-engineer + vibe-ai-llm-engineer
Quality Assurance     →  vibe-qa-automation-engineer + vibe-code-reviewer + vibe-security-engineer
Deployment & Ops      →  vibe-devops-engineer + vibe-database-engineer + vibe-data-engineer
Documentation         →  vibe-tech-writer
Team Expansion      →  vibe-onboarding-engineer
Feedback Iteration    →  vibe-feedback-analyst
```

---

Each role file contains a complete workflow. For example, invoking `vibe-prototyper`:

> "Please follow your workflow and help me turn this requirement into an interactive prototype. The requirement is: an AI-driven todo app where users can add tasks using natural language."

The role will automatically execute: requirement understanding → AI prototype generation → user testing design → insight analysis → prototype-to-code migration.

---

## Project Structure

```
├── autopilot-code-team/               # Project root
│   ├── LICENSE                         # MIT License
│   ├── README.md                       # English (this file)
│   ├── zh-CN/README.md                 # Chinese version
│
├── product/                             # Product-side roles (6)
│   ├── product-manager.md
│   ├── vibe-behavioral-designer.md
│   ├── vibe-feedback-analyst.md
│   ├── vibe-priority-orchestrator.md
│   ├── vibe-project-manager.md           ← Entry point (via /vibe-project-manager)
│   └── vibe-trend-researcher.md
│
├── engineering/                         # Engineering-side roles (16)
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
├── en/                                  # English translations
│   ├── product/                           # English product roles (6)
│   └── engineering/                       # English engineering roles (16)
│
├── zh-CN/                               # Chinese mirror
│   ├── product/                           # Chinese product roles (6)
│   └── engineering/                       # Chinese engineering roles (16)
│
├── .reasonix/skills/                    # Reasonix skill registry
├── .claude/agents/                      # Claude Code subagents
├── .cursor/rules/                       # Cursor rules
├── .opencode/commands/                  # OpenCode commands
├── .github/workflows/                   # GitHub Actions CI
│
├── scripts/                             # Orchestration and validation
│   ├── install.py                       # Multi-platform config generator
│   ├── validate.py                      # Role file validator
│   ├── build-site.py                    # GitHub Pages builder
│   ├── relay-parser.py                  # Dependency graph parser
│   ├── relay-runner.py                  # Parallel dispatch engine
│   ├── relay-hooks.py                   # Pre/Post validation gates
│   ├── relay-goal.py                    # Self-check loop tool
│   ├── relay-lock.py                    # Concurrent state locking
│   ├── relay-worktree.py                # Git worktree isolation
│   └── relay-memory.py                  # Auto Memory learning
│
├── examples/                            # Example projects
│   └── ai-note-assistant/                 # End-to-end example (8 stages)
│
└── docs/                                # GitHub Pages site
    ├── index.html
    └── examples/relay-plan-example.json
```

**Total: 22 agent roles (Chinese + English bilingual) — all registered as Reasonix skills**

---

## Usage Example

### Scenario: Quickly Validate a Product Hypothesis

```
Step 1: Invoke vibe-trend-researcher
  "Research 2026 AI todo app market trends, output executable trend spec"

Step 2: Invoke vibe-prototyper
  "Based on the trend spec, use v0 to generate an interactive prototype, target: complete within 2 hours"

Step 3: Invoke vibe-priority-orchestrator
  "RICE-V score the prototype validation results, decide whether to proceed to development"

Step 4: Invoke product-manager + vibe-behavioral-designer
  "Output executable product spec, including design tokens and component specifications"

Step 5: Invoke vibe-architect + vibe-frontend-engineer + vibe-backend-engineer
  "Develop according to spec, using Cursor for AI-assisted coding"

Step 6: Invoke vibe-qa-automation-engineer + vibe-code-reviewer
  "Automated testing + code review + security scanning"

Step 7: Invoke vibe-devops-engineer
  "Deploy to Vercel, configure observability"

Step 8: Invoke vibe-tech-writer
  "Synchronously update documentation, ensure code and docs are consistent"
```

---

## Role Capability Quick Reference

| Role | Core Capability | Key Toolchain | Vibe Speed |
|------|--------------|-------------|------------|
| vibe-trend-researcher | AI-driven trend research | Perplexity, Deep Research, Kimi Research | Days |
| vibe-prototyper | Hours-level prototype validation | v0, Lovable, Bolt, Cursor | Hours |
| vibe-priority-orchestrator | RICE-V dynamic priority | PostHog, Amplitude, Langfuse | Days |
| vibe-behavioral-designer | Agent experience design | System Prompt engineering, MCP tool design | Days |
| vibe-feedback-analyst | LLM semantic feedback analysis | Vector databases, RAG pipelines | Days |
| vibe-architect | MCP ecosystem architecture | Terraform, Kubernetes, Vercel | Weeks |
| vibe-ai-llm-engineer | LLM application development | LangChain, Vercel AI SDK, Langfuse | Days |
| vibe-frontend-engineer | AI-assisted frontend development | Cursor, v0 Dev Mode, Tailwind | Days |
| vibe-backend-engineer | AI-assisted backend development | Cursor, Claude Code, Supabase | Days |
| vibe-qa-automation-engineer | AI-driven quality gates | Intelligent test generation, visual regression, security scanning | Days |
| vibe-security-engineer | AI security audit | Prompt injection detection, zero-trust architecture | Days |
| vibe-devops-engineer | AI deployment & observability | Terraform, Kubernetes, Helicone | Days |
| vibe-database-engineer | Database design & optimization | Supabase, Pinecone, Qdrant | Days |
| vibe-data-engineer | Data pipelines & RAG | ETL, vector databases, data quality | Weeks |
| vibe-git-master | AI-era Git workflow | Conventional Commits, automated merging | Hours |
| vibe-onboarding-engineer | New hire Day 1 onboarding | Dev Containers, AI-assisted onboarding | Days |
| vibe-tech-writer | Living documentation & knowledge base | Docs-as-code, runnable examples | Days |
| vibe-code-reviewer | AI code review | Code quality, security vulnerabilities, performance | Hours |
| vibe-mobile-engineer | AI mobile development | Cursor, React Native, Flutter | Days |
| vibe-minimal-change-engineer | Surgical changes | Minimal change principle, impact assessment | Hours |
| product-manager | Product definition & decisions | RICE-V, executable specs | Days |

---

## Contribution Guide

We welcome all contributions! Whether it is:
- New roles
- Improving existing role prompts or workflows
- Correcting toolchains or links
- Adding usage examples
- Translations

### Before Submitting Checklist

- [ ] File uses YAML Frontmatter, containing `name`, `description`, `color` fields
- [ ] File content contains no emoji
- [ ] Contains no false role-playing ("You are Alex", "10 years experience", etc.)
- [ ] Contains all required sections (core mission, key principles, technical deliverables, workflow, success metrics, communication style)
- [ ] Contains modern AI toolchain declarations
- [ ] Contains AI observability metrics (hallucination rate, TTFT, token cost)
- [ ] Local validation passes: `python scripts/validate.py` with no errors

### How to Submit

1. Fork this repository
2. Create your branch (`git checkout -b feature/new-role`)
3. Submit changes (`git commit -am 'Add vibe-xxx role'`)
4. Push to branch (`git push origin feature/new-role`)
5. Create Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

This project is open-sourced under the [MIT License](LICENSE).

You are free to use, modify, and distribute, including for commercial purposes. Just retain the original copyright notice.

---

## Acknowledgments

This project's role design is inspired by the latest practices in the Vibe Coding ecosystem, including usage experience with Cursor, v0, Lovable, Claude Code, Kimi Code, and other AI tools, as well as cutting-edge methodologies like the MCP protocol and RICE-V scoring framework.

Special thanks to all contributors and users for their feedback, which allows this agent team to continuously evolve.

---

<div align="center">

**Build Vibe products with AI teams.**

</div>
