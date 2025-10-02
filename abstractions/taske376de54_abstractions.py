"""Abstractions explored for ARC task e376de54.

This module lists the candidate pipelines considered while iterating on the
task as well as a tiny harness for spot-checking their performance on the
available splits.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Callable, Iterable, List, Sequence, Tuple

Grid = List[List[int]]
Case = Tuple[Grid, Grid]
Abstraction = Callable[[Grid], Grid]


def identity_abstraction(grid: Grid) -> Grid:
    """Baseline: copy the grid unchanged."""

    return [row[:] for row in grid]


def _load_solver() -> Abstraction:
    module_path = Path(__file__).parent / "arc2_samples" / "e376de54.py"
    spec = importlib.util.spec_from_file_location("taske376de54_solver", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load solver module at {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.solve_e376de54


SOLVER = _load_solver()


def median_line_alignment_abstraction(grid: Grid) -> Grid:
    """Orientation-aware alignment used in the final solver."""

    return SOLVER(grid)


ABSTRACTIONS: Sequence[Tuple[str, Abstraction]] = (
    ("identity", identity_abstraction),
    ("median_line_alignment", median_line_alignment_abstraction),
)


def _load_dataset() -> dict:
    path = Path(__file__).parent / "arc2_samples" / "e376de54.json"
    with path.open() as handle:
        return json.load(handle)


def _iter_splits(data: dict) -> Iterable[Tuple[str, List[dict]]]:
    ordered_keys = ["train", "test", "arc_gen", "arc-gen", "generated"]
    seen = set()
    for key in ordered_keys:
        if key in data:
            seen.add(key)
            yield key, data[key]
    for key, value in data.items():
        if key not in seen:
            yield key, value


def _grids_equal(a: Grid, b: Grid) -> bool:
    return a == b


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
                    target = case["output"]
                    if _grids_equal(prediction, target):
                        matches += 1
                    elif first_fail is None:
                        first_fail = idx
                accuracy = matches / len(cases)
                fail_display = first_fail if first_fail is not None else "-"
                print(
                    f"  {split_name}: {matches}/{len(cases)}"
                    f" acc={accuracy:.2%} first_fail={fail_display}"
                )
            else:
                # No reference outputs; show the first prediction for manual vetting.
                prediction = fn(cases[0]["input"])
                print(f"  {split_name}: no targets available; sample prediction:\n{_format_grid(prediction)}")
        print()


if __name__ == "__main__":
    evaluate_abstractions()
