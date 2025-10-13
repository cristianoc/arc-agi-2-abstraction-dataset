"""Abstractions explored for ARC task 135a2760."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Callable, Iterable, List

Grid = List[List[int]]
Case = dict[str, Grid]

_DATA_PATH = Path("analysis/arc2_samples/135a2760.json")


def _load_cases(split: str) -> list[Case]:
    if not _DATA_PATH.exists():
        return []
    with _DATA_PATH.open() as fh:
        data = json.load(fh)
    return list(data.get(split, []))


def _identity(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _two_color_parity(grid: Grid) -> Grid:
    """Enforce a simple alternating pattern for rows with exactly two inner colors."""
    result = [row[:] for row in grid]
    for row in result:
        if len(row) <= 4:
            continue
        inner = row[2:-2]
        if not inner:
            continue
        palette = [inner[0]]
        for value in inner:
            if value not in palette:
                palette.append(value)
            if len(palette) == 2:
                break
        if len(palette) != 2:
            continue
        first, second = palette
        for idx, value in enumerate(inner):
            expected = first if idx % 2 == 0 else second
            if value != expected:
                row[idx + 2] = expected
    return result


def _load_solver() -> Callable[[Grid], Grid]:
    spec = importlib.util.spec_from_file_location(
        "task135a2760", _DATA_PATH.with_suffix(".py")
    )
    if spec is None or spec.loader is None:
        raise ImportError("cannot load solver module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.solve_135a2760


def _majority_periodic(grid: Grid) -> Grid:
    solver = _load_solver()
    return solver(grid)


_ABSTRACTIONS: list[tuple[str, Callable[[Grid], Grid]]] = [
    ("identity", _identity),
    ("two_color_parity", _two_color_parity),
    ("majority_periodic", _majority_periodic),
]


def _evaluate_split(
    abstraction: Callable[[Grid], Grid],
    cases: Iterable[Case],
) -> tuple[int, int, int | None]:
    indexed_cases = [(idx, case) for idx, case in enumerate(cases) if "output" in case]
    total = len(indexed_cases)
    failures: list[int] = []
    for idx, case in indexed_cases:
        prediction = abstraction(case["input"])
        if prediction != case["output"]:
            failures.append(idx)
    solved = total - len(failures)
    first_failure = failures[0] if failures else None
    return solved, total, first_failure


def _format_result(name: str, split: str, solved: int, total: int, first_fail: int | None) -> str:
    if total == 0:
        return f"{name:>20s} | {split:<8s} | (no cases)"
    frac = solved / total * 100.0
    failure = "-" if first_fail is None else str(first_fail)
    return f"{name:>20s} | {split:<8s} | {solved:2d}/{total:<2d} ({frac:5.1f}%) | first fail: {failure}"


def main() -> None:
    splits = {split: _load_cases(split) for split in ("train", "test", "arc_gen")}
    for name, fn in _ABSTRACTIONS:
        for split_name, cases in splits.items():
            solved, total, first_fail = _evaluate_split(fn, cases)
            print(_format_result(name, split_name, solved, total, first_fail))
        print("-" * 72)


if __name__ == "__main__":
    main()
