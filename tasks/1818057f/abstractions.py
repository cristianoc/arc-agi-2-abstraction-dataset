"""Abstractions explored for ARC task 1818057f.

This module documents the small set of abstractions evaluated while solving the
task. Each abstraction is implemented as a function that transforms an input
grid. A lightweight harness executes them on the available splits (train/test)
and reports basic match statistics and first-failure indices when ground truth
is present.
"""

from __future__ import annotations

import json
import importlib.util
from pathlib import Path
from typing import Callable, Iterable, List, Sequence

Grid = List[List[int]]

TASK_PATH = Path(__file__).with_suffix("").with_name("arc2_samples") / "1818057f.json"
SOLVER_PATH = Path(__file__).with_suffix("").with_name("arc2_samples") / "1818057f.py"


def load_task() -> dict:
    """Load the ARC task description from disk."""

    return json.loads(TASK_PATH.read_text())


def identity_abstraction(grid: Grid) -> Grid:
    """Baseline abstraction: return the grid unchanged."""

    return [row[:] for row in grid]


def plus_painter_abstraction(grid: Grid) -> Grid:
    """Highlight every `4`-colored plus by repainting it with `8`.

    A plus is a center cell with four von-Neumann neighbours in color `4`; the
    output paints the center and neighbours with `8`, matching the final solver.
    """

    height = len(grid)
    width = len(grid[0]) if height else 0
    result = [row[:] for row in grid]

    for r in range(1, height - 1):
        for c in range(1, width - 1):
            if grid[r][c] != 4:
                continue

            if all(grid[r + dr][c + dc] == 4 for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                result[r][c] = 8
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    result[r + dr][c + dc] = 8

    return result


def load_solver() -> Callable[[Grid], Grid]:
    """Dynamically import the task solver from the analysis sample module."""

    spec = importlib.util.spec_from_file_location("task1818057f_solver", SOLVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.solve_1818057f


def render(grid: Grid) -> str:
    """Convert a grid to a compact hexadecimal string representation."""

    palette = "0123456789abcdef"
    return "\n".join("".join(palette[val] for val in row) for row in grid)


def evaluate_abstractions() -> None:
    """Evaluate each abstraction on train/test splits and print statistics."""

    data = load_task()
    abstractions: dict[str, Callable[[Grid], Grid]] = {
        "identity": identity_abstraction,
        "plus_painter": plus_painter_abstraction,
    }

    for split in ("train", "test", "arc-gen"):
        cases = data.get(split)
        if not cases:
            print(f"[{split}] no cases available")
            continue

        print(f"[{split}] {len(cases)} case(s)")
        for name, fn in abstractions.items():
            matches = 0
            first_fail = None
            predictions: list[str] = []

            for idx, case in enumerate(cases):
                prediction = fn(case["input"])
                if "output" in case:
                    ok = prediction == case["output"]
                    matches += int(ok)
                    if not ok and first_fail is None:
                        first_fail = idx
                else:
                    predictions.append(render(prediction))

            if cases and "output" in cases[0]:
                print(
                    f"  - {name:12s}: {matches}/{len(cases)} matched",
                    "first failure=" + (str(first_fail) if first_fail is not None else "None"),
                )
            else:
                print(f"  - {name:12s}: outputs unavailable; preview of first prediction below")
                if predictions:
                    print(render(fn(cases[0]["input"])) + "\n")

        print()

    # Compare the dedicated solver for completeness.
    solver = load_solver()
    print("[solver] predicted test output:")
    test_cases = data.get("test", [])
    if test_cases:
        predicted = solver(test_cases[0]["input"])
        print(render(predicted))
    else:
        print("No test cases present.")


if __name__ == "__main__":
    evaluate_abstractions()

