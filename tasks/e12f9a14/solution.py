"""Solver for ARC-AGI-2 task e12f9a14 (split: evaluation).

Refactored to match the typed-DSL lambda while preserving behaviour.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple

# Type aliases for readability and mypy.
Grid = List[List[int]]
Cell = Tuple[int, int]
Offset = Tuple[int, int]
Seed = Any  # Structured dict carrying seed + context; opaque to the lambda.


DIGIT_TEMPLATE_VARIANTS = {
    1: (
        (
            (-10, -3),
            (-10, 8),
            (-9, -3),
            (-9, 7),
            (-8, -3),
            (-8, 7),
            (-7, -3),
            (-7, 6),
            (-6, -3),
            (-6, 6),
            (-5, -3),
            (-5, 5),
            (-4, -3),
            (-4, 5),
            (-3, -3),
            (-3, 4),
            (-2, -2),
            (-2, 3),
            (-1, -1),
            (-1, 2),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
            (2, -1),
            (2, 2),
            (3, -2),
            (3, 3),
            (4, -3),
            (4, 4),
            (5, -3),
            (5, 5),
            (6, -3),
            (6, 5),
            (7, -3),
            (7, 6),
            (8, -3),
            (8, 6),
            (9, -3),
            (9, 7),
            (10, -2),
            (10, 7),
            (11, -1),
            (11, 8),
            (12, 0),
            (12, 8),
            (13, 1),
            (13, 9),
        ),
    ),
    2: (
        (
            (-6, 14),
            (-5, 13),
            (-4, 12),
            (-3, 11),
            (-2, 10),
            (-1, 9),
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (0, 6),
            (0, 7),
            (0, 8),
            (1, -4),
            (1, -3),
            (1, -2),
            (1, -1),
            (1, 0),
            (1, 1),
        ),
    ),
    4: (
        (
            (-10, 3),
            (-9, 2),
            (-8, 2),
            (-7, 1),
            (-6, 1),
            (-5, 0),
            (-4, 0),
            (-3, 0),
            (-2, 0),
            (-1, 0),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
            (2, 0),
            (3, 0),
            (4, 0),
            (5, 0),
            (6, 0),
            (7, 1),
            (8, 1),
            (9, 2),
            (10, 2),
            (11, 3),
            (12, 3),
            (13, 4),
        ),
        (
            (-10, 7),
            (-9, 6),
            (-8, 5),
            (-7, 4),
            (-6, 3),
            (-5, 2),
            (-4, 1),
            (-3, 1),
            (-2, 1),
            (-1, 1),
            (0, -12),
            (0, -11),
            (0, -10),
            (0, -9),
            (0, -8),
            (0, -7),
            (0, -6),
            (0, -5),
            (0, -4),
            (0, -3),
            (0, -2),
            (0, -1),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
        ),
        (
            (-3, 1),
            (-2, 1),
            (-1, 1),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 5),
            (2, -1),
            (3, -2),
        ),
    ),
    6: (
        (
            (-3, 0),
            (-3, 4),
            (-2, 0),
            (-2, 3),
            (-1, 0),
            (-1, 2),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
            (2, -1),
            (3, -2),
        ),
        (
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (1, 0),
            (1, 1),
            (1, 6),
            (2, 7),
            (3, 8),
        ),
    ),
    7: (
        (
            (0, -6),
            (0, -5),
            (0, -4),
            (0, -3),
            (0, -2),
            (0, -1),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
        ),
    ),
    9: (
        (
            (-10, 4),
            (-9, 4),
            (-8, 4),
            (-7, 4),
            (-6, 4),
            (-5, 4),
            (-4, -4),
            (-4, 4),
            (-3, -3),
            (-3, 4),
            (-2, -2),
            (-2, 3),
            (-1, -1),
            (-1, 2),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
            (2, -1),
            (2, 2),
            (3, -2),
            (3, 3),
            (4, -3),
            (4, 4),
            (5, -4),
            (5, 4),
            (6, 4),
            (7, 4),
            (8, 4),
            (9, 4),
            (10, 5),
            (11, 6),
            (12, 7),
            (13, 8),
        ),
    ),
}


def _clone(grid: Grid) -> Grid:
    return [row[:] for row in grid]


# Helper routines ---------------------------------------------------------

def _dominant_color(grid: Grid) -> int:
    counter: Counter[int] = Counter()
    for row in grid:
        counter.update(row)
    return counter.most_common(1)[0][0]


def _components(grid: Grid) -> Iterable[Tuple[int, List[Cell]]]:
    height = len(grid)
    width = len(grid[0])
    seen = [[False] * width for _ in range(height)]
    for r in range(height):
        for c in range(width):
            if seen[r][c]:
                continue
            color = grid[r][c]
            stack = [(r, c)]
            seen[r][c] = True
            cells: List[Cell] = []
            while stack:
                rr, cc = stack.pop()
                cells.append((rr, cc))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not seen[nr][nc] and grid[nr][nc] == color:
                        seen[nr][nc] = True
                        stack.append((nr, nc))
            yield color, cells


# DSL helper shims --------------------------------------------------------

def extractComponents(grid: Grid) -> List[Seed]:
    """Enumerate components, attaching grid-context so later steps are pure."""
    bg = _dominant_color(grid)
    h, w = len(grid), len(grid[0])
    return [
        {
            "color": color,
            "cells": cells,
            "grid": grid,
            "background": bg,
            "height": h,
            "width": w,
        }
        for color, cells in _components(grid)
    ]


def filterSeedBlocks(components: List[Seed]) -> List[Seed]:
    """Keep only non-background 2x2 seeds; compute anchor per seed."""
    seeds: List[Seed] = []
    for comp in components:
        color: int = comp["color"]
        cells: List[Cell] = comp["cells"]
        bg: int = comp["background"]
        if color == bg or len(cells) != 4:
            continue
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        if max(rows) - min(rows) != 1 or max(cols) - min(cols) != 1:
            continue
        seed = dict(comp)
        seed["anchor"] = (min(rows), min(cols))
        seeds.append(seed)
    return seeds


def selectDigitVariant(seed: Seed) -> Optional[List[Offset]]:
    """Choose the best collision-free template offsets for the seed color.

    Mirrors original logic: maximize in-bounds placements; forbid drawing over
    non-background cells except the seed's own footprint.
    """
    color: int = seed["color"]
    variants = DIGIT_TEMPLATE_VARIANTS.get(color)
    if not variants:
        return None

    anchor_r, anchor_c = seed["anchor"]
    seed_cells = set(seed["cells"])  # absolute positions
    grid: Grid = seed["grid"]
    bg: int = seed["background"]
    height: int = seed["height"]
    width: int = seed["width"]

    best: Optional[Tuple[int, List[Offset]]] = None  # (count, offsets)
    for offsets in variants:
        count = 0
        collision = False
        for dr, dc in offsets:
            r = anchor_r + dr
            c = anchor_c + dc
            if not (0 <= r < height and 0 <= c < width):
                # Out of bounds: ignore; counts as not placed.
                continue
            if (r, c) not in seed_cells and grid[r][c] != bg:
                collision = True
                break
            count += 1
        if collision:
            continue
        if best is None or count > best[0]:
            best = (count, list(offsets))

    return None if best is None else best[1]


def paintDigitTemplate(canvas: Grid, seed: Seed, offsets: Sequence[Offset]) -> Grid:
    """Paint the union of seed cells and variant placements with seed color."""
    out = _clone(canvas)
    anchor_r, anchor_c = seed["anchor"]
    color: int = seed["color"]
    height: int = seed["height"]
    width: int = seed["width"]
    cells = set(seed["cells"])  # absolute seed cells

    # Convert offsets to absolute placements, clip to bounds.
    placements = {
        (anchor_r + dr, anchor_c + dc)
        for dr, dc in offsets
        if 0 <= anchor_r + dr < height and 0 <= anchor_c + dc < width
    }

    for r, c in placements.union(cells):
        out[r][c] = color
    return out


def fold_repaint(canvas: Grid, items: Iterable[Seed], update: Callable[[Grid, Seed], Grid]) -> Grid:
    """Functional fold: repeatedly repaint the canvas for each item."""
    acc = canvas
    for it in items:
        acc = update(acc, it)
    return acc


def solve_e12f9a14(grid: Grid) -> Grid:
    components = extractComponents(grid)
    seeds = filterSeedBlocks(components)

    def repaint(canvas: Grid, seed: Seed) -> Grid:
        offsets = selectDigitVariant(seed)
        if offsets is None:
            return canvas
        return paintDigitTemplate(canvas, seed, offsets)

    return fold_repaint(grid, seeds, repaint)


p = solve_e12f9a14
