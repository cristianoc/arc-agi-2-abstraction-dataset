"""Abstractions explored for ARC task 36a08778.

The module records the intermediate abstraction attempts that led to the final
solver. Each abstraction is implemented as a pure function and evaluated by a
lightweight harness on the available splits (train/test/arc-gen).
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Callable, List

Grid = List[List[int]]

TASK_PATH = Path(__file__).with_name("arc2_samples") / "36a08778.json"
SOLVER_PATH = Path(__file__).with_name("arc2_samples") / "36a08778.py"


def load_task() -> dict:
    """Load the ARC task description from disk."""

    return json.loads(TASK_PATH.read_text())


def identity_abstraction(grid: Grid) -> Grid:
    """Baseline abstraction: return the grid unchanged."""

    return [row[:] for row in grid]


def _iter_runs_from_list(row: List[int], target: int = 2) -> Iterable[tuple[int, int]]:
    """Yield contiguous [start, end] spans of the target colour within a list."""

    start = None
    for idx, value in enumerate(row):
        if value == target:
            if start is None:
                start = idx
        elif start is not None:
            yield start, idx - 1
            start = None
    if start is not None:
        yield start, len(row) - 1


def _scaffold_abstraction(grid: Grid, *, process_runs: bool, require_scaffold_touch: bool) -> Grid:
    """Shared implementation for the scaffold-based abstractions."""

    height = len(grid)
    width = len(grid[0]) if height else 0
    result = [row[:] for row in grid]

    # Seed columns are the positions that already contain colour 6 in the top
    # two rows; extend them downward until blocked by colour 2.
    seed_cols = set()
    for r in range(min(2, height)):
        for c, value in enumerate(grid[r]):
            if value == 6:
                seed_cols.add(c)

    for c in seed_cols:
        for r in range(height):
            if grid[r][c] == 2:
                break
            if result[r][c] == 7:
                result[r][c] = 6

    if not process_runs or height <= 2:
        return result

    for r in range(2, height):
        for left, right in _iter_runs_from_list(grid[r]):
            run_len = right - left + 1

            if require_scaffold_touch:
                touches_scaffold = any(
                    result[r - 1][c] == 6 or result[r][c] == 6
                    for c in range(left, right + 1)
                )
                if not touches_scaffold:
                    continue

            left_neighbor = left - 1 if left > 0 else None
            right_neighbor = right + 1 if right + 1 < width else None

            if run_len > 1:
                for c in range(max(0, left - 1), min(width, right + 2)):
                    if result[r - 1][c] == 7:
                        result[r - 1][c] = 6
            else:
                c = right + 1
                if c < width and result[r - 1][c] == 7:
                    result[r - 1][c] = 6

            if run_len > 1 and left_neighbor is not None and result[r][left_neighbor] == 7:
                result[r][left_neighbor] = 6
            if right_neighbor is not None and result[r][right_neighbor] == 7:
                result[r][right_neighbor] = 6

            if run_len > 1 and left_neighbor is not None:
                for rr in range(r + 1, height):
                    if grid[rr][left_neighbor] == 2:
                        break
                    if result[rr][left_neighbor] == 7:
                        result[rr][left_neighbor] = 6

            if right_neighbor is not None:
                for rr in range(r + 1, height):
                    if grid[rr][right_neighbor] == 2:
                        break
                    if result[rr][right_neighbor] == 7:
                        result[rr][right_neighbor] = 6

    return result


def scaffold_seed_extension(grid: Grid) -> Grid:
    """Only extend the scaffold columns downward (first abstraction attempt)."""

    return _scaffold_abstraction(grid, process_runs=False, require_scaffold_touch=False)


def scaffold_unfiltered(grid: Grid) -> Grid:
    """Extend scaffolds and wrap every 2-run, regardless of connectivity."""

    return _scaffold_abstraction(grid, process_runs=True, require_scaffold_touch=False)


def scaffold_filtered(grid: Grid) -> Grid:
    """Final abstraction: wrap only the runs touched by existing scaffold."""

    return _scaffold_abstraction(grid, process_runs=True, require_scaffold_touch=True)


def load_solver() -> Callable[[Grid], Grid]:
    """Import the reference solver from the sample module."""

    spec = importlib.util.spec_from_file_location("task36a08778_solver", SOLVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.solve_36a08778


def render(grid: Grid) -> str:
    """Render a grid as a hexadecimal string for compact display."""

    palette = "0123456789abcdef"
    return "\n".join("".join(palette[val] for val in row) for row in grid)


def evaluate_abstractions() -> None:
    """Run all registered abstractions on each split and report metrics."""

    data = load_task()
    abstractions: dict[str, Callable[[Grid], Grid]] = {
        "identity": identity_abstraction,
        "seed_extension": scaffold_seed_extension,
        "scaffold_unfiltered": scaffold_unfiltered,
        "scaffold_filtered": scaffold_filtered,
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
            previews: list[str] = []

            for idx, case in enumerate(cases):
                prediction = fn(case["input"])
                if "output" in case:
                    ok = prediction == case["output"]
                    matches += int(ok)
                    if not ok and first_fail is None:
                        first_fail = idx
                else:
                    previews.append(render(prediction))

            if "output" in cases[0]:
                print(
                    f"  - {name:18s}: {matches}/{len(cases)} matched",
                    "first failure=" + (str(first_fail) if first_fail is not None else "None"),
                )
            else:
                print(f"  - {name:18s}: outputs unavailable; showing first prediction below")
                if previews:
                    print(previews[0] + "\n")

        print()

    solver = load_solver()
    print("[solver] predicted test output(s):")
    for idx, case in enumerate(data.get("test", [])):
        predicted = solver(case["input"])
        print(f"  test[{idx}]:\n{render(predicted)}\n")


if __name__ == "__main__":
    evaluate_abstractions()
