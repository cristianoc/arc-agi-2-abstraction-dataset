"""Abstractions explored for ARC task dd6b8c4b.

This module captures the intermediate pipelines considered while developing the
final solver and offers a small harness so we can compare their performance
across the available splits (train/test/arc-gen).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from analysis.arc2_samples.dd6b8c4b import solve_dd6b8c4b

Grid = List[List[int]]
Case = Tuple[Grid, Grid]
Abstraction = Callable[[Grid], Grid]


def _center(grid: Grid) -> Tuple[int, int]:
    return len(grid) // 2, len(grid[0]) // 2


def identity_abstraction(grid: Grid) -> Grid:
    """Baseline pass-through for reference."""

    return [row[:] for row in grid]


def ring_fill_abstraction(grid: Grid) -> Grid:
    """Fill the central ring according to the quadrant imbalance, without rebalancing the 9s."""

    height = len(grid)
    width = len(grid[0])
    center_row, center_col = _center(grid)

    left_quadrants = 0
    right_quadrants = 0
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value != 9:
                continue
            dr = r - center_row
            dc = c - center_col
            if dc > 0 and dr != 0:
                right_quadrants += 1
            elif dc < 0 and dr != 0:
                left_quadrants += 1

    diff = right_quadrants - left_quadrants
    ring_order = [
        (center_row - 1, center_col - 1),
        (center_row - 1, center_col),
        (center_row - 1, center_col + 1),
        (center_row, center_col - 1),
        (center_row + 1, center_col - 1),
        (center_row + 1, center_col),
        (center_row + 1, center_col + 1),
        (center_row, center_col + 1),
        (center_row, center_col),
    ]
    steps = max(0, min(len(ring_order), 2 * diff))

    result = [row[:] for row in grid]
    for idx in range(steps):
        r, c = ring_order[idx]
        result[r][c] = 9
    return result


def balanced_relocation_abstraction(grid: Grid) -> Grid:
    """Full solver that relocates 9s via scoring and ring filling."""

    return solve_dd6b8c4b(grid)


ABSTRACTIONS: Sequence[Tuple[str, Abstraction]] = (
    ("identity", identity_abstraction),
    ("ring_fill", ring_fill_abstraction),
    ("balanced_relocation", balanced_relocation_abstraction),
)


def _load_dataset() -> dict:
    path = Path(__file__).parent / "arc2_samples" / "dd6b8c4b.json"
    with path.open() as handle:
        return json.load(handle)


def _iter_splits(data: dict) -> Iterable[Tuple[str, List[dict]]]:
    preferred = ["train", "test", "arc_gen", "arc-gen", "generated"]
    yielded = set()
    for key in preferred:
        if key in data:
            yielded.add(key)
            yield key, data[key]
    for key, value in data.items():
        if key not in yielded:
            yield key, value


def _format_grid(grid: Grid) -> str:
    return "\n".join("".join(str(cell) for cell in row) for row in grid)


def evaluate_abstractions() -> None:
    data = _load_dataset()
    splits = list(_iter_splits(data))

    for name, fn in ABSTRACTIONS:
        print(f"[{name}]")
        for split_name, cases in splits:
            if not cases:
                print(f"  {split_name}: no cases")
                continue

            if all("output" in case for case in cases):
                matches = 0
                first_fail = None
                for idx, case in enumerate(cases):
                    prediction = fn(case["input"])
                    if prediction == case["output"]:
                        matches += 1
                    elif first_fail is None:
                        first_fail = idx
                total = len(cases)
                acc = matches / total
                fail_str = first_fail if first_fail is not None else "-"
                print(
                    f"  {split_name}: {matches}/{total}"
                    f" acc={acc:.2%} first_fail={fail_str}"
                )
            else:
                sample_prediction = fn(cases[0]["input"])
                print(
                    f"  {split_name}: no targets available; sample prediction:\n"
                    f"{_format_grid(sample_prediction)}"
                )
        print()


if __name__ == "__main__":
    evaluate_abstractions()
