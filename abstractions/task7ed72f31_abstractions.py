"""Abstractions explored for ARC task 7ed72f31.

Each abstraction is a lightweight transformation or heuristic that was
evaluated while solving the task. A compact harness runs them on the
available splits (train/test/arc-gen), reporting match counts and the
first failing example index per abstraction.
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter, deque
from pathlib import Path
from typing import Callable, List

Grid = List[List[int]]

TASK_ID = "7ed72f31"
TASK_DIR = Path(__file__).with_suffix("").with_name("arc2_samples")
TASK_PATH = TASK_DIR / f"{TASK_ID}.json"
SOLVER_PATH = TASK_DIR / f"{TASK_ID}.py"


def load_task() -> dict:
    """Load the ARC task description from disk."""

    return json.loads(TASK_PATH.read_text())


def identity_abstraction(grid: Grid) -> Grid:
    """Baseline: leave the grid unchanged."""

    return [row[:] for row in grid]


def nearest_axis_reflection_abstraction(grid: Grid) -> Grid:
    """Mirror non-axis objects across the closest axis of color 2."""

    if not grid:
        return []

    height, width = len(grid), len(grid[0])
    background = Counter(val for row in grid for val in row).most_common(1)[0][0]

    axes = []
    seen = [[False] * width for _ in range(height)]

    for y in range(height):
        for x in range(width):
            if grid[y][x] != 2 or seen[y][x]:
                continue
            queue = deque([(y, x)])
            seen[y][x] = True
            comp: list[tuple[int, int]] = []
            while queue:
                cy, cx = queue.popleft()
                comp.append((cy, cx))
                for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < height and 0 <= nx < width and not seen[ny][nx] and grid[ny][nx] == 2:
                        seen[ny][nx] = True
                        queue.append((ny, nx))

            rows = [r for r, _ in comp]
            cols = [c for _, c in comp]
            min_r, max_r = min(rows), max(rows)
            min_c, max_c = min(cols), max(cols)
            unique_rows = len(set(rows))
            unique_cols = len(set(cols))

            if len(comp) == 1:
                axis_type = "point"
            elif unique_rows == 1 and unique_cols > 1:
                axis_type = "horizontal"
            elif unique_cols == 1 and unique_rows > 1:
                axis_type = "vertical"
            else:
                axis_type = "block"

            axes.append(
                {
                    "type": axis_type,
                    "cells": set(comp),
                    "min_r": min_r,
                    "max_r": max_r,
                    "min_c": min_c,
                    "max_c": max_c,
                    "center_r": (min_r + max_r) / 2,
                    "center_c": (min_c + max_c) / 2,
                }
            )

    def axis_applicable(axis: dict, y: int, x: int) -> bool:
        if (y, x) in axis["cells"]:
            return False
        atype = axis["type"]
        if atype == "vertical":
            return axis["min_r"] <= y <= axis["max_r"]
        if atype == "horizontal":
            return axis["min_c"] <= x <= axis["max_c"]
        if atype == "block":
            return axis["min_r"] <= y <= axis["max_r"] or axis["min_c"] <= x <= axis["max_c"]
        return True

    def reflect(axis: dict, y: int, x: int) -> tuple[int, int]:
        atype = axis["type"]
        cy = axis["center_r"]
        cx = axis["center_c"]
        if atype == "vertical":
            return y, int(round(2 * cx - x))
        if atype == "horizontal":
            return int(round(2 * cy - y)), x
        ny = int(round(2 * cy - y))
        nx = int(round(2 * cx - x))
        return ny, nx

    result = [row[:] for row in grid]
    original = [(r, c, grid[r][c]) for r in range(height) for c in range(width)]
    for r, c, value in original:
        if value == 2 or value == background:
            continue

        best_axis = None
        best_dist = None
        for axis in axes:
            if not axis_applicable(axis, r, c):
                continue
            atype = axis["type"]
            if atype == "vertical":
                distance = abs(c - axis["center_c"])
            elif atype == "horizontal":
                distance = abs(r - axis["center_r"])
            else:
                distance = abs(r - axis["center_r"]) + abs(c - axis["center_c"])
            if best_dist is None or distance < best_dist:
                best_dist = distance
                best_axis = axis

        if best_axis is None:
            continue

        nr, nc = reflect(best_axis, r, c)
        if 0 <= nr < height and 0 <= nc < width and result[nr][nc] == background:
            result[nr][nc] = value

    return result


def solver_wrapper(grid: Grid) -> Grid:
    """Delegate to the final solver implementation."""

    spec = importlib.util.spec_from_file_location(f"task_{TASK_ID}_solver", SOLVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[assignment]
    solver = getattr(module, f"solve_{TASK_ID}")
    return solver(grid)


def render(grid: Grid) -> str:
    """Render grid values using hexadecimal digits."""

    palette = "0123456789abcdef"
    return "\n".join("".join(palette[val] for val in row) for row in grid)


def evaluate_abstractions() -> None:
    """Run each abstraction on every available split and report matches."""

    data = load_task()
    abstractions: dict[str, Callable[[Grid], Grid]] = {
        "identity": identity_abstraction,
        "nearest_axis_reflection": nearest_axis_reflection_abstraction,
        "final_solver": solver_wrapper,
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
            previews: list[str] = []

            for idx, case in enumerate(cases):
                prediction = fn(case["input"])
                if has_outputs and "output" in case:
                    ok = prediction == case["output"]
                    matches += int(ok)
                    if not ok and first_fail is None:
                        first_fail = idx
                else:
                    previews.append(render(prediction))

            if has_outputs:
                summary = f"{matches}/{len(cases)} matched"
                fail_info = first_fail if first_fail is not None else "None"
                print(f"  - {name:24s}: {summary} (first failure={fail_info})")
            else:
                print(f"  - {name:24s}: outputs unavailable; preview below")
                if previews:
                    print(previews[0])

        print()

    test_cases = data.get("test", [])
    if test_cases:
        solver = solver_wrapper
        print("[solver] predicted test output:")
        print(render(solver(test_cases[0]["input"])))


if __name__ == "__main__":
    evaluate_abstractions()
