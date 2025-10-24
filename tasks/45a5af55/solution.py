"""Solver for ARC-AGI-2 task 45a5af55."""

from __future__ import annotations

from typing import List, Literal

Grid = List[List[int]]
Axis = Literal["rows", "columns"]


def _clone(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def detectDominantAxis(grid: Grid) -> Axis:
    if not grid or not grid[0]:
        return "rows"
    h = len(grid)
    w = len(grid[0])
    return "rows" if h >= w else "columns"


def collectAxisStripes(grid: Grid, axis: Axis) -> List[int]:
    if not grid or not grid[0]:
        return []
    h = len(grid)
    w = len(grid[0])
    if axis == "rows":
        return [grid[r][0] for r in range(h)]
    return [grid[0][c] for c in range(w)]


def dropTrailingStripe(colors: List[int]) -> List[int]:
    return colors[:-1] if colors else []


def renderConcentricRings(grid: Grid, colors: List[int]) -> Grid:
    if not colors:
        return _clone(grid)
    size = 2 * len(colors)
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
    axis = detectDominantAxis(grid)
    stripes = collectAxisStripes(grid, axis)
    ring_colors = dropTrailingStripe(stripes)
    return renderConcentricRings(grid, ring_colors)


p = solve_45a5af55
