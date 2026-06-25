#!/usr/bin/env python3
# Copyright (c) 2026 Vibe Coding Agent Team Contributors
# SPDX-License-Identifier: MIT
"""
验证循环（Goal 模式）— subagent 自检工具

subagent 在交付前调用此脚本自检，不达标准继续修改。

使用方法：
    python scripts/relay-goal.py --checks '[...]'              # 运行自检，返回 JSON
    python scripts/relay-goal.py --checks '[...]' --max-retry 3  # 带重试的自检循环
    python scripts/relay-goal.py --list-checks                   # 列出可用检查项
    python scripts/relay-goal.py --feature feature_list.json F-001  # 检查单个 feature
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def run_check(name: str, cmd: str, pass_on: str = "exit_zero") -> dict:
    """运行单个检查项，返回结果"""
    result = {"name": name, "passed": False, "output": "", "error": ""}
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=False, timeout=120)
        try:
            stdout = r.stdout.decode("utf-8", errors="replace") if r.stdout else ""
            stderr = r.stderr.decode("utf-8", errors="replace") if r.stderr else ""
        except UnicodeDecodeError:
            stdout = r.stdout.decode("gbk", errors="replace") if r.stdout else ""
            stderr = r.stderr.decode("gbk", errors="replace") if r.stderr else ""
        output = (stdout + "\n" + stderr).strip()
        result["output"] = output[:500]  # 截断输出

        if pass_on == "empty_output":
            result["passed"] = output == ""
        elif pass_on == "non_empty":
            result["passed"] = output != ""
        elif pass_on == "contains_PASS":
            result["passed"] = "PASS" in output
        elif pass_on == "contains_OK":
            result["passed"] = "OK" in output or "PASS" in output
        elif pass_on == "exit_zero":
            result["passed"] = r.returncode == 0
        else:
            result["passed"] = r.returncode == 0

        if not result["passed"] and r.returncode != 0:
            result["error"] = f"exit code {r.returncode}"
    except subprocess.TimeoutExpired:
        result["error"] = "timeout (120s)"
    except Exception as e:
        result["error"] = str(e)
    return result


def run_self_check(checks: list[dict], max_retry: int = 3) -> dict:
    """
    运行自检循环。
    每次循环运行所有检查，全部通过则返回 PASS。
    未通过则等待后重试，直到达上限。

    返回 {"status": "pass"|"degraded"|"fail", "results": [...], "attempts": N}
    """
    for attempt in range(1, max_retry + 1):
        print(f"\n[Goal] 自检循环 #{attempt}/{max_retry}")
        print(f"[Goal] 检查项: {len(checks)}")

        results = []
        all_pass = True
        for check in checks:
            name = check.get("name", "?")
            cmd = check.get("cmd", "")
            pass_on = check.get("pass_on", "exit_zero")
            r = run_check(name, cmd, pass_on)
            results.append(r)
            icon = "PASS" if r["passed"] else "FAIL"
            print(f"  [{icon}] {name}")
            if not r["passed"] and r.get("output"):
                print(f"        {r['output'][:100]}")
            if not r["passed"]:
                all_pass = False

        if all_pass:
            print(f"\n[Goal] 全部通过 (attempt #{attempt})")
            return {"status": "pass", "results": results, "attempts": attempt}

        if attempt < max_retry:
            print(f"\n[Goal] 未通过，重试中... ({attempt}/{max_retry})")
        else:
            print(f"\n[Goal] 已达最大重试次数 ({max_retry})，以 degraded 状态交付")

    return {"status": "degraded", "results": results, "attempts": max_retry}


def load_feature_list(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_feature_checks(fl: dict, feature_id: str) -> tuple[list[dict], int]:
    """从 feature_list.json 中提取 feature 的 verify checks"""
    for f in fl.get("features", []):
        if f["id"] == feature_id:
            verify = f.get("verify", {})
            if isinstance(verify, dict):
                checks = verify.get("checks", [])
                max_retry = verify.get("max_retries", 3)
            elif isinstance(verify, list):
                # 兼容旧格式：纯文本列表 -> 转为虚拟检查
                checks = [{"name": c, "cmd": f"echo '{c} - manual check'", "pass_on": "contains_OK"} for c in verify]
                max_retry = 1
            else:
                checks = []
                max_retry = 3
            return checks, max_retry
    return [], 0


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python scripts/relay-goal.py --list-checks")
        print("  python scripts/relay-goal.py --checks '[{\"name\":\"test\",\"cmd\":\"...\",\"pass_on\":\"exit_zero\"}]'")
        print("  python scripts/relay-goal.py --checks '...' --max-retry 3")
        print("  python scripts/relay-goal.py --feature feature_list.json F-001")
        sys.exit(1)

    command = sys.argv[1]

    if command == "--list-checks":
        print("可用检查项 pass_on 策略:")
        print("  exit_zero     - 命令返回码为 0 则通过（默认）")
        print("  contains_PASS - 输出包含 PASS 则通过")
        print("  contains_OK   - 输出包含 OK 或 PASS 则通过")
        print("  empty_output  - 输出为空则通过")
        print("  non_empty     - 输出非空则通过")
        sys.exit(0)

    if command == "--feature":
        if len(sys.argv) < 4:
            print("[FAIL] 用法: --feature <feature_list.json> <feature-id>")
            sys.exit(1)
        fl_path = sys.argv[2]
        feature_id = sys.argv[3]
        try:
            fl = load_feature_list(fl_path)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[FAIL] 加载 feature_list 失败: {e}")
            sys.exit(1)
        checks, max_retry = get_feature_checks(fl, feature_id)
        if not checks:
            print(f"[FAIL] feature {feature_id} 没有 verify checks")
            sys.exit(1)
        result = run_self_check(checks, max_retry)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["status"] == "pass" else 1)

    if command == "--checks":
        if len(sys.argv) < 3:
            print("[FAIL] 用法: --checks '[...]'")
            sys.exit(1)
        checks_arg = sys.argv[2]
        max_retry = 3
        if "--max-retry" in sys.argv:
            idx = sys.argv.index("--max-retry") + 1
            if idx < len(sys.argv):
                max_retry = int(sys.argv[idx])

        # 支持 @file.json 语法从文件读取
        if checks_arg.startswith("@"):
            filepath = checks_arg[1:]
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    checks_arg = f.read()
            except (FileNotFoundError, IOError) as e:
                print(f"[FAIL] 读取文件失败: {e}")
                sys.exit(1)
            # 清理临时文件
            try:
                Path(filepath).unlink()
            except OSError:
                pass

        try:
            checks = json.loads(checks_arg)
        except json.JSONDecodeError as e:
            print(f"[FAIL] checks JSON 解析失败: {e}")
            sys.exit(1)

        result = run_self_check(checks, max_retry)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["status"] == "pass" else 1)

    else:
        print(f"[FAIL] 未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
