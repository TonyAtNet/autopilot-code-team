#!/usr/bin/env python3
# Copyright (c) 2026 AutoPilot Code Team Contributors
# SPDX-License-Identifier: MIT
"""
Git Worktree 隔离管理

为并发接力中的每棒创建独立 worktree，避免文件冲突。

使用方法：
    python scripts/relay-worktree.py --create <name>           # 创建 worktree
    python scripts/relay-worktree.py --list                    # 列出活跃 worktree
    python scripts/relay-worktree.py --merge <name>            # 合并回主分支
    python scripts/relay-worktree.py --remove <name>           # 清理 worktree
    python scripts/relay-worktree.py --merge-all               # 合并所有活跃 worktree
    python scripts/relay-worktree.py --cleanup-all             # 清理所有 worktree
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

WORKTREE_DIR = Path(".worktrees")


def git(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    """运行 git 命令"""
    return subprocess.run(
        ["git"] + list(args),
        capture_output=True,
        text=True,
        cwd=cwd or os.getcwd(),
        timeout=60,
    )


def get_main_branch() -> str:
    """获取主分支名（main/master）"""
    r = git("rev-parse", "--abbrev-ref", "HEAD")
    if r.returncode == 0:
        return r.stdout.strip()
    return "main"


def is_git_repo() -> bool:
    """检查是否在 git 仓库中"""
    r = git("rev-parse", "--git-dir")
    return r.returncode == 0


def list_worktrees() -> list[dict]:
    """列出所有 git worktree"""
    r = git("worktree", "list", "--porcelain")
    if r.returncode != 0:
        return []

    worktrees = []
    current = {}
    for line in r.stdout.strip().split("\n"):
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line[9:]}
        elif line.startswith("HEAD "):
            current["head"] = line[5:]
        elif line.startswith("branch "):
            current["branch"] = line[7:]
        elif line == "":
            if current:
                worktrees.append(current)
            current = {}
    if current:
        worktrees.append(current)
    return worktrees


def find_worktree(name: str) -> dict | None:
    """按名称查找 worktree"""
    wts = list_worktrees()
    for wt in wts:
        if wt.get("path", "").endswith(name) or wt.get("branch", "").endswith(name):
            return wt
    return None


def get_repo_root() -> Path:
    """获取 git 仓库根目录"""
    r = git("rev-parse", "--show-toplevel")
    if r.returncode == 0:
        return Path(r.stdout.strip())
    return Path(os.getcwd()).resolve()


def ensure_git_repo() -> bool:
    """确保当前目录是 git 仓库，如果不是则初始化"""
    if is_git_repo():
        return True
    print("[INFO] 当前目录不是 git 仓库，自动初始化...")
    r = git("init")
    if r.returncode != 0:
        print(f"[FAIL] git init 失败: {r.stderr.strip()}")
        return False
    # 创建初始提交（worktree 需要至少一个 commit）
    r = git("add", ".")
    git("config", "user.email", "relay@vibe-coding-team.local")
    git("config", "user.name", "Vibe Relay Runner")
    r = git("commit", "--allow-empty", "-m", "chore: init relay workspace")
    if r.returncode != 0:
        print(f"[WARN] 初始提交失败 (可能无文件): {r.stderr.strip()}")
        # 空提交再试一次
        r = git("commit", "--allow-empty", "-m", "chore: init relay workspace")
        if r.returncode != 0:
            print(f"[FAIL] 初始提交失败: {r.stderr.strip()}")
            return False
    print(f"[OK] git 仓库已初始化")
    return True


def create_worktree(name: str) -> dict:
    """创建独立 worktree"""
    if not ensure_git_repo():
        return {"success": False, "error": "无法初始化 git 仓库"}

    repo_root = get_repo_root()
    wt_path = repo_root.parent / name

    # 检查是否已存在
    existing = find_worktree(name)
    if existing:
        return {"success": True, "worktree": existing, "message": f"worktree '{name}' 已存在"}

    main_branch = get_main_branch()

    # 创建分支名：relay/<name>
    branch_name = f"relay/{name}"

    # 检查分支是否存在
    r = git("rev-parse", "--verify", branch_name)
    if r.returncode != 0:
        # 从 HEAD 创建新分支
        git("branch", branch_name)

    try:
        r = git("worktree", "add", str(wt_path), branch_name)
        if r.returncode != 0:
            return {"success": False, "error": f"创建 worktree 失败: {r.stderr.strip()}"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "创建 worktree 超时"}

    result = {
        "success": True,
        "worktree": {
            "name": name,
            "path": str(wt_path),
            "branch": branch_name,
            "base_branch": main_branch,
        },
    }
    return result


def merge_worktree(name: str) -> dict:
    """将 worktree 的改动 merge 回主分支"""
    if not is_git_repo():
        return {"success": False, "error": "当前目录不在 git 仓库中"}

    wt = find_worktree(name)
    if not wt:
        return {"success": False, "error": f"worktree '{name}' 未找到"}

    wt_path = wt["path"]
    branch = wt.get("branch", "").replace("refs/heads/", "")
    if not branch:
        return {"success": False, "error": f"无法确定 worktree '{name}' 的分支"}

    main_branch = get_main_branch()

    # 检查 worktree 是否有新提交
    r = git("log", "--oneline", "-1", cwd=wt_path)
    if r.returncode != 0 or not r.stdout.strip():
        return {"success": False, "error": f"worktree '{name}' 没有提交，无需 merge"}

    # 获取最新的提交信息
    last_msg = git("log", "--format=%s", "-1", cwd=wt_path).stdout.strip()

    # 策略：将 worktree 作为远程仓库 fetch，然后 merge
    # 使用绝对路径避免相对路径问题
    wt_abs_path = str(Path(wt_path).resolve())
    r = git("remote", "add", f"relay-{name}", wt_abs_path)
    if r.returncode != 0 and "already exists" not in r.stderr:
        # 可能已存在，更新 URL
        git("remote", "set-url", f"relay-{name}", wt_abs_path)

    r = git("fetch", f"relay-{name}", branch)
    if r.returncode != 0:
        # 清理 remote
        git("remote", "remove", f"relay-{name}")
        return {"success": False, "error": f"fetch worktree 失败: {r.stderr.strip()}"}

    # 获取 FETCH_HEAD 的 hash
    r = git("rev-parse", "FETCH_HEAD")
    if r.returncode != 0:
        git("remote", "remove", f"relay-{name}")
        return {"success": False, "error": "无法获取 FETCH_HEAD"}

    fetch_hash = r.stdout.strip()

    # merge FETCH_HEAD
    r = git("merge", fetch_hash, "--no-edit")
    git("remote", "remove", f"relay-{name}")

    if r.returncode != 0:
        # 检查是否有冲突
        conflict_check = git("diff", "--name-only", "--diff-filter=U")
        if conflict_check.returncode == 0 and conflict_check.stdout.strip():
            conflict_files = conflict_check.stdout.strip().split("\n")
            return {
                "success": False,
                "has_conflicts": True,
                "conflict_files": conflict_files,
                "error": f"merge 冲突，需手动解决: {', '.join(conflict_files[:5])}",
                "branch": branch,
            }
        return {"success": False, "error": f"merge 失败: {r.stderr.strip()}"}

    # 删除临时分支
    git("branch", "-D", branch)

    result = {
        "success": True,
        "branch": branch,
        "message": last_msg,
        "merged_into": main_branch,
        "conflict_files": [],
    }
    return result


def remove_worktree(name: str) -> dict:
    """清理 worktree"""
    wt = find_worktree(name)
    if not wt:
        return {"success": False, "error": f"worktree '{name}' 未找到"}

    wt_path = wt["path"]
    branch = wt.get("branch", "").replace("refs/heads/", "")

    errors = []
    # 先尝试安全删除
    r = git("worktree", "remove", wt_path)
    if r.returncode != 0:
        # 强制删除
        r = git("worktree", "remove", "--force", wt_path)
        if r.returncode != 0:
            errors.append(f"worktree remove 失败: {r.stderr.strip()}")

    # 清理残留分支
    if branch:
        git("branch", "-D", branch)

    # 清理本地 worktree 目录
    try:
        import shutil
        p = Path(wt_path)
        if p.exists():
            shutil.rmtree(p)
    except Exception as e:
        errors.append(f"清理目录失败: {e}")

    if errors:
        return {"success": False, "error": "; ".join(errors)}
    return {"success": True, "message": f"worktree '{name}' 已清理"}


def print_worktrees():
    """打印 worktree 列表"""
    wts = list_worktrees()
    if not wts:
        print("[INFO] 无活跃 worktree")
        return

    print(f"活跃 Worktree ({len(wts)}):")
    for wt in wts:
        path = wt.get("path", "?")
        branch = wt.get("branch", "detached").replace("refs/heads/", "")
        head = wt.get("head", "?")[:8]
        name = Path(path).name
        print(f"  [{name}] {path}")
        print(f"      分支: {branch}   HEAD: {head}")


def print_result(result: dict, action: str):
    """打印操作结果"""
    if result.get("success"):
        print(f"[OK] {action} 成功")
        if result.get("worktree"):
            wt = result["worktree"]
            print(f"     worktree: {wt.get('path')} @ {wt.get('branch')}")
        if result.get("message"):
            print(f"     提交: {result['message']}")
        if result.get("merged_into"):
            print(f"     merge 到: {result['merged_into']}")
    else:
        print(f"[FAIL] {action} 失败")
        if result.get("has_conflicts"):
            print(f"     冲突文件: {', '.join(result.get('conflict_files', []))}")
            print(f"     解决后运行: git merge --continue")
        print(f"     原因: {result.get('error', '?')}")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python scripts/relay-worktree.py --create <name>")
        print("  python scripts/relay-worktree.py --list")
        print("  python scripts/relay-worktree.py --merge <name>")
        print("  python scripts/relay-worktree.py --remove <name>")
        print("  python scripts/relay-worktree.py --merge-all")
        print("  python scripts/relay-worktree.py --cleanup-all")
        sys.exit(1)

    command = sys.argv[1]

    if command == "--list":
        print_worktrees()
        sys.exit(0)

    if command == "--cleanup-all":
        wts = list_worktrees()
        count = 0
        for wt in wts:
            branch = wt.get("branch", "")
            if not branch.startswith("refs/heads/relay/"):
                continue
            name = Path(wt["path"]).name
            result = remove_worktree(name)
            if result["success"]:
                count += 1
                print(f"  [OK] 已清理: {name}")
            else:
                print(f"  [FAIL] {name}: {result.get('error', '?')}")
        print(f"  共清理 {count} 个 worktree")
        sys.exit(0)

    if command == "--merge-all":
        wts = list_worktrees()
        success = 0
        failed = 0
        for wt in wts:
            name = Path(wt["path"]).name
            branch = wt.get("branch", "").replace("refs/heads/", "")
            if branch.startswith("relay/"):
                print(f"\n--- Merging {name} ---")
                result = merge_worktree(name)
                if result["success"]:
                    success += 1
                else:
                    failed += 1
                print_result(result, f"merge {name}")
        print(f"\n结果: {success} 成功, {failed} 失败")
        sys.exit(0 if failed == 0 else 1)

    if len(sys.argv) < 3:
        print(f"[FAIL] {command} 需要 <name> 参数")
        sys.exit(1)

    name = sys.argv[2]

    if command == "--create":
        result = create_worktree(name)
        print_result(result, f"创建 worktree '{name}'")
        sys.exit(0 if result["success"] else 1)

    elif command == "--merge":
        result = merge_worktree(name)
        print_result(result, f"merge worktree '{name}'")
        sys.exit(0 if result["success"] else 1)

    elif command == "--remove":
        result = remove_worktree(name)
        print_result(result, f"清理 worktree '{name}'")
        sys.exit(0 if result["success"] else 1)

    else:
        print(f"[FAIL] 未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
