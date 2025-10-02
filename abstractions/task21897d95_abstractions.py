"""Abstractions and evaluation harness for ARC task 21897d95."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import importlib.util


def _load_solver() -> Callable[[Grid], Grid]:
    module_path = Path(__file__).with_name("arc2_samples") / "21897d95.py"
    spec = importlib.util.spec_from_file_location("solver_21897d95", module_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to locate solver module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module.solve_21897d95  # type: ignore[attr-defined]


solve_21897d95 = _load_solver()

Grid = List[List[int]]
Sample = Dict[str, Grid]


def load_dataset() -> Dict[str, List[Sample]]:
    path = Path(__file__).with_name("arc2_samples") / "21897d95.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def majority_projection(grid: Grid) -> Grid:
    """Crude baseline that fills each column with its dominant color."""
    if not grid or not grid[0]:
        return []

    height, width = len(grid), len(grid[0])
    column_majorities: List[int] = []
    for col in range(width):
        counts = Counter(row[col] for row in grid)
        color = max(counts.items(), key=lambda item: (item[1], -item[0]))[0]
        column_majorities.append(color)

    if height == width:
        return [[column_majorities[c] for c in range(width)] for _ in range(height)]

    return [[column_majorities[r] for _ in range(height)] for r in range(width)]


ABSTRACTIONS: List[Tuple[str, Callable[[Grid], Grid]]] = [
    ("majority_projection", majority_projection),
    ("data_driven_solver", solve_21897d95),
]


def evaluate_abstractions() -> None:
    data = load_dataset()
    splits: Dict[str, List[Sample]] = {
        "train": data.get("train", []),
        "test": data.get("test", []),
        "arc_gen": data.get("arc_gen", []),
    }

    for name, fn in ABSTRACTIONS:
        print(f"=== {name} ===")
        for split, cases in splits.items():
            if not cases:
                print(f"  {split}: no samples")
                continue

            available = [(idx, case) for idx, case in enumerate(cases) if "output" in case]
            successes = 0
            first_failure: Optional[int] = None

            for idx, case in available:
                prediction = fn(case["input"])
                if prediction == case["output"]:
                    successes += 1
                elif first_failure is None:
                    first_failure = idx

            if not available:
                print(f"  {split}: predictions generated (no ground truth)")
            else:
                ratio = f"{successes}/{len(available)}"
                print(f"  {split}: {ratio} correct, first failure {first_failure}")
        print()


if __name__ == "__main__":
    evaluate_abstractions()
