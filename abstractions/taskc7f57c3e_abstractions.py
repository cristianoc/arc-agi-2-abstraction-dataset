"""Abstractions explored for ARC task c7f57c3e."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable, List

from arc2_samples.c7f57c3e import (
    RADIUS,
    _encode_patch,
    _nearest_color,
    _training_memory,
)


Grid = List[List[int]]


def load_task() -> dict:
    path = Path("arc2_samples/c7f57c3e.json")
    return json.loads(path.read_text())


def abstraction_identity(grid: Grid) -> Grid:
    """Baseline: return a copy of the input grid."""

    return [row[:] for row in grid]


def abstraction_knn5(grid: Grid) -> Grid:
    """5×5 nearest-neighbour recolouring using training patterns."""

    pattern_to_color, patterns, colors = _training_memory()
    height = len(grid)
    width = len(grid[0])
    result = [[0] * width for _ in range(height)]
    for r in range(height):
        for c in range(width):
            pattern = _encode_patch(grid, r, c)
            result[r][c] = _nearest_color(pattern, pattern_to_color, patterns, colors)
    return result


def evaluate_abstractions(abstractions: Iterable[tuple[str, Callable[[Grid], Grid]]]) -> None:
    data = load_task()
    sections = ["train", "test", "arc-gen"]
    for name, fn in abstractions:
        print(f"=== {name} ===")
        for section in sections:
            entries = data.get(section) or []
            evaluable = [ex for ex in entries if "output" in ex]
            if not evaluable:
                if entries:
                    print(f" {section}: no reference outputs")
                continue
            correct = 0
            first_fail = None
            for idx, example in enumerate(evaluable):
                predicted = fn([row[:] for row in example["input"]])
                if predicted == example["output"]:
                    correct += 1
                elif first_fail is None:
                    first_fail = idx
            status = f"{correct}/{len(evaluable)}"
            if first_fail is not None:
                status += f" first_fail={first_fail}"
            print(f" {section}: {status}")
        print()


if __name__ == "__main__":
    evaluate_abstractions(
        [
            ("identity", abstraction_identity),
            ("knn5", abstraction_knn5),
        ]
    )
