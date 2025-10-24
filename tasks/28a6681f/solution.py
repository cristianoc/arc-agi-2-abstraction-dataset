"""Solver for ARC-AGI-2 task 28a6681f (split: evaluation)."""

from __future__ import annotations

from typing import List, Tuple

Grid = List[List[int]]
Cell = Tuple[int, int]


def _copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def collectSupply(grid: Grid) -> List[Cell]:
    h = len(grid)
    w = len(grid[0]) if h else 0
    return sorted((r, c) for r in range(h) for c in range(w) if grid[r][c] == 1)


def _bounded_zero_segments_in_row(row: List[int]) -> List[Tuple[int, int]]:
    w = len(row)
    segs: List[Tuple[int, int]] = []
    c = 0
    while c < w:
        if row[c] != 0:
            c += 1
            continue
        start = c
        while c < w and row[c] == 0:
            c += 1
        end = c - 1
        left_color = row[start - 1] if start > 0 else 0
        right_color = row[end + 1] if end + 1 < w else 0
        if left_color != 0 and right_color != 0:
            segs.append((start, end))
    return segs


def findCandidates(grid: Grid) -> List[Cell]:
    cells: List[Cell] = []
    for r, row in enumerate(grid):
        for start, end in _bounded_zero_segments_in_row(row):
            cells.extend((r, c) for c in range(start, end + 1))
    return cells


def orderCandidates(candidates: List[Cell]) -> List[Cell]:
    return sorted(candidates, key=lambda rc: (-rc[0], -rc[1]))


def fillCandidates(grid: Grid, ordered_candidates: List[Cell], supply: List[Cell]) -> Tuple[Grid, List[Cell]]:
    result = _copy(grid)
    supply_copy = list(supply)
    removed: List[Cell] = []
    for r, c in ordered_candidates:
        if not supply_copy:
            break
        if supply_copy[0][0] <= r:
            removed.append(supply_copy.pop(0))
            result[r][c] = 1
    return result, removed


def clearRemoved(grid: Grid, removed: List[Cell]) -> Grid:
    result = _copy(grid)
    for r, c in removed:
        result[r][c] = 0
    return result


def solve_28a6681f(grid: Grid) -> Grid:
    supply = collectSupply(grid)
    candidates = findCandidates(grid)
    ordered_candidates = orderCandidates(candidates)
    result, removed = fillCandidates(grid, ordered_candidates, supply)
    return clearRemoved(result, removed)


p = solve_28a6681f
