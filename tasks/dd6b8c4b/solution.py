"""Solver for ARC-AGI-2 task dd6b8c4b (split: evaluation).

Refactored to align the main entrypoint with the typed-DSL lambda
representation while preserving the original behaviour.
"""

from __future__ import annotations

from collections import Counter
from typing import List, Tuple

Grid = List[List[int]]
Cell = Tuple[int, int]
Score = int


def _center(grid: Grid) -> Cell:
    return (len(grid) // 2, len(grid[0]) // 2)


def measureQuadrantImbalance(grid: Grid) -> int:
    h, w = len(grid), len(grid[0])
    cr, cc = _center(grid)
    left = 0
    right = 0
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v != 9:
                continue
            dr = r - cr
            dc = c - cc
            if dc > 0 and dr != 0:
                right += 1
            elif dc < 0 and dr != 0:
                left += 1
    return right - left


def selectRingTargets(grid: Grid, imbalance: int) -> List[Cell]:
    cr, cc = _center(grid)
    ring_order: List[Cell] = [
        (cr - 1, cc - 1),
        (cr - 1, cc),
        (cr - 1, cc + 1),
        (cr, cc - 1),
        (cr + 1, cc - 1),
        (cr + 1, cc),
        (cr + 1, cc + 1),
        (cr, cc + 1),
        (cr, cc),
    ]
    steps = max(0, min(len(ring_order), 2 * imbalance))
    return ring_order[:steps]


def scoreExistingNines(grid: Grid) -> List[Tuple[Score, Cell]]:
    h, w = len(grid), len(grid[0])
    cr, cc = _center(grid)
    scored: List[Tuple[Score, Cell]] = []
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v != 9:
                continue
            dr = r - cr
            dc = c - cc
            abs_dr = abs(dr)
            abs_dc = abs(dc)
            boundary_flag = int(r in (0, h - 1) or c in (0, w - 1))
            score: Score = (-3 * dr) - abs_dr + abs_dc - boundary_flag
            scored.append((score, (r, c)))
    scored.sort(key=lambda t: t[0])
    return scored


def rebalanceNines(grid: Grid, ring_targets: List[Cell], ranked: List[Tuple[Score, Cell]]) -> Grid:
    # Background is the most common colour in the grid.
    background = Counter(v for row in grid for v in row).most_common(1)[0][0]
    result: Grid = [row[:] for row in grid]

    # Promote ring targets to 9.
    for r, c in ring_targets:
        result[r][c] = 9

    # Retire the same number of lowest-scoring original 9s.
    retire = min(len(ring_targets), len(ranked))
    for i in range(retire):
        (__, (r, c)) = ranked[i]
        result[r][c] = background

    return result


def solve_dd6b8c4b(grid: Grid) -> Grid:
    imbalance = measureQuadrantImbalance(grid)
    ring_targets = selectRingTargets(grid, imbalance)
    ranked = scoreExistingNines(grid)
    return rebalanceNines(grid, ring_targets, ranked)


p = solve_dd6b8c4b
