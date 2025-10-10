"""Abstractions explored while solving ARC task 31f7f899."""

from collections import Counter
from pathlib import Path
import json
from typing import Callable, Dict, List, Optional

Grid = List[List[int]]


def load_task() -> Dict[str, List[Dict[str, Grid]]]:
    task_path = Path("arc2_samples/31f7f899.json")
    return json.loads(task_path.read_text())


def deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def identity_abstraction(grid: Grid) -> Grid:
    """Baseline pass-through."""
    return deep_copy(grid)


def sorted_stripes_abstraction(grid: Grid) -> Grid:
    """Sort the vertical spans of non-dominant stripes left→right."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return deep_copy(grid)

    background = max(
        Counter(cell for row in grid for cell in row).items(),
        key=lambda item: (item[1], -item[0]),
    )[0]

    def non_bg_count(row: List[int]) -> int:
        return sum(cell != background for cell in row)

    center_idx = max(range(rows), key=lambda r: (non_bg_count(grid[r]), -r))
    center_row = grid[center_idx]

    dominant_color = max(
        Counter(center_row).items(),
        key=lambda item: (item[1], -item[0]),
    )[0]

    special_cols: List[int] = []
    colors: List[int] = []
    lengths: List[int] = []

    for c, color in enumerate(center_row):
        if color == background or color == dominant_color:
            continue
        top = bottom = center_idx
        while top > 0 and grid[top - 1][c] == color:
            top -= 1
        while bottom + 1 < rows and grid[bottom + 1][c] == color:
            bottom += 1
        special_cols.append(c)
        colors.append(color)
        lengths.append(bottom - top + 1)

    target_lengths = sorted(lengths)

    output = deep_copy(grid)
    for c, color, target_len in zip(special_cols, colors, target_lengths):
        radius = target_len // 2
        top = center_idx - radius
        bottom = center_idx + radius
        for r in range(rows):
            output[r][c] = background
        for r in range(top, bottom + 1):
            output[r][c] = color

    return output


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": identity_abstraction,
    "sorted_stripes": sorted_stripes_abstraction,
}


def evaluate() -> None:
    task = load_task()
    for name, fn in ABSTRACTIONS.items():
        print(f"Abstraction: {name}")
        for split in ("train", "test", "arc-gen"):
            pairs = task.get(split, [])
            if not pairs:
                print(f"  {split}: no examples")
                continue
            matches = 0
            first_fail: Optional[int] = None
            for idx, ex in enumerate(pairs):
                pred = fn(ex["input"])
                expected = ex.get("output")
                if expected is None:
                    continue
                if pred == expected:
                    matches += 1
                elif first_fail is None:
                    first_fail = idx
            total_known = sum(1 for ex in pairs if "output" in ex)
            if total_known:
                print(
                    f"  {split}: {matches}/{total_known} matches",
                    "first fail=" + str(first_fail) if matches != total_known else "",
                )
            else:
                print(f"  {split}: predictions generated (no references)")
        print()


def main() -> None:
    evaluate()


if __name__ == "__main__":
    main()
