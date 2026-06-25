#!/usr/bin/env python3
# Copyright (c) 2026 Vibe Coding Agent Team Contributors
# SPDX-License-Identifier: MIT
"""
Vibe Coding Agent Team — 全平台安装配置生成器

从 product/*.md 和 engineering/*.md 自动生成各 Agent 工具的配置文件。

使用方法：
    python scripts/install.py --all          # 生成所有平台配置
    python scripts/install.py --claude       # 仅 Claude Code (.claude/agents/)
    python scripts/install.py --opencode     # 仅 OpenCode (.opencode/commands/)  
    python scripts/install.py --cursor       # 仅 Cursor (.cursor/rules/)
    python scripts/install.py --entrypoints  # 仅入口文件 (CLAUDE.md, OpenCode.md)
    python scripts/install.py --status       # 查看当前配置状态
    python scripts/install.py --help         # 帮助
"""

import os
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
AGENT_DIRS = {
    "product": REPO_ROOT / "product",
    "engineering": REPO_ROOT / "engineering",
}


def extract_frontmatter(content: str) -> dict:
    """提取 YAML Frontmatter"""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    frontmatter = content[3:end].strip()
    result = {}
    for line in frontmatter.splitlines():
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def strip_frontmatter(content: str) -> str:
    """去掉 YAML Frontmatter 和第一个 # 标题"""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:].strip()
    # 去掉第一行 # 标题（如果有）
    lines = content.split("\n")
    if lines and lines[0].startswith("# "):
        content = "\n".join(lines[1:]).strip()
    return content


def collect_roles() -> list[dict]:
    """收集所有角色文件"""
    roles = []
    for category, directory in AGENT_DIRS.items():
        if not directory.exists():
            continue
        for filepath in sorted(directory.glob("*.md")):
            content = filepath.read_text(encoding="utf-8")
            fm = extract_frontmatter(content)
            body = strip_frontmatter(content)
            name = fm.get("name", filepath.stem)
            roles.append({
                "name": name,
                "description": fm.get("description", ""),
                "color": fm.get("color", "slate"),
                "category": category,
                "filename": filepath.name,
                "source_path": str(filepath),
                "body": body,
            })
    return roles


def generate_claude_agents(roles: list[dict], output_dir: Path):
    """生成 Claude Code subagent 定义到 .claude/agents/"""
    output_dir.mkdir(parents=True, exist_ok=True)

    for role in roles:
        name = role["name"]
        desc = role["description"]
        body = role["body"]

        # 提取前 200 字作为 subagent 行为指引
        short_body = "\n".join(body.split("\n")[:40])

        subagent_content = f"""---
name: {name}
description: {desc[:120]}
model: sonnet
tools: Read, Glob, Grep, Bash, Write, Edit
---

# {name}

{short_body}
"""
        filepath = output_dir / f"{name}.md"
        filepath.write_text(subagent_content.strip() + "\n", encoding="utf-8")
        print(f"  [OK] .claude/agents/{name}.md")

    print(f"  -> 共生成 {len(roles)} 个 Claude Code subagent")


def generate_opencode_commands(roles: list[dict], output_dir: Path):
    """生成 OpenCode 自定义命令到 .opencode/commands/"""
    # OpenCode 命令按类别分组
    categories = {
        "product": [],
        "engineering": [],
    }
    for role in roles:
        cat = role["category"]
        if cat in categories:
            categories[cat].append(role)

    for cat, cat_roles in categories.items():
        cat_dir = output_dir / cat
        cat_dir.mkdir(parents=True, exist_ok=True)

        for role in cat_roles:
            name = role["name"]
            desc = role["description"]
            body = role["body"]

            # 提取核心工作流程部分
            workflow_section = ""
            if "## 工作流程" in body:
                wf = body.split("## 工作流程")[1]
                if "##" in wf:
                    wf = wf.split("##")[0]
                workflow_section = wf.strip()[:500]

            command_content = f"""# {name}
# {desc[:100]}

你正在以 {name} 的身份运作。

{body[:1500]}

## 工作流程
{workflow_section}

请按照工作流程执行。
"""
            filepath = cat_dir / f"{name}.md"
            filepath.write_text(command_content.strip() + "\n", encoding="utf-8")
            print(f"  [OK] .opencode/commands/{cat}/{name}.md")

    total = sum(len(v) for v in categories.values())
    print(f"  -> 共生成 {total} 个 OpenCode 命令")


