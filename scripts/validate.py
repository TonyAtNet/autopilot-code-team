#!/usr/bin/env python3
# Copyright (c) 2026 Vibe Coding Agent Team Contributors
# SPDX-License-Identifier: MIT
"""
Vibe Coding Agent Team 文件验证脚本

验证所有 product/ 和 engineering/ 目录下的 .md 文件是否符合开源规范：
1. YAML Frontmatter 必须包含 name, description, color
2. 文件内容不得包含 emoji
3. 文件内容不得包含虚假角色扮演关键词
4. 必须包含所有必备章节
5. 建议包含 AI 可观测性指标

使用方法：
    python scripts/validate.py

返回码：
    0 = 全部通过
    1 = 存在错误
"""

import os
import re
import sys
from pathlib import Path

# 配置
REPO_ROOT = Path(__file__).parent.parent
AGENT_DIRS = [REPO_ROOT / "product", REPO_ROOT / "engineering"]

# 必备 Frontmatter 字段
REQUIRED_FRONTMATTER = ["name", "description", "color"]

# 必备章节（不区分大小写，支持部分匹配）
REQUIRED_SECTIONS = [
    "核心使命",
    "关键原则",
    "技术交付物",
    "工作流程",
    "成功指标",
    "沟通风格",
]

# 禁止的 emoji Unicode 范围（简化检测：常见 emoji 块）
EMOJI_RANGES = [
    (0x1F300, 0x1F9FF),  # 杂项符号和象形文字
    (0x2600, 0x26FF),    # 杂项符号
    (0x2700, 0x27BF),    # 装饰符号
    (0x1F600, 0x1F64F),  # 表情符号
    (0x1F680, 0x1F6FF),  # 交通和地图符号
    (0x1F900, 0x1F9FF),  # 补充符号和象形文字
]

# 虚假角色扮演关键词（正则匹配）
PERSONA_KEYWORDS = [
    r"你是\s*\w+",
    r"你叫\s*\w+",
    r"你是.{0,10}专家",
    r"你是.{0,10}工程师",
    r"你是.{0,10}资深",
    r"[\d一二三四五六七八九十]{1,2}\s*年\s*经验",
    r"[\d一二三四五六七八九十]{1,2}\s*年\s*资深",
    r"[\d一二三四五六七八九十]{1,2}\s*年\s*专家",
    r"拥有.{0,10}年经验",
    r"曾就职于",
    r"曾在\s*\w+\s*工作",
    r"前\s*(Google|Meta|Apple|Amazon|微软|阿里|腾讯|字节|百度)\s*工程师",
    r"(AI|人工智能|技术).{0,5}专家",
    r"(产品|设计|开发).{0,5}专家",
]

# AI 可观测性建议关键词（不要求必须，但建议）
OBSERVABILITY_KEYWORDS = [
    "幻觉率",
    "TTFT",
    "Token",
    "token",
    "人工接管",
    "HITL",
    "可观测性",
    "延迟",
    "成本",
]


def contains_emoji(text: str) -> bool:
    """检查文本是否包含 emoji"""
    for char in text:
        code = ord(char)
        for start, end in EMOJI_RANGES:
            if start <= code <= end:
                return True
    return False


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


def validate_file(filepath: Path) -> tuple[list[str], list[str]]:
    """验证单个文件，返回 (错误列表, 警告列表)"""
    errors = []
    warnings = []
    content = filepath.read_text(encoding="utf-8")
    
    # 1. 检查 Frontmatter
    frontmatter = extract_frontmatter(content)
    for field in REQUIRED_FRONTMATTER:
        if field not in frontmatter:
            errors.append(f"缺少 Frontmatter 字段: {field}")
    
    # 2. 检查 Emoji
    if contains_emoji(content):
        # 找出具体行
        for i, line in enumerate(content.splitlines(), 1):
            if contains_emoji(line):
                errors.append(f"第 {i} 行包含 emoji: {line.strip()[:50]}")
    
    # 3. 检查虚假角色扮演
    for pattern in PERSONA_KEYWORDS:
        matches = re.finditer(pattern, content)
        for match in matches:
            # 获取所在行号
            line_num = content[:match.start()].count("\n") + 1
            errors.append(f"第 {line_num} 行疑似角色扮演: {match.group()[:50]}")
    
    # 4. 检查必备章节
    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"缺少必备章节: {section}")
    
    # 5. 检查工具链声明
    has_toolchain = "工具链" in content
    if not has_toolchain:
        errors.append("缺少工具链声明")
    
    # 6. 建议检查：AI 可观测性（只警告，不报错）
    has_observability = any(kw in content for kw in OBSERVABILITY_KEYWORDS)
    if not has_observability:
        warnings.append("建议添加 AI 可观测性指标（幻觉率、TTFT、Token 成本等）")
    
    return errors, warnings


def main() -> int:
    """主函数，返回退出码"""
    all_errors = []
    all_warnings = []
    total_files = 0
    
    print("=" * 60)
    print("Vibe Coding Agent Team 文件验证")
    print("=" * 60)
    print()
    
    for agent_dir in AGENT_DIRS:
        if not agent_dir.exists():
            print(f"目录不存在，跳过: {agent_dir}")
            continue
        
        md_files = sorted(agent_dir.glob("*.md"))
        if not md_files:
            print(f"目录为空: {agent_dir}")
            continue
        
        for filepath in md_files:
            total_files += 1
            filename = filepath.name
            errors, warnings = validate_file(filepath)
            
            if errors or warnings:
                all_errors.append((filename, errors))
                all_warnings.append((filename, warnings))
                if errors:
                    print(f"[FAIL] {filename}")
                else:
                    print(f"[PASS] {filename}")
                for err in errors:
                    print(f"       ERR: {err}")
                for warn in warnings:
                    print(f"       WARN: {warn}")
            else:
                print(f"[PASS] {filename}")
    
    print()
    print("=" * 60)
    error_count = sum(1 for _, e in all_errors if e)
    warning_count = sum(1 for _, w in all_warnings if w)
    passed = total_files - error_count
    print(f"验证结果: {passed}/{total_files} 通过")
    
    if error_count:
        print(f"失败文件: {error_count} 个")
    if warning_count:
        print(f"警告文件: {warning_count} 个")
    
    if error_count:
        print()
        print("请根据错误信息修复后重新运行验证。")
        print("详细规范见 CONTRIBUTING.md")
        return 1
    else:
        print("全部通过！")
        if warning_count:
            print(f"（有 {warning_count} 个文件存在建议性警告，不影响提交）")
        return 0


if __name__ == "__main__":
    sys.exit(main())
