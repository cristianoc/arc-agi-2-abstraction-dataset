"""Abstraction experiments for task 20270e3b."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Tuple


BG = 1
SPECIAL = 7
FILL = 4


Grid = List[List[int]]


def load_task() -> dict:
    path = Path("analysis/arc2_samples/20270e3b.json")
    return json.loads(path.read_text())


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def remove_special_rows(grid: Grid) -> Optional[Grid]:
    rows = [r for r, row in enumerate(grid) if any(v == SPECIAL for v in row)]
    if not rows:
        return None
    top, bottom = min(rows), max(rows)
    keep = [row[:] for idx, row in enumerate(grid) if not (top <= idx <= bottom)]
    return keep if keep else None


def vertical_overlay(grid: Grid) -> Optional[Grid]:
    h = len(grid)
    w = len(grid[0])
    sep_cols = [c for c in range(w) if all(grid[r][c] == BG for r in range(h))]
    if not sep_cols:
        return None
    left_edge = sep_cols[0]
    right_edge = sep_cols[-1]
    left = [row[:left_edge] for row in grid]
    right = [row[right_edge + 1 :] for row in grid]
    if not left:
        return None

    out = copy_grid(left)
    for r in range(h):
        for c in range(len(out[0])):
            if out[r][c] == SPECIAL:
                out[r][c] = FILL

    if not right or not right[0]:
        return out

    left_cols_with_special = [
        c for c in range(len(out[0])) if any(grid[r][c] == SPECIAL for r in range(h))
    ]
    start = (
        min(left_cols_with_special)
        if left_cols_with_special
        else max(0, len(out[0]) - len(right[0]))
    )

    left_rows_with_special = [r for r in range(h) if any(grid[r][c] == SPECIAL for c in range(left_edge))]
    right_rows_with_special = [
        r for r in range(h) if any(grid[r][c] == SPECIAL for c in range(right_edge + 1, w))
    ]
    left_anchor = min(left_rows_with_special) if left_rows_with_special else 0
    right_anchor = min(right_rows_with_special) if right_rows_with_special else 0
    row_offset = left_anchor - right_anchor - 1

    for r in range(h):
        rr = r + row_offset
        if not (0 <= rr < h):
            continue
        for k in range(len(right[0])):
            cc = start + k
            if cc >= len(out[0]):
                break
            if right[r][k] == FILL:
                out[rr][cc] = FILL
    return out


def horizontal_overlay(grid: Grid) -> Optional[Grid]:
    h = len(grid)
    w = len(grid[0])
    rows_with_special = [r for r, row in enumerate(grid) if any(v == SPECIAL for v in row)]
    if not rows_with_special:
        return None

    top = min(rows_with_special)
    bottom = max(rows_with_special)
    span = bottom - top + 1

    cols_with_special = [c for c in range(w) if any(grid[r][c] == SPECIAL for r in range(h))]
    if cols_with_special:
        c0, c1 = min(cols_with_special), max(cols_with_special)
    else:
        c0 = c1 = 0
    shift = c1 - c0
    extend = shift if c1 < w - 1 else 0
    new_w = w + extend

    out = [[BG] * new_w for _ in range(h - span)]

    for r in range(top):
        for c in range(w):
            val = FILL if grid[r][c] == SPECIAL else grid[r][c]
            out[r][c] = val

    for r in range(bottom + 1, h):
        tgt = r - span
        for c in range(w):
            val = FILL if grid[r][c] == SPECIAL else grid[r][c]
            cc = c + extend
            if cc < new_w:
                out[tgt][cc] = val

    for r in range(top, bottom + 1):
        tgt = r - span
        if 0 <= tgt < len(out):
            for c in range(w):
                if grid[r][c] == FILL:
                    cc = c + extend
                    if 0 <= cc < new_w:
                        out[tgt][cc] = FILL

    return out


def final_solver(grid: Grid) -> Grid:
    base = copy_grid(grid)
    res = vertical_overlay(base)
    if res is not None:
        return res
    res = horizontal_overlay(base)
    if res is not None:
        return res
    return [[FILL if v == SPECIAL else v for v in row] for row in base]


Abstraction = Callable[[Grid], Optional[Grid]]


def evaluate(split_name: str, cases: Sequence[dict], abstractions: Sequence[Tuple[str, Abstraction]]):
    print(f"[{split_name}] {len(cases)} cases")
    has_gt = any("output" in case for case in cases)
    for name, fn in abstractions:
        total = len(cases)
        matches = 0
        evaluated = 0
        first_fail = None
        preds: List[Grid] = []
        for idx, case in enumerate(cases):
            pred = fn(copy_grid(case["input"]))
            if pred is None:
                pred = case["input"]
            preds.append(pred)
            gt = case.get("output")
            if gt is None:
                continue
            evaluated += 1
            if pred == gt:
                matches += 1
            elif first_fail is None:
                first_fail = idx
        if evaluated:
            status = f"{matches}/{evaluated}"
            if evaluated != total:
                status += f" (of {total})"
            if first_fail is not None:
                status += f" (first fail at {first_fail})"
        else:
            if preds:
                dims = ", ".join(f"{len(p)}x{len(p[0])}" for p in preds[:2])
            else:
                dims = "n/a"
            status = f"no ground truth (first dims {dims})"
        print(f"  {name:20s} -> {status}")
    print()


def main():
    task = load_task()
    abstractions: Sequence[Tuple[str, Abstraction]] = [
        ("identity", lambda g: copy_grid(g)),
        ("remove_rows", remove_special_rows),
        ("vertical_overlay", vertical_overlay),
        ("horizontal_overlay", horizontal_overlay),
        ("final_solver", final_solver),
    ]

    evaluate("train", task.get("train", []), abstractions)
    evaluate("test", task.get("test", []), abstractions)
    evaluate("arc-gen", task.get("arc-gen", []), abstractions)


if __name__ == "__main__":
    main()
