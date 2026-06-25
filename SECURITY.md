# Security Policy

## Supported Versions

| Version | Supported          |
|---------|-------------------|
| 1.x     | ✅ Active support |

## Reporting a Vulnerability

This project provides **AI agent role configurations** and **orchestration scripts**. It does not handle user data, process network requests, or store credentials by design.

However, if you discover a security concern:

1. **Do not** open a public GitHub Issue
2. Submit a report via email or open a [security advisory](https://github.com/TonyAtNet/autopilot-code-team/security/advisories)
3. Include:
   - Description of the issue
   - Steps to reproduce (if applicable)
   - Suggested mitigation

We will acknowledge receipt within 48 hours and provide an initial assessment within 5 business days.

## Scope

Issues we consider in scope:
- Prompt injection in role definition files
- Unsafe tool/command suggestions in agent workflows
- Credential or token leakage risk in templates

Issues out of scope:
- General AI model hallucinations or misbehavior
- Third-party toolchain vulnerabilities (Cursor, Claude Code, etc.)

## Preferred Languages

Chinese (中文) or English
