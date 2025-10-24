"""Solver for ARC-AGI-2 task 8e5c0c38 (evaluation split).

Typed-DSL shaped: choose a best horizontal mirror axis per colour by minimal
deletions and trim asymmetric pixels using a fold-style repaint.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Callable, Dict, Iterable, List, Sequence, Tuple, TypeVar

Grid = List[List[int]]
Pos = Tuple[int, int]
T = TypeVar("T")


def fold_repaint(canvas: Grid, items: Sequence[T], update: Callable[[Grid, T], Grid]) -> Grid:
    acc = canvas
    for x in items:
        acc = update(acc, x)
    return acc


def background_color(grid: Grid) -> int:
    return Counter(pixel for row in grid for pixel in row).most_common(1)[0][0]


def groupCellsByColor(grid: Grid) -> Dict[int, List[Pos]]:
    bg = background_color(grid)
    groups: Dict[int, List[Pos]] = defaultdict(list)
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value != bg:
                groups[value].append((r, c))
    return groups


def evaluateAxisCost(cells: Sequence[Pos]) -> int:
    min_c = min(c for _, c in cells)
    max_c = max(c for _, c in cells)
    cells_set = set(cells)
    preferred_axis2 = min_c + max_c

    best_key = None
    best_axis2 = preferred_axis2

    for axis2 in range(2 * min_c, 2 * max_c + 1):
        to_remove = [
            (r, c) for (r, c) in cells if (r, axis2 - c) not in cells_set
        ]
        key = (len(to_remove), abs(axis2 - preferred_axis2), axis2)
        if best_key is None or key < best_key:
            best_key = key
            best_axis2 = axis2

    return best_axis2


def trimAsymmetricCells(canvas: Grid, cells: Sequence[Pos], axis2: int) -> Grid:
    if not cells:
        return canvas
    bg = background_color(canvas)
    cells_set = set(cells)
    to_remove = [(r, c) for (r, c) in cells if (r, axis2 - c) not in cells_set]
    if not to_remove:
        return canvas
    out = [row[:] for row in canvas]
    for r, c in to_remove:
        out[r][c] = bg
    return out


def solve_8e5c0c38(grid: Grid) -> Grid:
    colour_groups = groupCellsByColor(grid)

    def trim(canvas: Grid, entry):
        colour, cells = entry
        axis = evaluateAxisCost(cells)
        return trimAsymmetricCells(canvas, cells, axis)

    trimmed = fold_repaint(grid, list(colour_groups.items()), trim)
    return trimmed


p = solve_8e5c0c38
