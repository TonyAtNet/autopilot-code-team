#!/usr/bin/env python3
# Copyright (c) 2026 AutoPilot Code Team Contributors
# SPDX-License-Identifier: MIT
"""
接力计划依赖图解析器

读取接力计划 JSON，解析依赖图，输出拓扑排序后的执行批次。
同一批次内的角色可并行派发，批次间需串行。

使用方法：
    python scripts/relay-parser.py --plan relay-plan.json
    python scripts/relay-parser.py --plan relay-plan.json --graph  (输出依赖图 DOT)
    python scripts/relay-parser.py --validate relay-plan.json      (验证计划格式)
"""

import json
import sys
from collections import deque
from pathlib import Path


def load_plan(path: str) -> dict:
    """加载接力计划 JSON 文件"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_plan(plan: dict) -> list[str]:
    """验证接力计划的格式正确性，返回错误列表"""
    errors = []
    if "project" not in plan:
        errors.append("缺少 project 字段")
    if "version" not in plan:
        errors.append("缺少 version 字段")
    if "phases" not in plan or not isinstance(plan["phases"], list):
        errors.append("缺少 phases 数组")
        return errors

    all_relay_ids = set()
    for pi, phase in enumerate(plan["phases"]):
        if "id" not in phase:
            errors.append(f"phases[{pi}] 缺少 id")
        if "relays" not in phase or not isinstance(phase["relays"], list):
            errors.append(f"phases[{pi}] 缺少 relays 数组")
            continue
        for ri, relay in enumerate(phase["relays"]):
            rid = relay.get("id", f"phases[{pi}].relays[{ri}]")
            if rid in all_relay_ids:
                errors.append(f"重复的 relay id: {rid}")
            all_relay_ids.add(rid)
            if "role" not in relay:
                errors.append(f"{rid} 缺少 role 字段")
            if "dependencies" not in relay:
                errors.append(f"{rid} 缺少 dependencies 字段")
            else:
                for dep in relay["dependencies"]:
                    if dep not in all_relay_ids and dep != "":
                        # 可能在后续 phase 中，暂不报错
                        pass
            if "parallel_with" not in relay:
                errors.append(f"{rid} 缺少 parallel_with 字段")
            else:
                for pw in relay["parallel_with"]:
                    # 检查 mutual 声明
                    pass  # 完整检查在后面
    return errors


def resolve_batches(plan: dict) -> list[dict]:
    """
    将接力计划解析为执行批次列表。

    返回：
    [
        {"phase": "phase-id", "batch": 0, "relays": [...], "mode": "parallel"|"sequential"},
        ...
    ]
    """
    batches = []

    for phase in plan["phases"]:
        relays = phase.get("relays", [])
        phase_id = phase.get("id", "unknown-phase")

        # 构建依赖图（仅本阶段内的依赖）
        relay_map = {r["id"]: r for r in relays}
        phase_ids = set(relay_map.keys())
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

        # Kahn 拓扑排序
        queue = deque([rid for rid, deg in in_degree.items() if deg == 0])
        visited = set()

        batch_num = 0
        while queue:
            current_batch = list(queue)
            queue.clear()

            # 检查并分组 parallel_with
            batch_relays = []
            unassigned = set(current_batch)

            while unassigned:
                rid = unassigned.pop()
                group = {rid}
                pw_set = set(relay_map[rid].get("parallel_with", []))
                # 找出与 rid 互指 parallel 的 relay
                for other in list(unassigned):
                    if other in pw_set and rid in set(relay_map[other].get("parallel_with", [])):
                        group.add(other)
                        unassigned.discard(other)
                batch_relays.append(list(group))

            # 判断模式：如果最大的组 > 1，或者是并行标记但无依赖
            max_group_size = max(len(g) for g in batch_relays) if batch_relays else 1
            mode = "parallel" if max_group_size > 1 else "sequential"

            batches.append({
                "phase": phase_id,
                "batch": batch_num,
                "relays": current_batch,
                "groups": batch_relays,
                "mode": mode,
            })

            batch_num += 1

            # 更新 in_degree
            for rid in current_batch:
                visited.add(rid)
                for child in children.get(rid, []):
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        queue.append(child)

        # 检查未访问的节点（有环）
        unvisited = phase_ids - visited
        if unvisited:
            print(f"[WARN] Phase {phase_id} 中存在环形依赖: {unvisited}")

    return batches


def print_batches(batches: list[dict]):
    """可读性输出执行批次"""
    for b in batches:
        mode_label = "[并行]" if b["mode"] == "parallel" else "[串行]"
        print(f"\nPhase [{b['phase']}] Batch #{b['batch']}  {mode_label}")
        for group in b["groups"]:
            roles_str = ", ".join(group)
            print(f"   ├─ {roles_str}")


def print_graph(plan: dict):
    """输出 DOT 格式依赖图"""
    print("digraph relay_plan {")
    print("  rankdir=LR;")
    print('  node [shape=box, style="rounded,filled", fillcolor="#EEF2FF"];')

    for phase in plan["phases"]:
        phase_id = phase.get("id", "unknown")
        print(f'\n  subgraph cluster_{phase_id} {{')
        print(f'    label="{phase_id}";')
        print("    style=dashed;")
        print("    color=#CBD5E1;")

        relays = phase.get("relays", [])
        relay_map = {r["id"]: r for r in relays}
        all_ids = set(relay_map.keys())

        for r in relays:
            rid = r["id"]
            role = r.get("role", "?")
            print(f'    {rid} [label="{rid}\\n{role}"];')

        for r in relays:
            rid = r["id"]
            internal_deps = [d for d in r.get("dependencies", []) if d in all_ids]
            for dep in internal_deps:
                print(f"    {dep} -> {rid};")

        # parallel_with 虚线
        processed = set()
        for r in relays:
            rid = r["id"]
            for pw in r.get("parallel_with", []):
                key = tuple(sorted([rid, pw]))
                if pw in all_ids and key not in processed:
                    processed.add(key)
                    print(f'    {rid} -> {pw} [style=dashed, color="#10B981", label="parallel"];')

        print("  }")

    print("}")


def main():
    if len(sys.argv) < 3:
        print("用法:")
        print("  python scripts/relay-parser.py --plan <plan.json>")
        print("  python scripts/relay-parser.py --plan <plan.json> --graph")
        print("  python scripts/relay-parser.py --validate <plan.json>")
        sys.exit(1)

    command = sys.argv[1]
    path = sys.argv[2]

    if command == "--validate":
        try:
            plan = load_plan(path)
            errors = validate_plan(plan)
            if errors:
                print(f"[FAIL] 验证发现 {len(errors)} 个错误:")
                for e in errors:
                    print(f"   - {e}")
                sys.exit(1)
            else:
                print(f"[PASS] 接力计划 [{plan.get('project', '?')}] 格式验证通过")
                print(f"   版本: {plan.get('version', '?')}")
                print(f"   阶段数: {len(plan.get('phases', []))}")
                total_relays = sum(len(p.get("relays", [])) for p in plan.get("phases", []))
                print(f"   棒次总数: {total_relays}")
        except json.JSONDecodeError as e:
            print(f"[FAIL] JSON 解析失败: {e}")
            sys.exit(1)
        sys.exit(0)

    if command == "--plan":
        try:
            plan = load_plan(path)
            errors = validate_plan(plan)
            if errors:
                print(f"[WARN] 计划有 {len(errors)} 个警告（仍尝试解析）:")
                for e in errors:
                    print(f"   - {e}")

            if "--graph" in sys.argv:
                print_graph(plan)
            else:
                batches = resolve_batches(plan)
                print(f"\n接力计划: {plan.get('project', '?')} v{plan.get('version', '?')}")
                print(f"   阶段数: {len(plan.get('phases', []))}")
                total = sum(len(p.get("relays", 0)) for p in plan.get("phases", [])) if False else 0
                print(f"   执行批次: {len(batches)}")
                print_batches(batches)

        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
