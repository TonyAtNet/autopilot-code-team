# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-06-24

### Added

- **22 AI-native roles**: 6 product roles + 16 engineering roles for Vibe Coding workflows
- **Chinese primary + English translations**: Full bilingual support (`en/` and `zh-CN/`)
- **Reasonix skill registry**: All 22 roles registered as subagent skills via `.reasonix/skills/`
- **Multi-platform support**: Auto-generated configs for Claude Code (`.claude/agents/`), OpenCode (`.opencode/commands/`), and Cursor (`.cursor/rules/`)
- **Codex CLI compatibility**: AGENTS.md auto-loaded by Codex CLI
- **Automated relay system**:
  - `relay-parser.py` — Dependency graph parser, topological sort into execution batches
  - `relay-runner.py` — Parallel dispatch engine (init → next → complete → status)
  - `relay-hooks.py` — Pre/Post validation gates with 8 built-in checks
  - `relay-goal.py` — Self-check loop (subagent retries until conditions met)
  - `relay-lock.py` — Concurrent state locking system
  - `relay-worktree.py` — Git worktree isolation for parallel relays
  - `relay-memory.py` — Auto Memory learning across relay sessions
- **Validation & build tooling**: `validate.py` (22 checks), `build-site.py` (GitHub Pages)
- **Project documentation**: README (EN + ZH-CN), AGENTS.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md
- **MIT License**

[1.0.0]: https://github.com/TonyAtNet/autopilot-code-team/releases/tag/v1.0.0
