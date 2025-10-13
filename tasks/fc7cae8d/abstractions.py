"""Abstraction explorations for ARC task fc7cae8d."""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence

TASK_PATH = Path(__file__).with_name("arc2_samples") / "fc7cae8d.json"


Grid = List[List[int]]


@dataclass
class Component:
    color: int
    cells: Sequence[tuple[int, int]]
    touches_border: bool


def _load_task() -> Dict[str, List[Dict[str, Grid]]]:
    with TASK_PATH.open() as f:
        return json.load(f)


def _largest_component(grid: Grid) -> Component:
    height = len(grid)
    width = len(grid[0])
    visited = [[False] * width for _ in range(height)]

    best_interior: Optional[Component] = None
    best_any: Optional[Component] = None

    for r in range(height):
        for c in range(width):
            if visited[r][c]:
                continue
            color = grid[r][c]
            queue = deque([(r, c)])
            visited[r][c] = True
            cells = []
            touches_border = False

            while queue:
                rr, cc = queue.popleft()
                cells.append((rr, cc))
                if rr in (0, height - 1) or cc in (0, width - 1):
                    touches_border = True
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width:
                        if not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            queue.append((nr, nc))

            component = Component(color=color, cells=cells, touches_border=touches_border)

            if best_any is None or len(cells) > len(best_any.cells):
                best_any = component
            if not touches_border:
                if best_interior is None or len(cells) > len(best_interior.cells):
                    best_interior = component

    if best_interior is not None:
        return best_interior
    assert best_any is not None
    return best_any


def _crop(grid: Grid, cells: Iterable[tuple[int, int]]) -> Grid:
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    r0, r1 = min(rows), max(rows)
    c0, c1 = min(cols), max(cols)
    return [row[c0 : c1 + 1] for row in grid[r0 : r1 + 1]]


def _rotate_ccw(grid: Grid) -> Grid:
    return [list(row) for row in zip(*grid)][::-1]


def _flip_horizontal(grid: Grid) -> Grid:
    return [list(reversed(row)) for row in grid]


def _rotate_pipeline(grid: Grid, *, flip_mode: str) -> Grid:
    component = _largest_component(grid)
    cropped = _crop(grid, component.cells)
    rotated = _rotate_ccw(cropped)

    if flip_mode == "never":
        return rotated
    if flip_mode == "always":
        return _flip_horizontal(rotated)
    if flip_mode != "heuristic":
        raise ValueError(f"Unknown flip_mode: {flip_mode}")

    left_column = [row[0] for row in rotated]
    right_column = [row[-1] for row in rotated]
    dominant = component.color

    left_primary = sum(1 for val in left_column if val == dominant)
    right_primary = sum(1 for val in right_column if val == dominant)
    left_impurity = len(left_column) - left_primary
    right_impurity = len(right_column) - right_primary

    left_score = (left_primary, -left_impurity)
    right_score = (right_primary, -right_impurity)

    if left_score < right_score:
        return _flip_horizontal(rotated)
    return rotated


# --- Abstractions ---------------------------------------------------------


def identity_baseline(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def rotate_component_ccw(grid: Grid) -> Grid:
    return _rotate_pipeline(grid, flip_mode="never")


def rotate_component_ccw_always_flip(grid: Grid) -> Grid:
    return _rotate_pipeline(grid, flip_mode="always")


def rotate_component_ccw_column_heuristic(grid: Grid) -> Grid:
    return _rotate_pipeline(grid, flip_mode="heuristic")


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": identity_baseline,
    "rotate_ccw": rotate_component_ccw,
    "rotate_ccw_flip": rotate_component_ccw_always_flip,
    "rotate_ccw_column_heuristic": rotate_component_ccw_column_heuristic,
}


def _evaluate(fn: Callable[[Grid], Grid], cases: Sequence[Dict[str, Grid]]):
    solved = 0
    evaluated = 0
    first_failure = None

    for idx, case in enumerate(cases):
        prediction = fn(case["input"])
        if "output" not in case:
            continue
        evaluated += 1
        if prediction == case["output"]:
            solved += 1
        elif first_failure is None:
            first_failure = idx

    accuracy = solved / evaluated if evaluated else None
    return accuracy, solved, evaluated, first_failure


def _format_result(accuracy: Optional[float], solved: int, evaluated: int, first_failure: Optional[int]) -> str:
    if accuracy is None:
        return "n/a (no targets)"
    percent = accuracy * 100
    failure_str = "-" if first_failure is None else str(first_failure)
    return f"{percent:5.1f}% ({solved}/{evaluated}), first fail: {failure_str}"


def main() -> None:
    task = _load_task()
    splits = {
        "train": task.get("train", []),
        "test": task.get("test", []),
    }

    arc_gen_path = TASK_PATH.with_name(f"{TASK_PATH.stem}_arcgen.json")
    if arc_gen_path.exists():
        with arc_gen_path.open() as f:
            splits["arc-gen"] = json.load(f)

    for name, fn in ABSTRACTIONS.items():
        print(f"=== {name} ===")
        for split_name, cases in splits.items():
            accuracy, solved, evaluated, failure = _evaluate(fn, cases)
            print(f"  {split_name:7s}: {_format_result(accuracy, solved, evaluated, failure)}")
        print()


if __name__ == "__main__":
    main()
