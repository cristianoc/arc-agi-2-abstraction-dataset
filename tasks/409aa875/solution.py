"""Solver for ARC-AGI-2 task 409aa875."""

from collections import Counter, deque
from typing import Dict, List, Tuple


Grid = List[List[int]]
Component = Dict[str, object]

SHIFT_ROWS = 5


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _background_color(grid: Grid) -> int:
    flat = [cell for row in grid for cell in row]
    return Counter(flat).most_common(1)[0][0]


def _connected_components(grid: Grid, background: int) -> List[Component]:
    height = len(grid)
    width = len(grid[0])
    seen = [[False] * width for _ in range(height)]
    components: List[Component] = []

    for r in range(height):
        for c in range(width):
            value = grid[r][c]
            if value == background or seen[r][c]:
                continue

            stack = [(r, c)]
            seen[r][c] = True
            cells: List[Tuple[int, int]] = []
            r_min = r_max = r
            c_min = c_max = c

            while stack:
                y, x = stack.pop()
                cells.append((y, x))
                r_min = min(r_min, y)
                r_max = max(r_max, y)
                c_min = min(c_min, x)
                c_max = max(c_max, x)

                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = y + dy, x + dx
                        if (
                            0 <= ny < height
                            and 0 <= nx < width
                            and not seen[ny][nx]
                            and grid[ny][nx] == value
                        ):
                            seen[ny][nx] = True
                            stack.append((ny, nx))

            components.append(
                {
                    "cells": cells,
                    "color": value,
                    "r_min": r_min,
                    "c_min": c_min,
                    "width": c_max - c_min + 1,
                }
            )

    return components


def _recolor_from(original: Grid, out: Grid, start: Tuple[int, int], new_color: int) -> None:
    height = len(original)
    width = len(original[0])
    target = original[start[0]][start[1]]
    queue = deque([start])
    visited = {start}

    while queue:
        y, x = queue.popleft()
        out[y][x] = new_color
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if (
                0 <= ny < height
                and 0 <= nx < width
                and (ny, nx) not in visited
                and original[ny][nx] == target
            ):
                visited.add((ny, nx))
                queue.append((ny, nx))


def _project_components(grid: Grid) -> Grid:
    background = _background_color(grid)
    components = [
        comp
        for comp in _connected_components(grid, background)
        if comp["r_min"] >= SHIFT_ROWS
    ]

    if not components:
        return _copy_grid(grid)

    height = len(grid)
    width = len(grid[0])
    base_col = min(comp["c_min"] for comp in components)
    out = _copy_grid(grid)
    per_row: Dict[int, List[Tuple[int, Component]]] = {}

    for comp in components:
        dest_r = int(comp["r_min"]) - SHIFT_ROWS
        offset = int(comp["c_min"]) - base_col
        width_comp = int(comp["width"])
        dest_c = offset + (width_comp - 1) // 2
        if 0 <= dest_r < height and 0 <= dest_c < width:
            per_row.setdefault(dest_r, []).append((dest_c, comp))

    for dest_r, entries in per_row.items():
        entries.sort(key=lambda item: item[0])
        group_size = len(entries)
        middle_index = group_size // 2 if group_size >= 3 and group_size % 2 == 1 else -1
        for idx, (dest_c, comp) in enumerate(entries):
            marker = 1 if idx == middle_index else 9
            original_value = grid[dest_r][dest_c]
            out[dest_r][dest_c] = marker
            if original_value != background and original_value != marker:
                _recolor_from(grid, out, (dest_r, dest_c), marker)

    return out


def solve_409aa875(grid: Grid) -> Grid:
    return _project_components(grid)


p = solve_409aa875
