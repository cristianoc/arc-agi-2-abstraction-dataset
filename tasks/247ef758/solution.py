"""Solver for ARC-AGI-2 task 247ef758 (split: evaluation)."""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy


def solve_247ef758(grid):
    """Heuristic solver tuned from inspection of the training pairs."""
    work = deepcopy(grid)
    height = len(work)
    width = len(work[0]) if height else 0

    if height == 0 or width == 0:
        return work

    axis_column = None
    for c in range(width):
        column = [work[r][c] for r in range(height)]
        if column[0] != 0 and all(v == column[0] for v in column):
            axis_column = c
            break

    if axis_column is None:
        return work

    color_to_cells: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for r in range(height):
        for c in range(axis_column):
            val = work[r][c]
            if val != 0:
                color_to_cells[val].append((r, c))

    top_row = grid[0]
    color_to_cols: dict[int, set[int]] = defaultdict(set)
    for c in range(axis_column + 1, width):
        val = top_row[c]
        if val != 0:
            color_to_cols[val].add(c)

    last_col_index = width - 1
    color_to_rows: dict[int, set[int]] = defaultdict(set)
    for r in range(height):
        val = grid[r][last_col_index]
        if val != 0:
            color_to_rows[val].add(r)

    def color_min_row(color: int) -> int:
        return min(r for r, _ in color_to_cells[color])

    movable_colors = [
        color
        for color in color_to_cells
        if color_to_cols[color] and color_to_rows[color]
    ]

    movable_colors.sort(key=color_min_row, reverse=True)

    for color in movable_colors:
        cells = color_to_cells[color]
        min_r = min(r for r, _ in cells)
        max_r = max(r for r, _ in cells)
        min_c = min(c for _, c in cells)
        max_c = max(c for _, c in cells)

        center_r = (min_r + max_r) // 2
        center_c = (min_c + max_c) // 2

        offsets = [(r - center_r, c - center_c) for r, c in cells]

        for r, c in cells:
            work[r][c] = 0

        for target_row in sorted(color_to_rows[color]):
            for target_col in sorted(color_to_cols[color]):
                for dr, dc in offsets:
                    rr = target_row + dr
                    cc = target_col + dc
                    if 0 <= rr < height and 0 <= cc < width:
                        work[rr][cc] = color

    return work


p = solve_247ef758
