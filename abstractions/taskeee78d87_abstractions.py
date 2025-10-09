#!/usr/bin/env python3
"""Abstraction experiments for ARC task eee78d87."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from arc2_samples.eee78d87 import COL_TYPE_MAP, ROW_TYPE_MAP, TEMPLATES


Grid = List[List[int]]


def choose_template_name(grid: Grid) -> str:
    coords = [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val != 7]
    if not coords:
        return "plus"

    rows = [r for r, _ in coords]
    cols = [c for _, c in coords]
    center = ((min(rows) + max(rows)) // 2, (min(cols) + max(cols)) // 2)

    def count(offsets: Iterable[Tuple[int, int]]) -> int:
        total = 0
        for dr, dc in offsets:
            rr, cc = center[0] + dr, center[1] + dc
            if 0 <= rr < len(grid) and 0 <= cc < len(grid[0]) and grid[rr][cc] != 7:
                total += 1
        return total

    orth = count([(-1, 0), (1, 0), (0, -1), (0, 1)])
    diag = count([(-1, -1), (-1, 1), (1, -1), (1, 1)])

    if orth == 4:
        return "plus"
    if orth == 2:
        return "H"
    if diag == 4:
        return "X"
    return "plus"


def render_template(name: str) -> Grid:
    table = TEMPLATES[name]
    return [
        [table[ROW_TYPE_MAP[r]][COL_TYPE_MAP[c]] for c in range(len(COL_TYPE_MAP))]
        for r in range(len(ROW_TYPE_MAP))
    ]


def plus_bias(_: Grid) -> Grid:
    """Naive first attempt: assume every shape behaves like the plus case."""
    return render_template("plus")


def or_only(grid: Grid) -> Grid:
    """Second attempt: classify but restrict to OR-based templates (fails on the X case)."""
    key = choose_template_name(grid)
    if key == "X":
        key = "H"
    return render_template(key)


def final_template(grid: Grid) -> Grid:
    """Final abstraction that matches the task."""
    return render_template(choose_template_name(grid))


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "plus_bias": plus_bias,
    "or_only": or_only,
    "final_template": final_template,
}


def evaluate() -> None:
    data_path = ROOT / "arc2_samples" / "eee78d87.json"
    payload = json.loads(data_path.read_text())

    for name, solver in ABSTRACTIONS.items():
        print(f"=== {name} ===")
        for split in ("train", "test"):
            cases = payload.get(split, [])
            total = len(cases)
            matched = 0
            first_fail = None
            for idx, case in enumerate(cases):
                pred = solver(case["input"])
                target = case.get("output")
                if target is None:
                    continue
                if pred == target:
                    matched += 1
                elif first_fail is None:
                    first_fail = idx
            if cases and cases[0].get("output") is not None:
                print(f"  {split}: {matched}/{total} matched, first failure={first_fail}")
            else:
                print(f"  {split}: predictions generated (no ground truth)")
        print()

    test_case = payload["test"][0]["input"]
    prediction = final_template(test_case)
    print("Final template prediction for test[0]:")
    for row in prediction:
        print("".join("0123456789abcdef"[cell] for cell in row))


if __name__ == "__main__":
    evaluate()
