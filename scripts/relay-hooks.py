#!/usr/bin/env python3
# Copyright (c) 2026 Vibe Coding Agent Team Contributors
# SPDX-License-Identifier: MIT
"""
接力计划 Pre/Post Hooks 验证门禁

在每棒执行前后自动运行检查脚本，确保质量门禁不被绕过。

使用方法：
    python scripts/relay-hooks.py --pre <relay-id> --plan relay-plan.json
    python scripts/relay-hooks.py --post <relay-id> --plan relay-plan.json
    python scripts/relay-hooks.py --list-checks                     # 列出可用检查项
    python scripts/relay-hooks.py --validate <relay-id>             # 手动验证单棒
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RELAY_STATE_DIR = Path(".relay-state")


def load_plan(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_state() -> dict:
    sp = RELAY_STATE_DIR / "progress.json"
    if sp.exists():
        with open(sp, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict):
    RELAY_STATE_DIR.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = datetime.now().isoformat()
    with open(RELAY_STATE_DIR / "progress.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def find_relay(plan: dict, relay_id: str) -> dict | None:
    """在接力计划中查找指定 relay"""
    for phase in plan.get("phases", []):
        for relay in phase.get("relays", []):
            if relay["id"] == relay_id:
                return relay
    return None


def run_check(check_name: str, check_cmd: str) -> dict:
    """
    运行一个检查项。
    返回 {"name": ..., "passed": bool, "output": str, "error": str}
    """
    result = {"name": check_name, "passed": False, "output": "", "error": ""}
    try:
        r = subprocess.run(
            check_cmd,
            shell=True,
            capture_output=True,
            text=False,
            timeout=120,
        )
        # 尝试 UTF-8 解码，失败则用 GBK
        try:
            stdout = r.stdout.decode("utf-8", errors="replace") if r.stdout else ""
            stderr = r.stderr.decode("utf-8", errors="replace") if r.stderr else ""
        except UnicodeDecodeError:
            stdout = r.stdout.decode("gbk", errors="replace") if r.stdout else ""
            stderr = r.stderr.decode("gbk", errors="replace") if r.stderr else ""
        result["output"] = (stdout + "\n" + stderr).strip()
        result["passed"] = r.returncode == 0
        if not result["passed"]:
            result["error"] = f"exit code {r.returncode}"
    except subprocess.TimeoutExpired:
        result["error"] = "timeout (120s)"
    except Exception as e:
        result["error"] = str(e)
    return result


def build_pre_hooks(relay: dict) -> list[dict]:
    """从 relay 配置构建 pre-hooks 检查列表"""
    hooks = []
    checks = relay.get("pre_checks", [])

    check_map = {
        "git_clean": {
            "name": "Git 工作区干净",
            "cmd": "git status --porcelain",
            "pass_on": "empty_output",
        },
        "branch_exists": {
            "name": "Git 分支存在",
            "cmd": "git rev-parse --abbrev-ref HEAD",
            "pass_on": "non_empty",
        },
        "dependency_plan": {
            "name": "接力计划存在",
            "cmd": "test -f docs/examples/relay-plan-example.json && echo 'OK'",
            "pass_on": "contains_OK",
        },
    }

    for check in checks:
        if check in check_map:
            hooks.append(check_map[check])
        else:
            # 自定义检查：作为 shell 命令直接执行
            hooks.append({"name": check, "cmd": check, "pass_on": "exit_zero"})

    # 默认 pre-hooks
    if not hooks:
        hooks.append(check_map["git_clean"])
        hooks.append(check_map["dependency_plan"])

    return hooks


def build_post_hooks(relay: dict, plan_path: str = "") -> list[dict]:
    """从 relay 配置构建 post-hooks 检查列表"""
    hooks = []
    checks = relay.get("post_checks", [])

    check_map = {
        "tests_pass": {
            "name": "测试通过",
            "cmd": "python -m pytest --tb=short -q --no-header 2>/dev/null || echo 'SKIP: no pytest config'",
            "pass_on": "contains_OK",
        },
        "coverage": {
            "name": "测试覆盖率",
            "cmd": "python -m pytest --cov --cov-fail-under=80 2>/dev/null || echo 'SKIP: no coverage config'",
            "pass_on": "contains_OK",
        },
        "security_scan": {
            "name": "安全扫描",
            "cmd": "python scripts/validate.py 2>/dev/null && echo 'PASS' || echo 'WARN'",
            "pass_on": "contains_OK",
        },
        "lint_pass": {
            "name": "代码风格检查",
            "cmd": "python -m flake8 . --count --select=E9,F63,F7,F82 --show-source 2>/dev/null || echo 'SKIP: no flake8'",
            "pass_on": "contains_OK",
        },
        "relay_plan_valid": {
            "name": "接力计划验证",
            "cmd": f"python scripts/relay-parser.py --validate \"{plan_path}\" 2>&1 || echo 'FAIL'",
            "pass_on": "contains_PASS",
        },
    }

    for check in checks:
        if check in check_map:
            hooks.append(check_map[check])
        else:
            hooks.append({"name": check, "cmd": check, "pass_on": "exit_zero"})

    # 默认至少运行计划验证
    if not hooks:
        hooks.append(check_map["relay_plan_valid"])

    return hooks


def interpret_result(result: dict, pass_on: str) -> bool:
    """根据 pass_on 策略判断是否通过"""
    output = result.get("output", "")
    if pass_on == "empty_output":
        return output.strip() == ""
    elif pass_on == "non_empty":
        return output.strip() != ""
    elif pass_on == "contains_OK":
        return "OK" in output or "PASS" in output
    elif pass_on == "contains_PASS":
        return "PASS" in output
    elif pass_on == "exit_zero":
        return result["passed"]
    return result["passed"]


def run_hooks(hooks: list[dict]) -> list[dict]:
    """执行一系列 hook 检查"""
    results = []
    for hook in hooks:
        check_result = run_check(hook["name"], hook["cmd"])
        check_result["passed"] = interpret_result(check_result, hook.get("pass_on", "exit_zero"))
        results.append(check_result)
    return results


def print_results(results: list[dict], phase: str):
    """打印 hook 结果"""
    all_pass = all(r["passed"] for r in results)
    status = "PASS" if all_pass else "FAIL"
    print(f"[{phase}] 验证门禁: {status}")
    print(f"  检查项: {len(results)}")
    print()

    for r in results:
        icon = "PASS" if r["passed"] else "FAIL"
        print(f"  [{icon}] {r['name']}")
        if r.get("error"):
            print(f"        error: {r['error']}")
        out = r.get("output", "")
        if out and not r["passed"]:
            # 只输出前 3 行
            lines = out.split("\n")[:3]
            for line in lines:
                print(f"        {line.strip()[:100]}")
    print()
    return all_pass


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python scripts/relay-hooks.py --pre <relay-id> --plan <plan.json>")
        print("  python scripts/relay-hooks.py --post <relay-id> --plan <plan.json>")
        print("  python scripts/relay-hooks.py --list-checks")
        sys.exit(1)

    command = sys.argv[1]

    if command == "--list-checks":
        print("可用 Pre-checks:")
        print("  git_clean       - Git 工作区是否干净")
        print("  branch_exists   - Git 分支是否存在")
        print("  dependency_plan - 接力计划文件是否存在")
        print()
        print("可用 Post-checks:")
        print("  tests_pass      - 单元测试是否通过")
        print("  coverage        - 测试覆盖率 > 80%")
        print("  security_scan   - 安全扫描结果")
        print("  lint_pass       - 代码风格检查")
        print("  relay_plan_valid- 接力计划格式验证")
        print()
        print("可用 Self-check:")
        print("  relay-goal.py 驱动，使用接力计划中的 verify.checks 做自检循环")
        print()
        print("也可以使用任意 shell 命令作为自定义检查")
        sys.exit(0)

    if command == "--self-check":
        relay_id = sys.argv[2]
        plan_idx = sys.argv.index("--plan") + 1
        plan_path = sys.argv[plan_idx]
        try:
            plan = load_plan(plan_path)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[FAIL] 加载计划失败: {e}")
            sys.exit(1)
        relay = find_relay(plan, relay_id)
        if not relay:
            print(f"[FAIL] 未找到 relay: {relay_id}")
            sys.exit(1)
        verify = relay.get("verify", {})
        checks_data = verify.get("checks", [])
        max_retry = verify.get("max_retries", 3)
        if not checks_data:
            print(f"[INFO] relay {relay_id} 没有 verify checks，跳过自检")
            sys.exit(0)
        import subprocess as sp
        import tempfile, os
        # 通过临时文件传递 checks，避免 shell 转义问题
        tmp_path = os.path.join(tempfile.gettempdir(), f"relay_checks_{relay_id}.json")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(checks_data, f)
        cmd = f'python scripts/relay-goal.py --checks @{tmp_path} --max-retry {max_retry}'
        r = sp.run(cmd, shell=True, capture_output=True, timeout=300)
        # 清理临时文件
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        out = r.stdout.decode("utf-8", errors="replace") if r.stdout else ""
        # 提取最后一段 JSON（兼容嵌套 {} 结构）
        import re
        json_matches = list(re.finditer(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', out, re.DOTALL))
        if json_matches:
            last_json = json_matches[-1].group()
            result = json.loads(last_json)
            passed = result.get("status") == "pass"
            if passed:
                print(f"[PASS] 自检通过 (attempts: {result.get('attempts')})")
            else:
                print(f"[FAIL] 自检未通过: {result.get('status')} (attempts: {result.get('attempts')})")
                for res in result.get("results", []):
                    if not res["passed"]:
                        print(f"   FAIL: {res['name']} - {res.get('error', '')}")
            state = load_state()
            if "self_checks" not in state:
                state["self_checks"] = {}
            state["self_checks"][relay_id] = result
            save_state(state)
            sys.exit(0 if passed else 1)
        print(f"[FAIL] 自检执行异常")
        sys.exit(1)

    if command not in ("--pre", "--post", "--self-check"):
        print(f"[FAIL] 未知命令: {command}")
        sys.exit(1)

    if len(sys.argv) < 4:
        print("[FAIL] 缺少参数: <relay-id> --plan <plan.json>")
        sys.exit(1)

    relay_id = sys.argv[2]
    plan_idx = sys.argv.index("--plan") + 1
    if plan_idx >= len(sys.argv):
        print("[FAIL] 缺少计划文件路径")
        sys.exit(1)
    plan_path = sys.argv[plan_idx]

    try:
        plan = load_plan(plan_path)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[FAIL] 加载计划失败: {e}")
        sys.exit(1)

    relay = find_relay(plan, relay_id)
    if not relay:
        print(f"[FAIL] 未找到 relay: {relay_id}")
        sys.exit(1)

    phase_name = "Pre-hook" if command == "--pre" else "Post-hook"

    if command == "--pre":
        hooks = build_pre_hooks(relay)
    else:
        hooks = build_post_hooks(relay, plan_path)

    print(f"[INFO] 执行 {phase_name} - relay: {relay_id} ({relay.get('role', '?')})")
    print(f"[INFO] 检查项数: {len(hooks)}")
    print()

    results = run_hooks(hooks)
    all_pass = print_results(results, phase_name)

    # 保存结果到状态文件
    state = load_state()
    if "hook_results" not in state:
        state["hook_results"] = {}
    if relay_id not in state["hook_results"]:
        state["hook_results"][relay_id] = {}
    state["hook_results"][relay_id][command[2:]] = {
        "passed": all_pass,
        "results": [{"name": r["name"], "passed": r["passed"]} for r in results],
        "timestamp": datetime.now().isoformat(),
    }
    save_state(state)

    if not all_pass:
        print(f"[FAIL] {phase_name} 未通过！")
        print("[INFO] 修复问题后重新运行验证")
        print(f"[INFO] python scripts/relay-hooks.py {command} {relay_id} --plan {plan_path}")
        sys.exit(1)

    print(f"[PASS] {phase_name} 全部通过")
    sys.exit(0)


if __name__ == "__main__":
    main()
