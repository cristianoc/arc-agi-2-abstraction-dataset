"""Solver for ARC-AGI-2 task 45a5af55."""

from __future__ import annotations

from typing import List

Grid = List[List[int]]


def _build_rings(colors: List[int]) -> Grid:
    size = 2 * len(colors)
    if size == 0:
        return []
    out = [[0] * size for _ in range(size)]
    for depth, color in enumerate(colors):
        top = depth
        bottom = size - 1 - depth
        left = depth
        right = size - 1 - depth
        for x in range(left, right + 1):
            out[top][x] = color
            out[bottom][x] = color
        for y in range(top, bottom + 1):
            out[y][left] = color
            out[y][right] = color
    return out


def solve_45a5af55(grid: Grid) -> Grid:
    """Convert leading stripes into concentric square rings."""

    if not grid or not grid[0]:
        return [row[:] for row in grid]

    height = len(grid)
    width = len(grid[0])
    if min(height, width) <= 1:
        return [row[:] for row in grid]

    use_rows = height >= width
    axis_length = height if use_rows else width
    if axis_length <= 1:
        return [row[:] for row in grid]

    if use_rows:
        colors = [grid[r][0] for r in range(axis_length - 1)]
    else:
        colors = [grid[0][c] for c in range(axis_length - 1)]

    return _build_rings(colors)


p = solve_45a5af55
