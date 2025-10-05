"""Abstractions explored for ARC task b0039139."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable, List

from arc2_samples.b0039139 import solve_b0039139


Grid = List[List[int]]
Example = dict[str, Grid]
Solver = Callable[[Grid], Grid]


def identity_solver(grid: Grid) -> Grid:
    """Baseline identity transformation."""

    return [row[:] for row in grid]


def tiling_solver(grid: Grid) -> Grid:
    """Wrapper around the refined segment-tiling solver."""

    return solve_b0039139(grid)


SOLVERS: list[tuple[str, Solver]] = [
    ("identity", identity_solver),
    ("segment_tiling", tiling_solver),
]


def load_dataset() -> dict[str, Iterable[Example]]:
    data_path = Path(__file__).with_name("arc2_samples") / "b0039139.json"
    with data_path.open() as fh:
        return json.load(fh)


def evaluate_solver(name: str, solver: Solver, dataset: dict[str, Iterable[Example]]) -> None:
    print(f"=== {name} ===")
    for split in ("train", "test", "arc_gen"):
        samples: List[Example] = list(dataset.get(split, []))
        if not samples:
            print(f"  {split}: no samples available")
            continue
        if split == "train":
            correct = 0
            first_fail: int | None = None
            for idx, sample in enumerate(samples):
                prediction = solver(sample["input"])
                if sample["output"] == prediction:
                    correct += 1
                elif first_fail is None:
                    first_fail = idx
            summary = f"{correct}/{len(samples)} correct"
            if first_fail is not None:
                summary += f", first failure at {split}[{first_fail}]"
            else:
                summary += ", first failure: None"
            print(f"  {split}: {summary}")
        else:
            shapes = [f"{len(pred)}x{len(pred[0])}" for pred in (solver(s["input"]) for s in samples)]
            print(f"  {split}: generated {len(samples)} predictions; shapes: {', '.join(shapes)}")


def main() -> None:
    dataset = load_dataset()
    for name, solver in SOLVERS:
        evaluate_solver(name, solver, dataset)


if __name__ == "__main__":
    main()
