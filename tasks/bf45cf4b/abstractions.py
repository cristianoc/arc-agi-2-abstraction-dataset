"""Abstractions explored for ARC task bf45cf4b.

This module enumerates the candidate pipelines considered and provides a tiny
evaluation harness so we can compare them on the available splits.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from analysis.arc2_samples.bf45cf4b import solve_bf45cf4b

Grid = List[List[int]]
Case = Tuple[Grid, Grid]
Abstraction = Callable[[Grid], Grid]


def identity_abstraction(grid: Grid) -> Grid:
    """Baseline: keep the grid unchanged for comparison."""

    return [row[:] for row in grid]


def mask_tiling_abstraction(grid: Grid) -> Grid:
    """Mask-driven tiling that matches the final solver."""

    return solve_bf45cf4b(grid)


ABSTRACTIONS: Sequence[Tuple[str, Abstraction]] = (
    ("identity", identity_abstraction),
    ("mask_tiling", mask_tiling_abstraction),
)


def _load_dataset() -> dict:
    path = Path(__file__).parent / "arc2_samples" / "bf45cf4b.json"
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
                prediction = fn(cases[0]["input"])
                print(
                    f"  {split_name}: no targets available; sample prediction:\n"
                    f"{_format_grid(prediction)}"
                )
        print()


if __name__ == "__main__":
    evaluate_abstractions()
