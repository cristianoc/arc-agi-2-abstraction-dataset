"""Abstraction experiments for ARC task c7f57c3e."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable, Iterable, List, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from arc2_samples import c7f57c3e as task

Grid = List[List[int]]


def _variant_a(grid: Grid) -> Grid:
    background = task._most_common_color(grid)
    palette = task._palette_without(grid, background)
    if len(palette) < 3:
        return task._copy_grid(grid)
    high = palette[-1]
    mid = max(c for c in palette if c < high)
    c1 = palette[0]
    c2 = palette[1]
    return task._apply_variant_a(grid, background, c1, c2, mid, high)


def _variant_b(grid: Grid) -> Grid:
    background = task._most_common_color(grid)
    palette = task._palette_without(grid, background)
    if len(palette) < 3:
        return task._copy_grid(grid)
    high = palette[-1]
    candidates = [c for c in palette if c < high]
    if not candidates:
        return task._copy_grid(grid)
    mid = max(candidates)
    pivot = palette[1] if len(palette) > 1 else palette[0]
    return task._apply_variant_b(grid, background, pivot, mid, high)


def _hybrid(grid: Grid) -> Grid:
    return task.solve_c7f57c3e(grid)


def _load_dataset() -> dict:
    path = Path("arc2_samples/c7f57c3e.json")
    with path.open() as fh:
        return json.load(fh)


def _evaluate_split(
    name: str,
    cases: Iterable[dict],
    solver: Callable[[Grid], Grid],
) -> tuple[int, int, int | None]:
    total = 0
    matches = 0
    first_failure: int | None = None
    for idx, case in enumerate(cases):
        if "output" not in case:
            continue
        total += 1
        predicted = solver(case["input"])
        if predicted == case["output"]:
            matches += 1
        elif first_failure is None:
            first_failure = idx
    return total, matches, first_failure


def _print_report(split: str, total: int, matches: int, first_failure: int | None) -> None:
    if total == 0:
        print(f"    {split}: no cases")
        return
    if matches == total:
        status = "all match"
    else:
        status = f"{matches}/{total} match"
    fail_str = "n/a" if first_failure is None else str(first_failure)
    print(f"    {split}: {status} (first failure: {fail_str})")


def main() -> None:
    data = _load_dataset()
    pipelines: Sequence[tuple[str, Callable[[Grid], Grid]]] = (
        ("variant_a", _variant_a),
        ("variant_b", _variant_b),
        ("hybrid", _hybrid),
    )
    splits = {
        "train": data.get("train", []),
        "test": data.get("test", []),
        "arc_gen": data.get("arc_gen", []),
    }

    for name, solver in pipelines:
        print(f"Abstraction: {name}")
        for split, cases in splits.items():
            total, matches, first_failure = _evaluate_split(split, cases, solver)
            _print_report(split, total, matches, first_failure)
        print()


if __name__ == "__main__":
    main()
