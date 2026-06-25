#!/usr/bin/env python3
# Copyright (c) 2026 AutoPilot Code Team Contributors
# SPDX-License-Identifier: MIT
"""
接力计划并行派发引擎

读取接力计划 JSON，按序执行各批次。PM (Reasonix) 通过此脚本协调派发和状态追踪。

使用方法：
    python scripts/relay-runner.py --plan relay-plan.json          # 解析计划，输出执行指令
    python scripts/relay-runner.py --plan relay-plan.json --exec   # 执行模式
    python scripts/relay-runner.py --status                        # 查看当前进度
    python scripts/relay-runner.py --status --json                 # JSON 格式进度
"""

import json
import os
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path

RELAY_STATE_DIR = Path(".relay-state")


def load_plan(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_state_dir():
    RELAY_STATE_DIR.mkdir(parents=True, exist_ok=True)


def state_path() -> Path:
    return RELAY_STATE_DIR / "progress.json"


def load_state() -> dict:
    ensure_state_dir()
    sp = state_path()
    if sp.exists():
        with open(sp, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "project": "",
        "version": "",
        "phases": [],
        "completed_batches": [],
        "current_batch": None,
        "relay_results": {},
        "started_at": None,
        "updated_at": None,
    }


def save_state(state: dict):
    ensure_state_dir()
    state["updated_at"] = datetime.now().isoformat()
    with open(state_path(), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def resolve_batches(plan: dict) -> list[dict]:
    """解析依赖图，返回执行批次列表（同 relay-parser.py 逻辑）"""
    batches = []
    all_ids = set()

    for phase in plan["phases"]:
        relays = phase.get("relays", [])
        phase_id = phase.get("id", "unknown-phase")
        relay_map = {r["id"]: r for r in relays}
        phase_ids = set(relay_map.keys())  # 仅本阶段的 relay ID

        # Kahn 拓扑排序（仅本阶段内的依赖）
        in_degree = {}
        children = {}
        for r in relays:
            rid = r["id"]
            internal_deps = [d for d in r.get("dependencies", []) if d in phase_ids]
            in_degree[rid] = len(internal_deps)
            children[rid] = []

        for r in relays:
            rid = r["id"]
            internal_deps = [d for d in r.get("dependencies", []) if d in phase_ids]
            for dep in internal_deps:
                children.setdefault(dep, []).append(rid)

        queue = deque([rid for rid, deg in in_degree.items() if deg == 0])
        batch_num = 0
        while queue:
            current_batch = list(queue)
            queue.clear()

            # 分组 parallel_with
            unassigned = set(current_batch)
            groups = []
            while unassigned:
                rid = unassigned.pop()
                group = {rid}
                pw_set = set(relay_map[rid].get("parallel_with", []))
                for other in list(unassigned):
                    if other in pw_set and rid in set(relay_map[other].get("parallel_with", [])):
                        group.add(other)
                        unassigned.discard(other)
                groups.append(list(group))

            max_group_size = max(len(g) for g in groups) if groups else 1
            mode = "parallel" if max_group_size > 1 else "sequential"

            batch_relays = []
            for group in groups:
                for rid in group:
                    batch_relays.append(relay_map[rid])

            batches.append({
                "phase": phase_id,
                "batch": batch_num,
                "relays": batch_relays,
                "groups": groups,
                "mode": mode,
            })

            batch_num += 1
            for rid in current_batch:
                for child in children.get(rid, []):
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        queue.append(child)

    return batches


def get_next_batch(state: dict, batches: list[dict]) -> dict | None:
    """获取下一个需要执行的批次"""
    completed_ids = set(state.get("completed_batches", []))
    for b in batches:
        key = f"{b['phase']}:{b['batch']}"
        if key not in completed_ids:
            return b
    return None


def generate_instructions(plan: dict) -> list[dict]:
    """生成所有批次的执行指令（PM 可读格式）"""
    batches = resolve_batches(plan)
    instructions = []

    for b in batches:
        mode_label = "并行执行" if b["mode"] == "parallel" else "串行执行"
        inst = {
            "phase": b["phase"],
            "batch": b["batch"],
            "mode": b["mode"],
            "mode_label": mode_label,
            "groups": [],
        }

        for group in b["groups"]:
            group_inst = {
                "relays": [],
                "dispatch_type": "parallel" if len(group) > 1 else "serial",
            }
            for rid in group:
                relay = next(r for r in plan["phases"][_find_phase_idx(plan, b["phase"])]["relays"] if r["id"] == rid)
                group_inst["relays"].append({
                    "id": rid,
                    "role": relay.get("role", "?"),
                    "description": relay.get("description", ""),
                    "context": relay.get("context", {}),
                    "acceptance_criteria": relay.get("acceptance_criteria", []),
                    "pre_checks": relay.get("pre_checks", []),
                    "post_checks": relay.get("post_checks", []),
                })
            inst["groups"].append(group_inst)

        instructions.append(inst)

    return instructions


def _find_phase_idx(plan, phase_id):
    for i, p in enumerate(plan["phases"]):
        if p["id"] == phase_id:
            return i
    return -1


def format_instructions_for_pm(instructions: list[dict]) -> str:
    """将指令格式化为 PM 可读的文本"""
    lines = []
    lines.append("=" * 60)
    lines.append("接力计划执行指令")
    lines.append("=" * 60)
    lines.append(f"总批次: {len(instructions)}")
    lines.append("")

    for inst in instructions:
        phase_name = f"[{inst['phase']}]"
        lines.append(f"\n--- 阶段 {phase_name}  Batch #{inst['batch']} --- {inst['mode_label']} ---")

        for gi, group in enumerate(inst["groups"]):
            if group["dispatch_type"] == "parallel":
                lines.append(f"\n  [并行组 #{gi + 1}] 同时派发以下角色:")
            else:
                lines.append(f"\n  [单棒]")

            for relay in group["relays"]:
                lines.append(f"    run_skill({relay['role']})")
                lines.append(f"      描述: {relay['description']}")
                ctx = relay.get("context", {})
                if ctx:
                    bg = ctx.get("background", "")
                    if bg:
                        lines.append(f"      背景: {bg[:80]}...")
                    qs = ctx.get("questions", [])
                    if qs:
                        lines.append(f"      问题: {', '.join(qs[:3])}")
                ac = relay.get("acceptance_criteria", [])
                if ac:
                    lines.append(f"      验收: {', '.join(ac[:3])}")
                pre = relay.get("pre_checks", [])
                if pre:
                    lines.append(f"      Pre-checks: {', '.join(pre)}")
                post = relay.get("post_checks", [])
                if post:
                    lines.append(f"      Post-checks: {', '.join(post)}")

        if inst["mode"] == "parallel":
            lines.append(f"\n  [并行批次] 等待所有角色完成后，PM 统一压缩上下文进入下一批")
        else:
            lines.append(f"\n  [串行批次] 逐棒执行，每棒完成后压缩上下文传递")

    lines.append("\n" + "=" * 60)
    lines.append("指令结束")
    return "\n".join(lines)


def check_status(state: dict, plan: dict | None = None) -> str:
    """查看当前执行进度"""
    lines = []
    project = state.get("project", "?")
    completed = state.get("completed_batches", [])
    relay_results = state.get("relay_results", {})
    current = state.get("current_batch")

    lines.append(f"项目: {project}")
    lines.append(f"已完成批次: {len(completed)}")
    if current:
        lines.append(f"当前批次: Phase {current.get('phase')} Batch #{current.get('batch')}")

    if plan:
        batches = resolve_batches(plan)
        total = len(batches)
        lines.append(f"总批次: {total}")
        lines.append(f"进度: {len(completed)}/{total}")

        for b in batches:
            key = f"{b['phase']}:{b['batch']}"
            status = "DONE" if key in completed else ("RUNNING" if current and key == f"{current['phase']}:{current['batch']}" else "PENDING")
            mode = "PAR" if b["mode"] == "parallel" else "SEQ"
            roles = ", ".join(r.get("role", "?") for r in b["relays"])
            lines.append(f"  [{status}] Batch #{b['batch']} {mode} [{roles}]")

    if relay_results:
        lines.append(f"\n已完成棒次结果:")
        for rid, result in relay_results.items():
            status = result.get("status", "?")
            lines.append(f"  {rid}: {status} | 交付物: {result.get('artifacts', 'N/A')}")

    return "\n".join(lines)


def init_state(plan: dict):
    """从接力计划初始化状态文件"""
    state = {
        "project": plan.get("project", ""),
        "version": plan.get("version", ""),
        "phases": [p.get("id") for p in plan.get("phases", [])],
        "completed_batches": [],
        "current_batch": None,
        "relay_results": {},
        "started_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    save_state(state)
    return state


def mark_batch_completed(state: dict, phase: str, batch: int):
    """标记批次完成"""
    key = f"{phase}:{batch}"
    if key not in state["completed_batches"]:
        state["completed_batches"].append(key)
    state["current_batch"] = None
    save_state(state)


def mark_relay_completed(state: dict, relay_id: str, status: str, artifacts: list = None):
    """标记单棒完成"""
    state["relay_results"][relay_id] = {
        "status": status,
        "artifacts": artifacts or [],
        "completed_at": datetime.now().isoformat(),
    }
    save_state(state)


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python scripts/relay-runner.py --plan <plan.json>            # 生成执行指令")
        print("  python scripts/relay-runner.py --plan <plan.json> --init     # 初始化状态")
        print("  python scripts/relay-runner.py --plan <plan.json> --next     # 获取下一个批次指令")
        print("  python scripts/relay-runner.py --plan <plan.json> --complete <phase:batch>  # 标记批次完成")
        print("  python scripts/relay-runner.py --status                      # 查看进度")
        print("  python scripts/relay-runner.py --status --json               # JSON 格式进度")
        sys.exit(1)

    command = sys.argv[1]

    if command in ("--plan",):
        if len(sys.argv) < 3:
            print("[FAIL] 缺少计划文件路径")
            sys.exit(1)
        plan_path = sys.argv[2]

        try:
            plan = load_plan(plan_path)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[FAIL] 加载计划失败: {e}")
            sys.exit(1)

        if "--init" in sys.argv:
            state = init_state(plan)
            print(f"[OK] 状态已初始化: {state_path()}")
            print(f"  项目: {plan.get('project', '?')}")
            sys.exit(0)

        if "--next" in sys.argv:
            state = load_state()
            if not state.get("project"):
                print("[FAIL] 状态未初始化，请先 --init")
                sys.exit(1)
            batches = resolve_batches(plan)
            next_batch = get_next_batch(state, batches)
            if next_batch:
                key = f"{next_batch['phase']}:{next_batch['batch']}"
                state["current_batch"] = {"phase": next_batch["phase"], "batch": next_batch["batch"]}
                save_state(state)
                # 输出 JSON 格式的指令
                instructions = generate_instructions(plan)
                for inst in instructions:
                    if inst["phase"] == next_batch["phase"] and inst["batch"] == next_batch["batch"]:
                        print(json.dumps(inst, ensure_ascii=False, indent=2))
                        break
            else:
                print("[DONE] 所有批次已完成！")
            sys.exit(0)

        if "--complete" in sys.argv:
            idx = sys.argv.index("--complete") + 1
            if idx >= len(sys.argv):
                print("[FAIL] 缺少批次标识（格式: phase:batch）")
                sys.exit(1)
            batch_key = sys.argv[idx]
            parts = batch_key.split(":")
            if len(parts) != 2:
                print("[FAIL] 格式错误，应为 phase:batch")
                sys.exit(1)
            state = load_state()
            mark_batch_completed(state, parts[0], int(parts[1]))
            print(f"[OK] 批次 {batch_key} 已完成")
            # 检查是否全部完成
            batches = resolve_batches(plan)
            next_batch = get_next_batch(state, batches)
            if not next_batch:
                print("[DONE] 所有批次执行完成！")
            sys.exit(0)

        # 默认：输出执行指令
        instructions = generate_instructions(plan)
        print(format_instructions_for_pm(instructions))

    elif command == "--status":
        state = load_state()
        if not state.get("project"):
            print("[INFO] 无活跃接力计划")
            sys.exit(0)

        if "--json" in sys.argv:
            print(json.dumps(state, ensure_ascii=False, indent=2))
        else:
            # 尝试加载计划文件显示进度
            plan = None
            possible_plans = list(Path(".").glob("relay-plan*.json")) + list(Path(".").glob("docs/examples/relay-plan*.json"))
            if possible_plans:
                try:
                    plan = load_plan(str(possible_plans[0]))
                except Exception:
                    pass
            print(check_status(state, plan))


if __name__ == "__main__":
    main()