def generate_cursor_rules(roles: list[dict], output_dir: Path):
    """生成 Cursor 规则到 .cursor/rules/"""
    output_dir.mkdir(parents=True, exist_ok=True)

    for role in roles:
        name = role["name"]
        desc = role["description"]
        body = role["body"]

        # 提取核心使命和工作流程
        mission = ""
        if "## 核心使命" in body:
            mission = body.split("## 核心使命")[1]
            if "##" in mission:
                mission = mission.split("##")[0]

        workflow = ""
        if "## 工作流程" in body:
            wf = body.split("## 工作流程")[1]
            if "##" in wf:
                wf = wf.split("##")[0]
            workflow = wf.strip()[:500]

        principles = ""
        if "## 关键原则" in body:
            pr = body.split("## 关键原则")[1]
            if "##" in pr:
                pr = pr.split("##")[0]
            principles = pr.strip()[:500]

        rule_content = f"""---
description: {desc[:120]}
globs: **/*
---

# {name}

## 核心使命
{mission.strip()[:500]}

## 关键原则
{principles}

## 工作流程
{workflow}

请按照以上角色定义和工作流程执行任务。
"""
        filepath = output_dir / f"{name}.mdc"
        filepath.write_text(rule_content.strip() + "\n", encoding="utf-8")
        print(f"  [OK] .cursor/rules/{name}.mdc")

    print(f"  -> 共生成 {len(roles)} 个 Cursor 规则")


def generate_entrypoints(roles: list[dict]):
    """生成入口文件 CLAUDE.md 和 OpenCode.md"""
    # CLAUDE.md — Claude Code 入口
    claude_content = """# Vibe Coding Agent Team

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
"""
    (REPO_ROOT / "CLAUDE.md").write_text(claude_content.strip() + "\n", encoding="utf-8")
    print("  [OK] CLAUDE.md")

    # OpenCode.md — OpenCode 项目记忆文件
    opencode_content = """# Vibe Coding Agent Team

This repository contains 22 AI-native agent role configurations for Vibe Coding.

## Role Categories

### Product (6 roles)
- vibe-project-manager — 项目经理，唯一入口
- vibe-trend-researcher — 趋势研究员
- product-manager — 产品经理
- vibe-behavioral-designer — 体验设计师
- vibe-feedback-analyst — 反馈分析师
- vibe-priority-orchestrator — 优先级调度器

### Engineering (16 roles)
- vibe-architect — 系统架构师
- vibe-prototyper — 原型工程师
- vibe-frontend-engineer — 前端工程师
- vibe-backend-engineer — 后端工程师
- vibe-ai-llm-engineer — LLM 工程师
- vibe-mobile-engineer — 移动端工程师
- vibe-git-master — Git 大师
- vibe-code-reviewer — 代码审查员
- vibe-minimal-change-engineer — 最小变更工程师
- vibe-qa-automation-engineer — QA 自动化工程师
- vibe-security-engineer — 安全工程师
- vibe-devops-engineer — DevOps 工程师
- vibe-database-engineer — 数据库工程师
- vibe-data-engineer — 数据工程师
- vibe-onboarding-engineer — 入职工程师
- vibe-tech-writer — 技术文档工程师

## Usage

Use Ctrl+K in OpenCode to access custom commands in `.opencode/commands/`.
Select a command by category (product/engineering) to invoke the corresponding role.
"""
    (REPO_ROOT / "OpenCode.md").write_text(opencode_content.strip() + "\n", encoding="utf-8")
    print("  [OK] OpenCode.md")


def print_status(roles: list[dict]):
    """查看当前各平台配置状态"""
    print(f"源角色文件: {len(roles)} 个")
    print()

    checks = [
        ("Claude Code", ".claude/agents/", ".claude/agents"),
        ("OpenCode", ".opencode/commands/", ".opencode/commands"),
        ("Cursor", ".cursor/rules/", ".cursor/rules"),
        ("CLAUDE.md 入口", "CLAUDE.md", "CLAUDE.md"),
        ("OpenCode.md 入口", "OpenCode.md", "OpenCode.md"),
    ]

    for name, label, path in checks:
        p = REPO_ROOT / path
        exists = p.exists()
        count = 0
        if p.is_dir():
            count = len(list(p.rglob("*")))
        elif p.is_file():
            count = 1
        status = "[OK]" if exists else "[--]"
        print(f"  {status} {label} ({'存在' if exists else '缺失'})", end="")
        if count:
            print(f" — {count} 个文件")
        else:
            print()


def clean_generate(func, roles, output_dir, label):
    """安全生成：先清理旧目录再生成"""
    if output_dir.exists():
        shutil.rmtree(output_dir)
    func(roles, output_dir)


