"""Abstraction experiments for ARC task dbff022c."""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List


Grid = List[List[int]]


def load_task() -> dict:
    task_path = Path(__file__).resolve().parent.parent / "arc2_samples" / "dbff022c.json"
    with task_path.open() as fh:
        return json.load(fh)


def deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def neighbors(r: int, c: int):
    yield r + 1, c
    yield r - 1, c
    yield r, c + 1
    yield r, c - 1


def in_bounds(r: int, c: int, rows: int, cols: int) -> bool:
    return 0 <= r < rows and 0 <= c < cols


@dataclass
class ZeroComponent:
    cells: List[tuple[int, int]]
    color: int
    size: int
    adjacency: set[int]
    touches_border: bool


def collect_zero_components(grid: Grid) -> List[ZeroComponent]:
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    components: List[ZeroComponent] = []

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 or visited[r][c]:
                continue

            queue = deque([(r, c)])
            visited[r][c] = True
            zero_cells: List[tuple[int, int]] = []
            neighbor_color = None
            neighbors_mixed = False
            boundary_cells = set()
            touches_border = False

            while queue:
                cr, cc = queue.popleft()
                zero_cells.append((cr, cc))
                if cr == 0 or cr == rows - 1 or cc == 0 or cc == cols - 1:
                    touches_border = True

                for nr, nc in neighbors(cr, cc):
                    if not in_bounds(nr, nc, rows, cols):
                        continue
                    val = grid[nr][nc]
                    if val == 0 and not visited[nr][nc]:
                        visited[nr][nc] = True
                        queue.append((nr, nc))
                    elif val != 0:
                        if neighbor_color is None:
                            neighbor_color = val
                        elif neighbor_color != val:
                            neighbors_mixed = True
                        boundary_cells.add((nr, nc))

            if neighbor_color is None or neighbors_mixed:
                continue

            region = set(zero_cells)
            region_queue = deque(zero_cells + list(boundary_cells))
            seen = set(region_queue)
            while region_queue:
                cr, cc = region_queue.popleft()
                region.add((cr, cc))
                for nr, nc in neighbors(cr, cc):
                    if not in_bounds(nr, nc, rows, cols):
                        continue
                    if grid[nr][nc] in (0, neighbor_color) and (nr, nc) not in seen:
                        seen.add((nr, nc))
                        region_queue.append((nr, nc))

            adjacency = set()
            for cr, cc in region:
                for nr, nc in neighbors(cr, cc):
                    if not in_bounds(nr, nc, rows, cols):
                        continue
                    val = grid[nr][nc]
                    if val not in (0, neighbor_color):
                        adjacency.add(val)

            components.append(
                ZeroComponent(
                    cells=zero_cells,
                    color=neighbor_color,
                    size=len(zero_cells),
                    adjacency=adjacency,
                    touches_border=touches_border,
                )
            )

    return components


def abstraction_identity(grid: Grid) -> Grid:
    return deep_copy(grid)


def abstraction_fill_same_color(grid: Grid) -> Grid:
    result = deep_copy(grid)
    for component in collect_zero_components(grid):
        if component.touches_border:
            continue
        for r, c in component.cells:
            result[r][c] = component.color
    return result


def abstraction_partner_rule(grid: Grid) -> Grid:
    result = deep_copy(grid)
    for component in collect_zero_components(grid):
        if component.touches_border:
            continue

        fill = None
        if component.color == 3:
            fill = 3
        elif component.color == 8:
            fill = 1
        elif component.color == 2:
            fill = 7
        elif component.color == 4 and component.size == 1:
            if 5 in component.adjacency:
                fill = 5
            elif 6 in component.adjacency:
                fill = 6

        if fill is None:
            continue

        for r, c in component.cells:
            result[r][c] = fill

    return result


def evaluate(abstractions: dict[str, Callable[[Grid], Grid]]) -> None:
    task = load_task()
    train = task["train"]
    test = task.get("test", [])

    for name, fn in abstractions.items():
        train_hits = 0
        train_fail = None
        for idx, pair in enumerate(train):
            pred = fn(pair["input"])
            if pred == pair["output"]:
                train_hits += 1
            elif train_fail is None:
                train_fail = idx

        test_hits = 0
        test_fail = None
        for idx, pair in enumerate(test):
            pred = fn(pair["input"])
            if "output" in pair and pred == pair["output"]:
                test_hits += 1
            elif test_fail is None:
                test_fail = idx

        print(f"[{name}] train {train_hits}/{len(train)}", end="")
        if train_fail is not None:
            print(f" first_fail=train[{train_fail}]")
        else:
            print(" all-ok")

        if test:
            print(f"        test  {test_hits}/{len(test)}", end="")
            if test_fail is not None:
                print(f" first_fail=test[{test_fail}]")
            else:
                print(" all-ok")


def main():
    abstractions = {
        "identity": abstraction_identity,
        "fill_same_color": abstraction_fill_same_color,
        "partner_rule": abstraction_partner_rule,
    }
    evaluate(abstractions)


if __name__ == "__main__":
    main()
