"""Abstractions explored while solving ARC task 4c3d4a41."""

import json
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, List


BASE_DIR = Path(__file__).resolve().parent.parent
TASK_PATH = BASE_DIR / "arc2_samples" / "4c3d4a41.json"


Grid = List[List[int]]


def load_task() -> Dict[str, List[Dict[str, Grid]]]:
    return json.loads(TASK_PATH.read_text())


def clone(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def find_split_col(grid: Grid) -> int:
    top_row = grid[0]
    for col, value in enumerate(top_row):
        if value != 0:
            return col
    return len(top_row) // 2


def dominant_left_color(grid: Grid, split_col: int) -> int:
    counter = Counter()
    for row in grid:
        for col in range(split_col):
            value = row[col]
            if value != 0:
                counter[value] += 1
    return counter.most_common(1)[0][0] if counter else 5


def apply_overlay(grid: Grid, base: Grid, split_col: int, color: int) -> Grid:
    height = len(grid)
    width = len(grid[0])
    offset = split_col + 1
    for r in range(height):
        for c in range(split_col):
            if c + offset < width and grid[r][c] == color:
                base[r][c + offset] = color
            base[r][c] = 0
    return base


def overlay_only(grid: Grid) -> Grid:
    split_col = find_split_col(grid)
    color = dominant_left_color(grid, split_col)
    result = clone(grid)
    return apply_overlay(grid, result, split_col, color)


def copy_second_row_then_overlay(grid: Grid) -> Grid:
    split_col = find_split_col(grid)
    color = dominant_left_color(grid, split_col)
    height = len(grid)
    width = len(grid[0])
    result = clone(grid)
    if height > 2:
        for c in range(split_col + 1, width):
            result[1][c] = grid[2][c]
    return apply_overlay(grid, result, split_col, color)


def shift_rows_with_left_presence(grid: Grid) -> Grid:
    split_col = find_split_col(grid)
    color = dominant_left_color(grid, split_col)
    height = len(grid)
    width = len(grid[0])
    result = clone(grid)
    for src_row in range(height):
        if any(grid[src_row][c] == color for c in range(split_col)):
            dst_row = src_row - 1
            if dst_row >= 0:
                for c in range(split_col + 1, width):
                    result[dst_row][c] = grid[src_row][c]
    return apply_overlay(grid, result, split_col, color)


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "overlay_only": overlay_only,
    "copy_second_row_then_overlay": copy_second_row_then_overlay,
    "shift_rows_with_left_presence": shift_rows_with_left_presence,
}


def evaluate_examples(examples: List[Dict[str, Grid]], fn: Callable[[Grid], Grid]) -> Dict[str, object]:
    total = len(examples)
    if total == 0:
        return {"total": 0, "matches": 0, "first_failure": None, "has_outputs": True}
    if any("output" not in ex for ex in examples):
        return {"total": total, "matches": None, "first_failure": None, "has_outputs": False}
    matches = 0
    first_failure = None
    for idx, ex in enumerate(examples):
        prediction = fn(ex["input"])
        if prediction == ex["output"]:
            matches += 1
        elif first_failure is None:
            first_failure = idx
    return {"total": total, "matches": matches, "first_failure": first_failure, "has_outputs": True}


def describe(result: Dict[str, object]) -> str:
    if result["total"] == 0:
        return "no cases"
    if not result["has_outputs"]:
        return f"outputs unavailable ({result['total']} cases)"
    matches = result["matches"]
    total = result["total"]
    if matches == total:
        return f"{matches}/{total} matches"
    first_failure = result["first_failure"]
    return f"{matches}/{total} matches, first failure at index {first_failure}"


def main() -> None:
    task = load_task()
    for name, fn in ABSTRACTIONS.items():
        print(f"{name}:")
        for split in ("train", "test", "arc-gen"):
            examples = task.get(split, [])
            if not examples:
                print(f"  {split}: no data")
                continue
            summary = describe(evaluate_examples(examples, fn))
            print(f"  {split}: {summary}")
        print()


if __name__ == "__main__":
    main()