def _mirror_to_zh_cn():
    """将 root 的中文角色镜像到 zh-CN/ 目录"""
    zh_cn_root = REPO_ROOT / "zh-CN"
    zh_cn_root.mkdir(parents=True, exist_ok=True)

    for category in ["product", "engineering"]:
        src_dir = REPO_ROOT / category
        dst_dir = zh_cn_root / category
        dst_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for f in sorted(src_dir.glob("*.md")):
            content = f.read_text(encoding="utf-8")
            dst_file = dst_dir / f.name
            dst_file.write_text(content, encoding="utf-8")
            count += 1
            print(f"  [OK] zh-CN/{category}/{f.name}")

    print(f"  -> 共镜像 {count} 个文件到 zh-CN/")


def _generate_english_configs():
    """为英文版角色生成各平台配置（使用 en/ 目录）"""
    en_base = REPO_ROOT / "en"
    if not en_base.exists():
        print("  [SKIP] en/ 目录不存在")
        return

    # 加载英文角色
    en_roles = []
    for category in ["product", "engineering"]:
        cat_dir = en_base / category
        if not cat_dir.exists():
            continue
        for filepath in sorted(cat_dir.glob("*.md")):
            content = filepath.read_text(encoding="utf-8")
            fm = extract_frontmatter(content)
            body = strip_frontmatter(content)
            name = fm.get("name", filepath.stem)
            en_roles.append({
                "name": name,
                "description": fm.get("description", ""),
                "category": category,
                "filename": filepath.name,
                "body": body,
            })

    if not en_roles:
        print("  [SKIP] 未找到英文角色")
        return

    print(f"  已加载 {len(en_roles)} 个英文角色")

    # Claude Code agents (English)
    en_agent_dir = REPO_ROOT / ".claude" / "agents" / "en"
    generate_claude_agents(en_roles, en_agent_dir)

    # OpenCode commands (English)
    en_cmd_dir = REPO_ROOT / ".opencode" / "commands" / "en"
    generate_opencode_commands(en_roles, en_cmd_dir)

    # Cursor rules (English)
    en_rule_dir = REPO_ROOT / ".cursor" / "rules" / "en"
    generate_cursor_rules(en_roles, en_rule_dir)


def main():
    if len(sys.argv) < 2 or "--help" in sys.argv:
        print("Vibe Coding Agent Team — 全平台安装配置生成器")
        print()
        print("用法:")
        print("  python scripts/install.py --all          生成所有平台配置（含中文镜像）")
        print("  python scripts/install.py --claude       仅 Claude Code")
        print("  python scripts/install.py --opencode     仅 OpenCode")
        print("  python scripts/install.py --cursor       仅 Cursor")
        print("  python scripts/install.py --entrypoints  仅入口文件")
        print("  python scripts/install.py --zh-cn        生成 zh-CN 中文镜像")
        print("  python scripts/install.py --english      生成英文版平台配置")
        print("  python scripts/install.py --status       查看状态")
        sys.exit(0)

    roles = collect_roles()
    print(f"已加载 {len(roles)} 个角色\n")

    if "--status" in sys.argv:
        print_status(roles)
        sys.exit(0)

    do_all = "--all" in sys.argv

    if do_all or "--claude" in sys.argv:
        print("生成 Claude Code 配置...")
        clean_generate(generate_claude_agents, roles, REPO_ROOT / ".claude" / "agents", "Claude Code")
        print()

    if do_all or "--opencode" in sys.argv:
        print("生成 OpenCode 配置...")
        clean_generate(generate_opencode_commands, roles, REPO_ROOT / ".opencode" / "commands", "OpenCode")
        print()

    if do_all or "--cursor" in sys.argv:
        print("生成 Cursor 配置...")
        clean_generate(generate_cursor_rules, roles, REPO_ROOT / ".cursor" / "rules", "Cursor")
        print()

    if do_all or "--entrypoints" in sys.argv:
        print("生成入口文件...")
        generate_entrypoints(roles)
        print()

    if do_all or "--zh-cn" in sys.argv:
        print("生成 zh-CN 中文镜像...")
        _mirror_to_zh_cn()
        print()

    if do_all or "--english" in sys.argv:
        print("生成英文版平台配置...")
        _generate_english_configs()
        print()

    # 更新 .gitignore — 确保生成的文件不被忽略
    gitignore_path = REPO_ROOT / ".gitignore"
    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding="utf-8")
        # 确保 .claude/agents 和 .cursor/rules 不被忽略
        for pattern in [".claude/", ".cursor/", ".opencode/"]:
            if pattern in content:
                # 从忽略列表中移除
                content = content.replace(pattern + "\n", "")
                content = content.replace("/" + pattern + "\n", "")
        gitignore_path.write_text(content, encoding="utf-8")

    print("完成！")
    print(f"\n提示: 运行 python scripts/install.py --status 查看配置状态")


if __name__ == "__main__":
    main()
