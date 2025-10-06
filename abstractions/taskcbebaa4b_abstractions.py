"""Abstraction experiments for task cbebaa4b."""

from __future__ import annotations

import json
import importlib.util
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple


Grid = List[List[int]]
Abstraction = Callable[[Grid], Optional[Grid]]


def load_task() -> dict:
    path = Path("analysis/arc2_samples/cbebaa4b.json")
    return json.loads(path.read_text())


def load_solver():
    path = Path("analysis/arc2_samples/cbebaa4b.py").resolve()
    spec = importlib.util.spec_from_file_location("cbebaa4b_solver", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module.solve_cbebaa4b


solve_cbebaa4b = load_solver()


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def get_bbox(points: Sequence[Tuple[int, int]]) -> Tuple[int, int, int, int]:
    ys = [y for y, _ in points]
    xs = [x for _, x in points]
    return min(ys), max(ys), min(xs), max(xs)


def identity_abstraction(grid: Grid) -> Grid:
    return copy_grid(grid)


def naive_stack_abstraction(grid: Grid) -> Optional[Grid]:
    h, w = len(grid), len(grid[0])
    color_cells: Dict[int, List[Tuple[int, int]]] = {}
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            if val not in (0, 2):
                color_cells.setdefault(val, []).append((y, x))
    if not color_cells:
        return None

    door_color = None
    for color, cells in color_cells.items():
        ymin, ymax, xmin, xmax = get_bbox(cells)
        if ymax - ymin + 1 == 3 and xmax - xmin + 1 == 3 and len(cells) == 9:
            door_color = color
            break
    if door_color is None:
        return None

    ymin, _, xmin, _ = get_bbox(color_cells[door_color])
    out = [[0] * w for _ in range(h)]
    # keep the door where it already sits
    for y, x in color_cells[door_color]:
        out[y][x] = door_color

    slot_top = ymin
    for color, cells in sorted(color_cells.items()):
        if color == door_color:
            continue
        cymin, cymax, cxmin, cxmax = get_bbox(cells)
        height = cymax - cymin + 1
        slot_top -= height
        if slot_top < 0:
            return None
        shift_y = slot_top - cymin
        shift_x = xmin - cxmin
        for y, x in cells:
            ny, nx = y + shift_y, x + shift_x
            if not (0 <= ny < h and 0 <= nx < w):
                return None
            out[ny][nx] = color
    return out


def connector_matching_abstraction(grid: Grid) -> Grid:
    return solve_cbebaa4b(copy_grid(grid))


def evaluate(split: str, cases: Sequence[dict], abstractions: Sequence[Tuple[str, Abstraction]]) -> None:
    print(f"[{split}] {len(cases)} cases")
    for name, fn in abstractions:
        total = len(cases)
        matches = 0
        first_fail: Optional[int] = None
        for idx, case in enumerate(cases):
            pred = fn(copy_grid(case["input"]))
            if pred is None:
                pred = case["input"]
            if pred == case.get("output", pred):
                matches += 1
            elif first_fail is None and "output" in case:
                first_fail = idx
        status = f"{matches}/{total}"
        if first_fail is not None:
            status += f" (first fail at {first_fail})"
        print(f"  {name:25s} -> {status}")
    print()


def main() -> None:
    task = load_task()
    abstractions: Sequence[Tuple[str, Abstraction]] = [
        ("identity", identity_abstraction),
        ("naive_stack", naive_stack_abstraction),
        ("connector_matching", connector_matching_abstraction),
    ]

    evaluate("train", task.get("train", []), abstractions)
    evaluate("test", task.get("test", []), abstractions)
    evaluate("arc-gen", task.get("arc-gen", []), abstractions)


if __name__ == "__main__":
    main()
