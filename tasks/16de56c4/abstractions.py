"""Abstractions explored while solving ARC task 16de56c4."""

from __future__ import annotations

import json
from math import gcd
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

Grid = List[List[int]]
Sample = Dict[str, Grid]


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def apply_row_rule(grid: Grid) -> Grid:
    result = copy_grid(grid)
    width = len(grid[0])
    for r, row in enumerate(grid):
        nonzero_cols = [c for c, v in enumerate(row) if v]
        if not nonzero_cols:
            continue
        colors = {row[c] for c in nonzero_cols}
        if len(colors) > 2:
            continue

        last_col = nonzero_cols[-1]
        color = row[last_col]
        same_color_cols = [c for c in nonzero_cols if row[c] == color]
        if len(same_color_cols) >= 2:
            diffs = [same_color_cols[i + 1] - same_color_cols[i] for i in range(len(same_color_cols) - 1)]
            step = diffs[0]
            for d in diffs[1:]:
                step = gcd(step, d)
            if step == 0:
                continue
            start = min(same_color_cols)
            for c in range(start, -1, -step):
                result[r][c] = color
            for c in range(start + step, width, step):
                result[r][c] = color
        else:
            other_cols = [c for c in nonzero_cols if c != last_col]
            if not other_cols:
                continue
            freq: Dict[int, int] = {}
            for c in other_cols:
                freq[row[c]] = freq.get(row[c], 0) + 1
            if all(count < 2 for count in freq.values()):
                continue
            step = 0
            for c in other_cols:
                delta = abs(last_col - c)
                step = delta if step == 0 else gcd(step, delta)
            if step == 0:
                continue
            for c in range(last_col, -1, -step):
                result[r][c] = color
    return result


def apply_column_rule(grid: Grid, original: Grid) -> Grid:
    height = len(grid)
    width = len(grid[0])
    result = copy_grid(grid)
    for c in range(width):
        orig_col = [original[r][c] for r in range(height)]
        positions_by_color: Dict[int, List[int]] = {}
        for r, val in enumerate(orig_col):
            if val:
                positions_by_color.setdefault(val, []).append(r)

        for color, rows in positions_by_color.items():
            if len(rows) < 2:
                continue
            rows.sort()
            diffs = [rows[i + 1] - rows[i] for i in range(len(rows) - 1)]
            step = diffs[0]
            for d in diffs[1:]:
                step = gcd(step, d)
            if step == 0:
                continue
            for r in rows:
                result[r][c] = color
            r = rows[0] - step
            while r >= 0:
                val = orig_col[r]
                if val and val != color:
                    break
                result[r][c] = color
                r -= step

        for color, rows in positions_by_color.items():
            if len(rows) != 1:
                continue
            base_row = rows[0]
            repeated_sets = [pos for col, pos in positions_by_color.items() if col != color and len(pos) >= 2]
            if not repeated_sets:
                continue
            target_rows: List[int] = []
            for pos in repeated_sets:
                target_rows.extend([r for r in pos if r > base_row])
            if not target_rows:
                continue
            step_base = 0
            for r in target_rows:
                delta = r - base_row
                step_base = delta if step_base == 0 else gcd(step_base, delta)
            if step_base == 0:
                continue
            flat = sorted(set(target_rows))
            if len(flat) >= 2:
                step_repeat = flat[1] - flat[0]
                for i in range(1, len(flat) - 1):
                    step_repeat = gcd(step_repeat, flat[i + 1] - flat[i])
                if step_repeat and step_repeat != step_base:
                    continue
            for r in target_rows:
                if (r - base_row) % step_base == 0:
                    result[r][c] = color
    return result


def identity(grid: Grid) -> Grid:
    return copy_grid(grid)


def row_rule_only(grid: Grid) -> Grid:
    return apply_row_rule(grid)


def column_rule_only(grid: Grid) -> Grid:
    return apply_column_rule(grid, grid)


def row_then_column(grid: Grid) -> Grid:
    after_rows = apply_row_rule(grid)
    return apply_column_rule(after_rows, grid)


ABSTRACTIONS: Sequence[Tuple[str, Callable[[Grid], Grid]]] = (
    ("identity", identity),
    ("row_rule", row_rule_only),
    ("column_rule", column_rule_only),
    ("row_then_column", row_then_column),
)


def load_samples(kind: str) -> List[Sample]:
    repo_root = Path(__file__).resolve().parents[1]
    task_path = repo_root / "arc2_samples" / "16de56c4.json"
    data = json.loads(task_path.read_text())
    if kind == "arc_gen":
        arc_gen_path = repo_root / "arc2_samples" / "16de56c4_arcgen.json"
        if not arc_gen_path.exists():
            return []
        data = json.loads(arc_gen_path.read_text())
        return data.get("train", [])
    return data.get(kind, [])


def evaluate_split(
    samples: Iterable[Sample],
    transform: Callable[[Grid], Grid],
) -> Tuple[int, int, Optional[int]]:
    matches = 0
    total = 0
    first_failure: Optional[int] = None
    for idx, sample in enumerate(samples):
        total += 1
        predicted = transform(sample["input"])
        expected = sample.get("output")
        if expected is None:
            continue
        if predicted == expected:
            matches += 1
        elif first_failure is None:
            first_failure = idx
    return matches, total, first_failure


def run_evaluation() -> None:
    train_samples = load_samples("train")
    test_samples = load_samples("test")
    arc_gen_samples = load_samples("arc_gen")

    for name, transform in ABSTRACTIONS:
        print(f"Abstraction: {name}")
        for split_name, samples in (
            ("train", train_samples),
            ("test", test_samples),
            ("arc-gen", arc_gen_samples),
        ):
            if not samples:
                print(f"  {split_name}: no cases")
                continue
            matches, total, first_failure = evaluate_split(samples, transform)
            if split_name == "test":
                print(f"  {split_name}: produced {total} predictions (no ground truth)")
                continue
            status = f"{matches}/{total} matches"
            if matches == total:
                print(f"  {split_name}: {status}")
            else:
                print(
                    f"  {split_name}: {status} (first failure at index {first_failure})"
                )
        print()


if __name__ == "__main__":
    run_evaluation()
