"""Solver for ARC-AGI-2 task fc7cae8d (split: evaluation).

Refactored to align the main solver with the typed DSL lambda while
preserving original behavior and heuristics.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import List, Sequence, Tuple, Optional, TypedDict


Grid = List[List[int]]


@dataclass(frozen=True)
class Component:
    color: int
    cells: Sequence[Tuple[int, int]]
    touches_border: bool


class _CompDict(TypedDict):
    color: int
    cells: List[Tuple[int, int]]
    touches_border: bool


def _largest_component(grid: Grid) -> _CompDict:
    """Return the largest color component, preferring ones away from the border."""
    height = len(grid)
    width = len(grid[0])
    visited = [[False] * width for _ in range(height)]

    best_interior: Optional[_CompDict] = None
    best_any: Optional[_CompDict] = None

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

            component: _CompDict = {
                "color": color,
                "cells": cells,
                "touches_border": touches_border,
            }

            if best_any is None or len(cells) > len(best_any["cells"]):
                best_any = component
            if not touches_border:
                if best_interior is None or len(cells) > len(best_interior["cells"]):
                    best_interior = component

    return best_interior or best_any  # type: ignore[return-value]


def _rotate_ccw(grid: Grid) -> Grid:
    return [list(row) for row in zip(*grid)][::-1]


def _maybe_flip_horizontal(grid: Grid, dominant_color: int) -> Grid:
    left_column = [row[0] for row in grid]
    right_column = [row[-1] for row in grid]

    left_primary = sum(1 for val in left_column if val == dominant_color)
    right_primary = sum(1 for val in right_column if val == dominant_color)
    left_impurity = len(left_column) - left_primary
    right_impurity = len(right_column) - right_primary

    left_score = (left_primary, -left_impurity)
    right_score = (right_primary, -right_impurity)

    if left_score < right_score:
        return [list(reversed(row)) for row in grid]
    return grid


# --- DSL-style helpers used by the main lambda-equivalent solver ---

def selectInteriorComponent(grid: Grid) -> Component:
    d = _largest_component(grid)
    return Component(color=d["color"], cells=tuple(d["cells"]), touches_border=bool(d["touches_border"]))


def cropComponent(grid: Grid, component: Component) -> Grid:
    rows = [r for r, _ in component.cells]
    cols = [c for _, c in component.cells]
    r0, r1 = min(rows), max(rows)
    c0, c1 = min(cols), max(cols)
    return [row[c0 : c1 + 1] for row in grid[r0 : r1 + 1]]


def rotateCounterClockwise(grid: Grid) -> Grid:
    return _rotate_ccw(grid)


def conditionalMirror(grid: Grid, dominant_color: int) -> Grid:
    return _maybe_flip_horizontal(grid, dominant_color)


def solve_fc7cae8d(grid: Grid) -> Grid:
    component = selectInteriorComponent(grid)
    cropped = cropComponent(grid, component)
    rotated = rotateCounterClockwise(cropped)
    return conditionalMirror(rotated, component.color)


p = solve_fc7cae8d
