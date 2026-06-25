# AutoPilot Code Team

See @AGENTS.md for full project instructions and role definitions.

## Quick Start

This project contains 22 AI-native agent roles. Use them with Claude Code through subagents:

- `.claude/agents/` contains subagent definitions for all 22 roles
- The project manager (`vibe-project-manager`) is the single entry point

```bash
# In Claude Code, use subagents:
# Claude automatically delegates to the right subagent based on your task
```

For manual subagent invocation, refer to AGENTS.md.
