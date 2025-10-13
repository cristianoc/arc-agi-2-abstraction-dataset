"""Abstractions explored for ARC task 71e489b6."""

from __future__ import annotations

import json
from collections import deque
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple


OFFSETS4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "arc2_samples" / "71e489b6.json"
SOLVER_PATH = ROOT / "arc2_samples" / "71e489b6.py"


def _deep_copy(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    return [list(row) for row in grid]


def _zero_neighbors(grid: Sequence[Sequence[int]], r: int, c: int) -> int:
    h, w = len(grid), len(grid[0])
    return sum(
        1
        for dr, dc in OFFSETS4
        if 0 <= r + dr < h and 0 <= c + dc < w and grid[r + dr][c + dc] == 0
    )


def identity_abstraction(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    """Baseline identity mapping."""
    return _deep_copy(grid)


def majority_cleanup_abstraction(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    """Only apply the zero-majority cleanup step."""
    h, w = len(grid), len(grid[0])
    result = _deep_copy(grid)
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 1 and _zero_neighbors(grid, r, c) >= 3:
                result[r][c] = 0
    return result


_solver_module = SourceFileLoader("solver_71e489b6", str(SOLVER_PATH)).load_module()


def tip_halo_abstraction(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    """Full tip-detection with halo drawing (final solver)."""
    return _solver_module.solve_71e489b6(grid)


ABSTRACTIONS: List[Tuple[str, Callable[[Sequence[Sequence[int]]], List[List[int]]]]] = [
    ("identity", identity_abstraction),
    ("majority_cleanup", majority_cleanup_abstraction),
    ("tip_halo", tip_halo_abstraction),
]


def _evaluate_split(
    func: Callable[[Sequence[Sequence[int]]], List[List[int]]],
    entries: Iterable[Dict[str, Sequence[Sequence[int]]]],
) -> Tuple[Optional[int], int, Optional[int]]:
    """Return (#matches, total, first failure index) or (None, total, None) when no outputs."""
    matches = 0
    total = 0
    first_failure: Optional[int] = None
    has_outputs = False
    for idx, sample in enumerate(entries):
        total += 1
        prediction = func(sample["input"])
        if "output" not in sample:
            continue
        has_outputs = True
        if prediction == sample["output"]:
            matches += 1
        elif first_failure is None:
            first_failure = idx
    if not has_outputs:
        return None, total, None
    return matches, total, first_failure


def main() -> None:
    data = json.loads(DATA_PATH.read_text())
    splits = [
        ("train", data.get("train", [])),
        ("test", data.get("test", [])),
        ("arc_gen", data.get("arc_gen", [])),
    ]
    for name, func in ABSTRACTIONS:
        print(f"[{name}]")
        for split_name, entries in splits:
            if not entries:
                print(f"  {split_name}: 0 samples")
                continue
            matches, total, first_failure = _evaluate_split(func, entries)
            if matches is None:
                print(f"  {split_name}: predictions only (no labels)")
            else:
                ff_display = "-" if first_failure is None else str(first_failure)
                print(f"  {split_name}: {matches}/{total} matches, first_failure={ff_display}")
        print()


if __name__ == "__main__":
    main()
