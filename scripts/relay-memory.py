#!/usr/bin/env python3
# Copyright (c) 2026 Vibe Coding Agent Team Contributors
# SPDX-License-Identifier: MIT
"""
Auto Memory 学习机制

跨接力自动记录和回顾学习笔记，帮助 PM 优化后续接力计划。

使用方法：
    python scripts/relay-memory.py --record <relay-id> key=value [key=value ...]
    python scripts/relay-memory.py --recall <role>                    # 查询角色历史
    python scripts/relay-memory.py --summary                          # 整体学习总结
    python scripts/relay-memory.py --render                           # Markdown 报告
    python scripts/relay-memory.py --render --full                    # 完整报告含原始数据
    python scripts/relay-memory.py --clear                            # 清空记忆
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path(".relay-memory")
MEMORY_FILE = MEMORY_DIR / "memory.json"

# 默认记录字段
RECORD_FIELDS = [
    "role",           # 角色名
    "actual_effort",  # 实际用时 (hours)
    "estimated_effort", # 估算用时 (hours)
    "blockers",       # 阻塞点 (逗号分隔)
    "quality",        # 交付质量 (pass/degraded/fail)
    "toolchain",      # 使用的工具链
    "notes",          # PM 备注
]


def ensure_dir():
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def load_memory() -> dict:
    ensure_dir()
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "records": [],
        "insights": {},
    }


def save_memory(memory: dict):
    ensure_dir()
    memory["updated_at"] = datetime.now().isoformat()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def record_entry(relay_id: str, kv_pairs: list[str]) -> dict:
    """记录一条学习笔记"""
    memory = load_memory()

    entry = {
        "relay_id": relay_id,
        "timestamp": datetime.now().isoformat(),
    }

    for pair in kv_pairs:
        if "=" not in pair:
            print(f"[WARN] 忽略无效键值对: {pair} (格式: key=value)")
            continue
        key, value = pair.split("=", 1)
        key = key.strip()
        value = value.strip()

        if key == "blockers":
            entry["blockers"] = [b.strip() for b in value.split(",") if b.strip()]
        elif key in ("actual_effort", "estimated_effort"):
            try:
                entry[key] = float(value)
            except ValueError:
                entry[key] = value
        else:
            entry[key] = value

    # 自动添加 relay_id 中提取的 role
    if "role" not in entry:
        entry["role"] = relay_id

    memory["records"].append(entry)
    memory["insights"] = compute_insights(memory)
    save_memory(memory)

    return entry


def compute_insights(memory: dict) -> dict:
    """计算跨记录的学习洞察"""
    records = memory.get("records", [])
    insights = {}

    # 按角色分组
    by_role = defaultdict(list)
    for r in records:
        role = r.get("role", "unknown")
        by_role[role].append(r)

    for role, role_records in by_role.items():
        role_insight = {
            "total_runs": len(role_records),
            "estimation_bias": 0,
            "avg_actual_effort": 0,
            "common_blockers": [],
            "quality_distribution": {"pass": 0, "degraded": 0, "fail": 0},
            "recent_toolchains": [],
        }

        # 估算偏差
        effort_diffs = []
        actuals = []
        for r in role_records:
            if "actual_effort" in r and "estimated_effort" in r:
                try:
                    actual = float(r["actual_effort"])
                    estimated = float(r["estimated_effort"])
                    if estimated > 0:
                        effort_diffs.append((actual - estimated) / estimated)
                    actuals.append(actual)
                except (ValueError, TypeError):
                    pass

        if effort_diffs:
            avg_bias = sum(effort_diffs) / len(effort_diffs)
            role_insight["estimation_bias"] = round(avg_bias * 100, 1)  # 百分比
            role_insight["bias_label"] = "高估" if avg_bias > 0.1 else ("低估" if avg_bias < -0.1 else "准确")

        if actuals:
            role_insight["avg_actual_effort"] = round(sum(actuals) / len(actuals), 1)

        # 质量分布
        for r in role_records:
            q = r.get("quality", "unknown")
            if q in role_insight["quality_distribution"]:
                role_insight["quality_distribution"][q] += 1

        # 常见阻塞点
        blocker_count = defaultdict(int)
        for r in role_records:
            for b in r.get("blockers", []):
                blocker_count[b] += 1
        sorted_blockers = sorted(blocker_count.items(), key=lambda x: -x[1])
        role_insight["common_blockers"] = [
            {"blocker": b, "count": c} for b, c in sorted_blockers[:5]
        ]

        # 最近使用的工具链
        toolchains = []
        for r in role_records[-3:]:
            tc = r.get("toolchain", "")
            if tc:
                toolchains.append(tc)
        role_insight["recent_toolchains"] = toolchains

        insights[role] = role_insight

    # 全局洞察
    total_runs = len(records)
    total_effort_bias = 0
    bias_count = 0
    for role, ri in insights.items():
        if "estimation_bias" in ri:
            total_effort_bias += ri["estimation_bias"]
            bias_count += 1

    insights["_global"] = {
        "total_runs": total_runs,
        "avg_estimation_bias": round(total_effort_bias / bias_count, 1) if bias_count > 0 else 0,
        "roles_seen": list(by_role.keys()),
        "last_updated": datetime.now().isoformat(),
    }

    return insights


def recall_role(role: str) -> dict:
    """查询某个角色的历史表现"""
    memory = load_memory()
    insights = memory.get("insights", {})

    if role in insights:
        return insights[role]

    # 回退：搜索记录
    records = [r for r in memory.get("records", []) if r.get("role") == role]
    if not records:
        return {"error": f"角色 {role} 没有历史记录", "total_runs": 0}
    return {"total_runs": len(records), "records": records[-5:]}


def format_summary(memory: dict, full: bool = False) -> str:
    """格式化为可读总结"""
    insights = memory.get("insights", {})
    records = memory.get("records", [])
    lines = []

    lines.append("# Auto Memory 学习总结")
    lines.append(f"最后更新: {memory.get('updated_at', '?')[:19]}")
    lines.append(f"总接力记录: {len(records)}")
    lines.append("")

    # 全局
    global_insight = insights.get("_global", {})
    lines.append(f"## 全局指标")
    lines.append(f"- 已观察角色数: {len(global_insight.get('roles_seen', []))}")
    lines.append(f"- 平均估算偏差: {global_insight.get('avg_estimation_bias', 0)}%")
    lines.append(f"- 角色列表: {', '.join(global_insight.get('roles_seen', []))}")
    lines.append("")

    # 按角色
    lines.append(f"## 角色分析")
    for role, ri in sorted(insights.items()):
        if role == "_global":
            continue
        lines.append(f"")
        lines.append(f"### {role}")
        lines.append(f"- 运行次数: {ri.get('total_runs', 0)}")
        if "avg_actual_effort" in ri:
            lines.append(f"- 平均实际用时: {ri['avg_actual_effort']}h")
        if "estimation_bias" in ri:
            bias = ri["estimation_bias"]
            label = ri.get("bias_label", "")
            lines.append(f"- 估算偏差: {bias:+.1f}% ({label})")
        qd = ri.get("quality_distribution", {})
        if qd:
            lines.append(f"- 质量分布: pass={qd.get('pass',0)} degraded={qd.get('degraded',0)} fail={qd.get('fail',0)}")
        blockers = ri.get("common_blockers", [])
        if blockers:
            lines.append(f"- 常见阻塞点:")
            for b in blockers:
                lines.append(f"  - {b['blocker']} ({b['count']}次)")
        tcs = ri.get("recent_toolchains", [])
        if tcs:
            lines.append(f"- 近期工具链: {', '.join(tcs[-3:])}")

    if full:
        lines.append("")
        lines.append("## 原始记录")
        for r in records[-20:]:
            lines.append(f"- [{r.get('timestamp','?')[:19]}] {r.get('role','?')} (relay: {r.get('relay_id','?')})")
            if r.get("blockers"):
                lines.append(f"  阻塞: {', '.join(r['blockers'])}")
            if r.get("quality"):
                lines.append(f"  质量: {r['quality']}")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python scripts/relay-memory.py --record <relay-id> role=xxx actual_effort=4.5 estimated_effort=3 blockers='网络延迟,文档缺失' quality=pass toolchain='Cursor,Claude' notes='...'")
        print("  python scripts/relay-memory.py --recall <role>")
        print("  python scripts/relay-memory.py --summary")
        print("  python scripts/relay-memory.py --render")
        print("  python scripts/relay-memory.py --render --full")
        print("  python scripts/relay-memory.py --clear")
        sys.exit(1)

    command = sys.argv[1]

    if command == "--record":
        if len(sys.argv) < 4:
            print("[FAIL] 用法: --record <relay-id> key=value [key=value ...]")
            sys.exit(1)
        relay_id = sys.argv[2]
        kv_pairs = sys.argv[3:]
        entry = record_entry(relay_id, kv_pairs)
        print(f"[OK] 已记录: relay={relay_id} role={entry.get('role','?')}")
        print(f"     时间: {entry.get('timestamp','?')[:19]}")
        if entry.get("blockers"):
            print(f"     阻塞: {', '.join(entry['blockers'])}")
        if entry.get("quality"):
            print(f"     质量: {entry['quality']}")
        sys.exit(0)

    elif command == "--recall":
        if len(sys.argv) < 3:
            print("[FAIL] 用法: --recall <role>")
            sys.exit(1)
        role = sys.argv[2]
        result = recall_role(role)
        if "error" in result:
            print(f"[INFO] {result['error']}")
            sys.exit(0)
        print(f"角色: {role}")
        print(f"运行次数: {result.get('total_runs', 0)}")
        if "estimation_bias" in result:
            print(f"估算偏差: {result['estimation_bias']:+.1f}% ({result.get('bias_label','')})")
        if "avg_actual_effort" in result:
            print(f"平均用时: {result['avg_actual_effort']}h")
        qd = result.get("quality_distribution", {})
        if qd:
            print(f"质量: pass={qd.get('pass',0)} degraded={qd.get('degraded',0)} fail={qd.get('fail',0)}")
        for b in result.get("common_blockers", []):
            print(f"阻塞: {b['blocker']} ({b['count']}次)")
        sys.exit(0)

    elif command == "--summary":
        memory = load_memory()
        records = memory.get("records", [])
        if not records:
            print("[INFO] 暂无记忆数据")
            sys.exit(0)
        total = len(records)
        roles = set(r.get("role", "?") for r in records)
        print(f"总记录: {total}")
        print(f"角色数: {len(roles)} ({', '.join(sorted(roles))})")
        insights = memory.get("insights", {})
        global_i = insights.get("_global", {})
        if "avg_estimation_bias" in global_i:
            print(f"平均估算偏差: {global_i['avg_estimation_bias']:+.1f}%")
        sys.exit(0)

    elif command == "--render":
        memory = load_memory()
        if not memory.get("records"):
            print("[INFO] 暂无记忆数据")
            sys.exit(0)
        full = "--full" in sys.argv
        print(format_summary(memory, full))
        sys.exit(0)

    elif command == "--clear":
        memory = load_memory()
        count = len(memory.get("records", []))
        memory["records"] = []
        memory["insights"] = {}
        save_memory(memory)
        print(f"[OK] 已清空 {count} 条记忆")
        sys.exit(0)

    else:
        print(f"[FAIL] 未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
