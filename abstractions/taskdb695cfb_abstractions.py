"""Abstractions explored for ARC task db695cfb.

The module documents lightweight abstractions that were evaluated while
solving the task. Every abstraction is exposed as a simple function and a
compact harness runs them on the available splits (train/test/arc-gen),
reporting match counts and first-failure indices.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Callable, List

Grid = List[List[int]]

TASK_ID = "db695cfb"
TASK_DIR = Path(__file__).with_suffix("").with_name("arc2_samples")
TASK_PATH = TASK_DIR / f"{TASK_ID}.json"
SOLVER_PATH = TASK_DIR / f"{TASK_ID}.py"


def load_task() -> dict:
    """Load the ARC task description from disk."""

    return json.loads(TASK_PATH.read_text())


def identity_abstraction(grid: Grid) -> Grid:
    """Baseline: return the grid unchanged."""

    return [row[:] for row in grid]


def connect_ones_abstraction(grid: Grid) -> Grid:
    """Fill diagonal segments connecting repeated `1`s, without 6-extensions."""

    if not grid:
        return []

    height, width = len(grid), len(grid[0])
    result = [row[:] for row in grid]

    ones = [(r, c) for r in range(height) for c in range(width) if grid[r][c] == 1]
    if len(ones) < 2:
        return result

    from collections import defaultdict

    groups_nwse = defaultdict(list)
    groups_nesw = defaultdict(list)
    for r, c in ones:
        groups_nwse[r - c].append((r, c))
        groups_nesw[r + c].append((r, c))

    for key, coords in groups_nwse.items():
        if len(coords) < 2:
            continue
        rows = [r for r, _ in coords]
        r_min, r_max = min(rows), max(rows)
        for r in range(r_min, r_max + 1):
            c = r - key
            if 0 <= c < width and grid[r][c] != 6:
                result[r][c] = 1

    for key, coords in groups_nesw.items():
        if len(coords) < 2:
            continue
        rows = [r for r, _ in coords]
        r_min, r_max = min(rows), max(rows)
        for r in range(r_min, r_max + 1):
            c = key - r
            if 0 <= c < width and grid[r][c] != 6:
                result[r][c] = 1

    return result


def load_solver() -> Callable[[Grid], Grid]:
    """Import the final solver from the analysis module."""

    spec = importlib.util.spec_from_file_location(f"task_{TASK_ID}_solver", SOLVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return getattr(module, f"solve_{TASK_ID}")


def connect_and_extend_abstraction(grid: Grid) -> Grid:
    """Wrapper that delegates to the finished solver (connect + extend)."""

    solver = load_solver()
    return solver(grid)


def render(grid: Grid) -> str:
    """Render a grid using hexadecimal characters for readability."""

    palette = "0123456789abcdef"
    return "\n".join("".join(palette[val] for val in row) for row in grid)


def evaluate_abstractions() -> None:
    """Run all abstractions on every split and report simple metrics."""

    data = load_task()
    abstractions: dict[str, Callable[[Grid], Grid]] = {
        "identity": identity_abstraction,
        "connect_ones": connect_ones_abstraction,
        "connect_and_extend": connect_and_extend_abstraction,
    }

    for split in ("train", "test", "arc-gen"):
        cases = data.get(split)
        if not cases:
            print(f"[{split}] no cases available")
            continue

        print(f"[{split}] {len(cases)} case(s)")
        has_outputs = "output" in cases[0]
        for name, fn in abstractions.items():
            matches = 0
            first_fail = None
            predictions: list[str] = []

            for idx, case in enumerate(cases):
                prediction = fn(case["input"])
                if has_outputs and "output" in case:
                    ok = prediction == case["output"]
                    matches += int(ok)
                    if not ok and first_fail is None:
                        first_fail = idx
                else:
                    predictions.append(render(prediction))

            if has_outputs:
                status = f"{matches}/{len(cases)} matched"
                fail_info = f"first failure={first_fail if first_fail is not None else 'None'}"
                print(f"  - {name:20s}: {status} ({fail_info})")
            else:
                print(f"  - {name:20s}: outputs unavailable; preview below")
                if predictions:
                    print(render(fn(cases[0]["input"])) + "\n")

        print()

    solver = load_solver()
    test_cases = data.get("test", [])
    if test_cases:
        print("[solver] predicted test output:")
        print(render(solver(test_cases[0]["input"])))


if __name__ == "__main__":
    evaluate_abstractions()

