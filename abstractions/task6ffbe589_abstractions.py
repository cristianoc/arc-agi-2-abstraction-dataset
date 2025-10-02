"""Abstraction experiments for ARC task 6ffbe589."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple


TASK_PATH = Path(__file__).parent / "arc2_samples" / "6ffbe589.json"


def _load_task() -> Dict[str, List[dict]]:
    return json.loads(TASK_PATH.read_text())


def _load_solver_module():
    solver_path = Path(__file__).parent / "arc2_samples" / "6ffbe589.py"
    spec = importlib.util.spec_from_file_location("task6ffbe589_solver", solver_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_SOLVER = _load_solver_module()


def _copy_grid(grid: List[List[int]]) -> List[List[int]]:
    return [row[:] for row in grid]


def abstraction_identity(grid: List[List[int]]) -> List[List[int]]:
    return _copy_grid(grid)


def abstraction_expanded_crop(grid: List[List[int]]) -> List[List[int]]:
    """Crop to the expanded dominant-color rectangle without further adjustments."""

    color = _SOLVER._dominant_color(grid)  # type: ignore[attr-defined]
    r0, r1, c0, c1 = _SOLVER._expand_if_needed(  # type: ignore[attr-defined]
        grid, *_SOLVER._best_border_rect(grid, color)  # type: ignore[attr-defined]
    )
    return [row[c0 : c1 + 1] for row in grid[r0 : r1 + 1]]


def abstraction_nearest_neighbor(grid: List[List[int]]) -> List[List[int]]:
    return _SOLVER.solve_6ffbe589(grid)  # type: ignore[attr-defined]


ABSTRACTIONS: Dict[str, Callable[[List[List[int]]], List[List[int]]]] = {
    "identity": abstraction_identity,
    "expanded_crop": abstraction_expanded_crop,
    "nearest_neighbor": abstraction_nearest_neighbor,
}


def _evaluate(task: Dict[str, List[dict]], name: str, fn: Callable[[List[List[int]]], List[List[int]]]) -> None:
    print(f"== {name} ==")
    for split in ("train", "test", "arc-gen"):
        entries = task.get(split, [])
        if not entries:
            continue

        total = sum(1 for entry in entries if "output" in entry)
        matches = 0
        first_failure = None

        for idx, entry in enumerate(entries):
            prediction = fn(entry["input"])
            target = entry.get("output")
            if target is None:
                continue
            if prediction == target:
                matches += 1
            elif first_failure is None:
                first_failure = idx

        print(
            f"  {split}: {matches}/{total} correct; first failure index: {first_failure}"
        )
    print()


def main() -> None:
    task = _load_task()
    for name, fn in ABSTRACTIONS.items():
        _evaluate(task, name, fn)

    test = task.get("test", [])
    if test:
        print("nearest_neighbor prediction on test[0]:")
        prediction = ABSTRACTIONS["nearest_neighbor"](test[0]["input"])
        for row in prediction:
            print("".join(str(value) for value in row))


if __name__ == "__main__":
    main()
