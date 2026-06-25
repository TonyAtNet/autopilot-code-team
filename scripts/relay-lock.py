#!/usr/bin/env python3
# Copyright (c) 2026 Vibe Coding Agent Team Contributors
# SPDX-License-Identifier: MIT
"""
并发状态锁系统

管理 feature_list.json 中 feature 的并发锁，确保并发角色不会冲突。

使用方法：
    python scripts/relay-lock.py --plan relay-plan.json --status              # 查看锁状态
    python scripts/relay-lock.py --plan relay-plan.json --lock <feature-id> <owner>   # 领取 feature
    python scripts/relay-lock.py --plan relay-plan.json --unlock <feature-id>         # 释放 feature
    python scripts/relay-lock.py --plan relay-plan.json --available           # 列出可领取的 feature
    python scripts/relay-lock.py --init                                       # 初始化 feature_list.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path

RELAY_STATE_DIR = Path(".relay-state")
FEATURE_LIST_PATH = Path("feature_list.json")


def load_feature_list() -> dict:
    if FEATURE_LIST_PATH.exists():
        with open(FEATURE_LIST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"project": "", "version": "1.0.0", "features": [], "accepted": [], "blocked": []}


def save_feature_list(data: dict):
    with open(FEATURE_LIST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_state() -> dict:
    sp = RELAY_STATE_DIR / "locks.json"
    if sp.exists():
        with open(sp, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"locks": {}, "history": []}


def save_state(state: dict):
    RELAY_STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(RELAY_STATE_DIR / "locks.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def check_dependencies(fl: dict, feature_id: str) -> list[str]:
    """检查 feature 的依赖是否全部已完成"""
    for feature in fl.get("features", []):
        if feature["id"] == feature_id:
            deps = feature.get("depends_on", [])
            unsatisfied = []
            for dep_id in deps:
                dep_feature = next((f for f in fl.get("features", []) if f["id"] == dep_id), None)
                if dep_feature and dep_feature.get("status") != "done":
                    unsatisfied.append(dep_id)
            return unsatisfied
    return ["feature_not_found"]


def acquire_lock(feature_id: str, owner: str) -> dict:
    """领取一个 feature 的锁"""
    state = load_state()
    locks = state["locks"]
    fl = load_feature_list()

    # 检查 feature 是否存在
    feature = next((f for f in fl.get("features", []) if f["id"] == feature_id), None)
    if not feature:
        return {"success": False, "error": f"feature {feature_id} 不存在"}

    # 检查是否已被锁定
    if feature_id in locks:
        existing = locks[feature_id]
        if existing.get("status") == "done":
            # 已完成，自动释放
            pass
        else:
            return {"success": False, "error": f"feature {feature_id} 已被 {existing['owner']} 锁定 (since {existing.get('locked_at', '?')})"}

    # 检查依赖是否满足
    unsatisfied = check_dependencies(fl, feature_id)
    if unsatisfied and unsatisfied != ["feature_not_found"]:
        return {"success": False, "error": f"feature {feature_id} 依赖未完成: {unsatisfied}"}

    # 检查状态
    if feature.get("status") == "done":
        return {"success": False, "error": f"feature {feature_id} 已完成"}

    # 加锁
    lock_entry = {
        "owner": owner,
        "locked_at": datetime.now().isoformat(),
        "status": "locked",
    }
    locks[feature_id] = lock_entry

    # 更新 feature_list.json
    feature["lock"] = owner
    feature["claimed_at"] = datetime.now().isoformat()
    save_feature_list(fl)

    state["history"].append({
        "action": "lock",
        "feature_id": feature_id,
        "owner": owner,
        "timestamp": datetime.now().isoformat(),
    })
    save_state(state)

    return {"success": True, "feature_id": feature_id, "owner": owner}


def release_lock(feature_id: str) -> dict:
    """释放一个 feature 的锁"""
    state = load_state()
    locks = state["locks"]
    fl = load_feature_list()

    if feature_id not in locks:
        return {"success": False, "error": f"feature {feature_id} 未被锁定"}

    # 更新 feature_list.json
    feature = next((f for f in fl.get("features", []) if f["id"] == feature_id), None)
    if feature:
        feature["lock"] = None
        feature["claimed_at"] = None
        feature["status"] = "done"
    save_feature_list(fl)

    # 记录释放
    lock_entry = locks.pop(feature_id)
    state["history"].append({
        "action": "unlock",
        "feature_id": feature_id,
        "owner": lock_entry.get("owner"),
        "timestamp": datetime.now().isoformat(),
    })
    save_state(state)

    return {"success": True, "feature_id": feature_id}


def get_status() -> dict:
    """查看当前锁状态"""
    state = load_state()
    fl = load_feature_list()

    locks = state.get("locks", {})
    features_status = []

    for feature in fl.get("features", []):
        fid = feature["id"]
        status = feature.get("status", "pending")
        lock_info = locks.get(fid, {})
        deps = feature.get("depends_on", [])
        unsat_deps = check_dependencies(fl, fid)

        features_status.append({
            "id": fid,
            "description": feature.get("description", ""),
            "role": feature.get("assigned_role", ""),
            "status": status,
            "locked": fid in locks,
            "lock_owner": lock_info.get("owner"),
            "locked_at": lock_info.get("locked_at"),
            "depends_on": deps,
            "dependencies_satisfied": len(unsat_deps) == 0,
            "acceptance_criteria": feature.get("acceptance_criteria", []),
        })

    return {
        "project": fl.get("project", "?"),
        "total_features": len(features_status),
        "done": sum(1 for f in features_status if f["status"] == "done"),
        "locked": sum(1 for f in features_status if f["locked"]),
        "pending": sum(1 for f in features_status if f["status"] == "pending" and not f["locked"]),
        "features": features_status,
    }


def print_status(status: dict):
    """可读性输出锁状态"""
    print(f"项目: {status['project']}")
    print(f"总数: {status['total_features']} | 完成: {status['done']} | 锁定: {status['locked']} | 待领取: {status['pending']}")
    print()

    for f in status["features"]:
        if f["locked"]:
            icon = "LOCKED"
            extra = f" by {f['lock_owner']} at {f['locked_at'][:19]}"
        elif f["status"] == "done":
            icon = "DONE"
            extra = ""
        elif not f["dependencies_satisfied"]:
            icon = "BLOCKED"
            extra = f" (waiting: {f['depends_on']})"
        else:
            icon = "READY"
            extra = ""

        print(f"  [{icon}] {f['id']} - {f['description'][:50]}")
        print(f"         Role: {f['role']}{extra}")
        if f["acceptance_criteria"]:
            print(f"         Criteria: {', '.join(f['acceptance_criteria'][:3])}")


def get_available_features() -> list[dict]:
    """列出当前可领取的 feature"""
    state = load_state()
    fl = load_feature_list()
    locks = state.get("locks", {})

    available = []
    for feature in fl.get("features", []):
        fid = feature["id"]
        if feature.get("status") == "done":
            continue
        if fid in locks and locks[fid].get("status") != "done":
            continue
        unsatisfied = check_dependencies(fl, fid)
        if not unsatisfied or unsatisfied == ["feature_not_found"]:
            available.append(feature)
        elif all(u == "feature_not_found" for u in unsatisfied):
            available.append(feature)

    return available


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python scripts/relay-lock.py --status")
        print("  python scripts/relay-lock.py --lock <feature-id> <owner>")
        print("  python scripts/relay-lock.py --unlock <feature-id>")
        print("  python scripts/relay-lock.py --available")
        print("  python scripts/relay-lock.py --init")
        sys.exit(1)

    command = sys.argv[1]

    if command == "--init":
        fl = load_feature_list()
        if not fl.get("features"):
            # 初始化示例 feature list
            fl = {
                "project": "AI 笔记助手",
                "version": "1.0.0",
                "features": [
                    {
                        "id": "F-001",
                        "description": "用户注册功能",
                        "assigned_role": "vibe-backend-engineer",
                        "depends_on": [],
                        "status": "pending",
                        "lock": None,
                        "claimed_at": None,
                        "acceptance_criteria": ["POST /api/register 返回 201", "密码哈希存储"]
                    },
                    {
                        "id": "F-002",
                        "description": "用户登录功能",
                        "assigned_role": "vibe-backend-engineer",
                        "depends_on": ["F-001"],
                        "status": "pending",
                        "lock": None,
                        "claimed_at": None,
                        "acceptance_criteria": ["POST /api/login 返回 JWT", "Token 过期时间 24h"]
                    },
                    {
                        "id": "F-003",
                        "description": "笔记 CRUD API",
                        "assigned_role": "vibe-backend-engineer",
                        "depends_on": ["F-002"],
                        "status": "pending",
                        "lock": None,
                        "claimed_at": None,
                        "acceptance_criteria": ["完整的笔记 CRUD", "向量嵌入自动生成"]
                    },
                    {
                        "id": "F-004",
                        "description": "笔记列表页面",
                        "assigned_role": "vibe-frontend-engineer",
                        "depends_on": ["F-003"],
                        "status": "pending",
                        "lock": None,
                        "claimed_at": None,
                        "acceptance_criteria": ["笔记列表渲染", "搜索功能"]
                    },
                    {
                        "id": "F-005",
                        "description": "AI 摘要生成集成",
                        "assigned_role": "vibe-ai-llm-engineer",
                        "depends_on": ["F-003", "F-004"],
                        "status": "pending",
                        "lock": None,
                        "claimed_at": None,
                        "acceptance_criteria": ["摘要生成 API", "流式输出"]
                    },
                ],
                "accepted": [],
                "blocked": [],
            }
            save_feature_list(fl)
            print(f"[OK] feature_list.json 已初始化: {len(fl['features'])} 个 feature")
        else:
            print(f"[INFO] feature_list.json 已存在: {len(fl.get('features', []))} 个 feature")
        sys.exit(0)

    elif command == "--status":
        status = get_status()
        if "--json" in sys.argv:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print_status(status)
        sys.exit(0)

    elif command == "--available":
        available = get_available_features()
        if not available:
            print("[INFO] 当前无可领取的 feature")
        else:
            print(f"可领取的 feature ({len(available)}):")
            for f in available:
                deps = f.get("depends_on", [])
                dep_str = f" (depends: {deps})" if deps else ""
                print(f"  {f['id']} - {f['description']}{dep_str}")
        sys.exit(0)

    elif command == "--lock":
        if len(sys.argv) < 4:
            print("[FAIL] 用法: --lock <feature-id> <owner>")
            sys.exit(1)
        feature_id = sys.argv[2]
        owner = sys.argv[3]
        result = acquire_lock(feature_id, owner)
        if result["success"]:
            print(f"[OK] {result['owner']} 已领取 {result['feature_id']}")
        else:
            print(f"[FAIL] {result['error']}")
            sys.exit(1)
        sys.exit(0)

    elif command == "--unlock":
        if len(sys.argv) < 3:
            print("[FAIL] 用法: --unlock <feature-id>")
            sys.exit(1)
        feature_id = sys.argv[2]
        result = release_lock(feature_id)
        if result["success"]:
            print(f"[OK] {result['feature_id']} 已释放")
        else:
            print(f"[FAIL] {result['error']}")
            sys.exit(1)
        sys.exit(0)

    else:
        print(f"[FAIL] 未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
