"""Solver for ARC-AGI-2 task 221dfab4 (evaluation split)."""

from __future__ import annotations

from collections import Counter
from typing import Callable, Iterable, List, Sequence, Set, Tuple, TypeVar

Grid = List[List[int]]
Color = int
Column = int
Row = int


# --- Small, pure helpers (DSL-compatible) ---

def majorityColor(grid: Grid) -> Color:
    counts = Counter(v for row in grid for v in row)
    return counts.most_common(1)[0][0]


def selectStripeColumns(grid: Grid) -> Set[Column]:
    if not grid:
        return set()
    width = len(grid[0])
    return {c for c in range(width) if any(row[c] == 4 for row in grid)}


def detectObjectColors(grid: Grid, background: Color) -> Set[Color]:
    counts = Counter(v for row in grid for v in row)
    return {col for col in counts if col not in (background, 4)}


def _set_cell(g: Grid, r: Row, c: Column, col: Color) -> Grid:
    return [([col if (ri == r and ci == c) else v for ci, v in enumerate(row)]) if ri == r else row[:] for ri, row in enumerate(g)]


T = TypeVar("T")


def fold_repaint(canvas: Grid, items: Iterable[T], update: Callable[[Grid, T], Grid]) -> Grid:
    g = canvas
    for x in items:
        g = update(g, x)
    return g


def paintStripes(grid: Grid, stripe_cols: Set[Column], background: Color) -> Grid:
    height = len(grid)

    def repaint_column(g: Grid, c: Column) -> Grid:
        def paint_cell(r: Row, old: Color) -> Color:
            phase = r % 6
            if phase == 0:
                return 3
            if phase in (2, 4):
                return 4
            return background

        # Rebuild column c immutably
        return [([paint_cell(r, v) if ci == c else v for ci, v in enumerate(row)]) for r, row in enumerate(g)]

    return fold_repaint(grid, stripe_cols, repaint_column)


def overlayObjects(grid: Grid, stripe_cols: Set[Column], object_colors: Set[Color]) -> Grid:
    height = len(grid)
    width = len(grid[0]) if grid else 0
    positions: List[Tuple[Row, Column]] = [
        (r, c)
        for r in range(0, height, 6)
        for c in range(width)
        if (c not in stripe_cols and grid[r][c] in object_colors)
    ]

    def paint_pos(g: Grid, rc: Tuple[Row, Column]) -> Grid:
        r, c = rc
        return _set_cell(g, r, c, 3)

    return fold_repaint(grid, positions, paint_pos)


# --- Solver entrypoint must exactly match abstractions.md lambda ---

def solve_221dfab4(grid: Grid) -> Grid:
    background = majorityColor(grid)
    stripe_cols = selectStripeColumns(grid)
    object_colors = detectObjectColors(grid, background)
    striped = paintStripes(grid, stripe_cols, background)
    return overlayObjects(striped, stripe_cols, object_colors)


p = solve_221dfab4
