"""Abstraction experiments for ARC task 3a25b0d8.

This script captures three stages of the solver that we iterated through:

1. `expanded_only` – just crop to the interesting columns/rows and add
   background padding.
2. `band_adjust` – adds the colour-specific band heuristics (widen 7,
   suppress singleton 4s, etc.) but stops before the final row-level
   synthesis.
3. `final_solver` – the finished solver from
   `analysis.arc2_samples.3a25b0d8`.

The harness evaluates each abstraction on the training set and reports
match counts plus the first failing example index. Test inputs do not ship
with ground-truth outputs, so they are omitted from the accuracy report.
"""

from __future__ import annotations

import importlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

solver = importlib.import_module("analysis.arc2_samples.3a25b0d8")

Grid = List[List[int]]


def _data_path() -> Path:
    return Path(__file__).resolve().parent / "arc2_samples" / "3a25b0d8.json"


def load_task() -> Dict[str, Sequence[Dict[str, Grid]]]:
    return json.loads(_data_path().read_text())


def _trim_and_expand(grid: Grid) -> Tuple[List[List[int]], Dict[str, int]]:
    height, width = len(grid), len(grid[0])
    flat = [cell for row in grid for cell in row]
    bg = Counter(flat).most_common(1)[0][0]
    non_bg = [cell for cell in flat if cell != bg]
    base = Counter(non_bg).most_common(1)[0][0] if non_bg else bg

    interesting_cols = [
        c for c in range(width) if any(grid[r][c] not in (bg, base) for r in range(height))
    ]
    if not interesting_cols:
        interesting_cols = [c for c in range(width) if any(grid[r][c] != bg for r in range(height))]

    col_lo, col_hi = min(interesting_cols), max(interesting_cols)
    tile = [[grid[r][c] for c in range(col_lo, col_hi + 1)] for r in range(height)]

    def row_has_special(row: Iterable[int]) -> bool:
        return any(cell not in (bg, base) for cell in row)

    prefix = 0
    while prefix < len(tile) and not row_has_special(tile[prefix]):
        prefix += 1
    start_idx = max(0, prefix - 1)

    suffix = len(tile) - 1
    while suffix >= 0 and not row_has_special(tile[suffix]):
        suffix -= 1
    end_idx = min(len(tile) - 1, suffix + 1) if suffix >= 0 else len(tile) - 1

    trimmed = tile[start_idx:end_idx + 1]
    expanded = [[bg] + row + [bg] for row in trimmed]
    return expanded, {"bg": bg, "base": base}


def expanded_only(grid: Grid) -> Grid:
    expanded, _ = _trim_and_expand(grid)
    return [row[:] for row in expanded]


def band_adjust(grid: Grid) -> Grid:
    expanded, info = _trim_and_expand(grid)
    bg = info["bg"]
    base = info["base"]
    width = len(expanded[0]) if expanded else 0

    def widen(row: List[int], color: int, target_len: int = 3) -> None:
        idxs = [i for i, val in enumerate(row) if val == color]
        if not idxs or len(idxs) >= target_len:
            return
        start = min(idxs)
        end = max(idxs)
        needed = target_len - (end - start + 1)
        left = start - 1
        right = end + 1
        while needed > 0 and (left >= 1 or right <= len(row) - 2):
            progressed = False
            if left >= 1 and row[left] == base:
                row[left] = color
                left -= 1
                needed -= 1
                progressed = True
            if needed <= 0:
                break
            if right <= len(row) - 2 and row[right] == base:
                row[right] = color
                right += 1
                needed -= 1
                progressed = True
            if not progressed:
                break

    specials_per_row = [{cell for cell in row if cell not in (bg, base)} for row in expanded]
    adjusted: List[List[int]] = []

    for idx, row in enumerate(expanded):
        cur = row[:]
        specials = specials_per_row[idx]

        if 7 in specials:
            widen(cur, 7)

        removed_all_4 = False
        if 4 in specials:
            positions = [i for i, val in enumerate(cur) if val == 4]
            runs: List[Tuple[int, int]] = []
            for i, val in enumerate(cur):
                if val == 4:
                    if runs and runs[-1][1] == i - 1:
                        runs[-1] = (runs[-1][0], i)
                    else:
                        runs.append((i, i))
            max_run = max((end - start + 1) for start, end in runs) if runs else 0
            if max_run <= 1:
                for pos in positions:
                    cur[pos] = base
                removed_all_4 = True
            else:
                cur[0] = base
                cur[-1] = base
                if width > 2 and 3 in specials:
                    cur[1] = 3
                    cur[-2] = 3

        if 3 in specials and (4 not in specials or removed_all_4):
            if base == 1:
                cur[0] = base
                cur[-1] = base
                if width > 2:
                    cur[1] = 3
                    cur[-2] = 3
                for j in range(2, width - 2):
                    cur[j] = base

        if not specials:
            prev = specials_per_row[idx - 1] if idx > 0 else set()
            nxt = specials_per_row[idx + 1] if idx + 1 < len(specials_per_row) else set()
            if 3 in (prev | nxt):
                cur[0] = base
                cur[-1] = base
                if width > 2:
                    cur[1] = 3
                    cur[-2] = 3
            elif prev and len(prev) == 1 and not nxt and adjusted:
                prev_row = adjusted[-1]
                for j, val in enumerate(prev_row):
                    if prev_row[j] != bg:
                        cur[j] = base

        if 6 in specials:
            cur[0] = bg
            cur[-1] = bg
            if width > 2:
                cur[1] = base
                cur[-2] = base

        adjusted.append(cur)

    return adjusted


def final_solver(grid: Grid) -> Grid:
    return solver.solve_3a25b0d8(grid)


ABSTRACTIONS = {
    "expanded_only": expanded_only,
    "band_adjust": band_adjust,
    "final_solver": final_solver,
}


def evaluate() -> None:
    task = load_task()
    train = task["train"]

    print("Abstraction evaluation on train split:")
    for name, fn in ABSTRACTIONS.items():
        passed = 0
        first_fail: Tuple[str, int] | None = None
        for idx, example in enumerate(train):
            pred = fn(example["input"])
            ok = pred == example["output"]
            if ok:
                passed += 1
            elif first_fail is None:
                first_fail = ("train", idx)
        total = len(train)
        summary = f"  {name}: {passed}/{total} correct"
        if first_fail is not None:
            summary += f", first_fail={first_fail}"
        else:
            summary += ", first_fail=None"
        print(summary)


if __name__ == "__main__":
    evaluate()
