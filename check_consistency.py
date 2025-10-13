#!/usr/bin/env python3
"""Consistency checker for the ARC-AGI-2 task bundle layout."""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

TASKS_DIR = Path("tasks")
README_PATH = Path("README.md")
CHANGELOG_PATH = Path("CHANGELOG.md")

@dataclass
class TaskInfo:
    task_id: str
    bundle_dir: Path
    has_solver: bool
    has_abs_py: bool
    has_abs_md: bool
    is_identity: bool

IDENTITY_SNIPPET = "return [row[:] for row in grid]"


def detect_identity_solver(path: Path) -> bool:
    if not path.exists():
        return False
    content = path.read_text(encoding="utf-8")
    return IDENTITY_SNIPPET in content and content.count("\n") < 40


def gather_task_info(root: Path) -> Dict[str, TaskInfo]:
    infos: Dict[str, TaskInfo] = {}
    for bundle_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        task_id = bundle_dir.name
        solver = bundle_dir / "solution.py"
        abs_py = bundle_dir / "abstractions.py"
        abs_md = bundle_dir / "abstractions.md"
        infos[task_id] = TaskInfo(
            task_id=task_id,
            bundle_dir=bundle_dir,
            has_solver=solver.exists(),
            has_abs_py=abs_py.exists(),
            has_abs_md=abs_md.exists(),
            is_identity=detect_identity_solver(solver),
        )
    return infos


def check_bundles(verbose: bool = False) -> bool:
    if not TASKS_DIR.exists():
        print("❌ tasks/ directory not found")
        return False

    infos = gather_task_info(TASKS_DIR)
    if not infos:
        print("❌ No task bundles found under tasks/")
        return False

    identity = [tid for tid, info in infos.items() if info.is_identity]
    missing_solver = [tid for tid, info in infos.items() if not info.has_solver]
    missing_abs_py = [tid for tid, info in infos.items() if not info.is_identity and not info.has_abs_py]
    missing_abs_md = [tid for tid, info in infos.items() if not info.is_identity and not info.has_abs_md]

    print("🔍 Bundle summary")
    print(f"   Total bundles        : {len(infos)}")
    print(f"   Identity baselines   : {len(identity)}")
    print(f"   Full abstractions    : {len(infos) - len(identity)}")
    print()

    ok = True
    if missing_solver:
        ok = False
        print(f"❌ Bundles missing solution.py ({len(missing_solver)}):")
        for tid in sorted(missing_solver):
            print(f"   - {tid}")
        print()

    if missing_abs_py or missing_abs_md:
        ok = False
        if missing_abs_py:
            print(f"❌ Bundles missing abstractions.py ({len(missing_abs_py)}):")
            for tid in sorted(missing_abs_py):
                print(f"   - {tid}")
            print()
        if missing_abs_md:
            print(f"❌ Bundles missing abstractions.md ({len(missing_abs_md)}):")
            for tid in sorted(missing_abs_md):
                print(f"   - {tid}")
            print()

    if verbose:
        for tid in sorted(infos):
            info = infos[tid]
            status: List[str] = []
            status.append("solver" if info.has_solver else "no-solver")
            status.append("identity" if info.is_identity else "full")
            if not info.is_identity:
                status.append("abs.py" if info.has_abs_py else "no-abs.py")
                status.append("abs.md" if info.has_abs_md else "no-abs.md")
            print(f"   • {tid}: {', '.join(status)}")
        print()

    if ok:
        print("✅ Bundle layout looks good\n")
    else:
        print("💥 Bundle issues detected\n")
    return ok


def check_documentation(task_count: int) -> bool:
    ok = True
    if not README_PATH.exists():
        print("❌ README.md missing")
        return False

    readme = README_PATH.read_text(encoding="utf-8")
    count_matches = re.findall(r"\b(\d+)\s+tasks?\b", readme)
    if str(task_count) in count_matches or f"{task_count} tasks" in readme:
        print(f"✅ README mentions {task_count} tasks")
    else:
        ok = False
        print(f"❌ README does not reference the current task count ({task_count})")

    if "tasks/" not in readme:
        ok = False
        print("❌ README has not been updated to describe the tasks/ layout")

    if CHANGELOG_PATH.exists():
        changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
        placeholders = re.findall(r"\d{4}-\d{2}-XX", changelog)
        if placeholders:
            ok = False
            print(f"❌ CHANGELOG contains placeholder dates: {placeholders}")
        else:
            print("✅ CHANGELOG dates look concrete")
    else:
        print("⚠️ CHANGELOG.md missing")
    print()
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Check dataset bundle consistency")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    tasks_ok = check_bundles(verbose=args.verbose)
    doc_ok = check_documentation(len([p for p in TASKS_DIR.iterdir() if p.is_dir()]))

    print("=" * 50)
    if tasks_ok and doc_ok:
        print("🎉 All checks passed! Repository is consistent.")
        sys.exit(0)
    else:
        print("💥 Some checks failed. Please review the messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
