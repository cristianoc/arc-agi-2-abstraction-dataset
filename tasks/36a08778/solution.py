"""Solver for ARC-AGI-2 task 36a08778 (typed-DSL main with pure helpers)."""

from __future__ import annotations

from typing import Iterable, List, Set, Tuple

Grid = List[List[int]]
Column = int
Run = Tuple[int, int, int]  # row, left, right


def _iter_runs(row: List[int], target: int = 2) -> Iterable[Tuple[int, int]]:
    """Yield [start, end] column spans of consecutive `target` values."""
    start = None
    for idx, value in enumerate(row):
        if value == target:
            if start is None:
                start = idx
        elif start is not None:
            yield start, idx - 1
            start = None
    if start is not None:
        yield start, len(row) - 1


# Typed-DSL helper building blocks (pure, no side effects)
def extractScaffoldColumns(grid: Grid) -> Set[Column]:
    height = len(grid)
    seeds: Set[int] = set()
    for r in range(min(2, height)):
        for c, value in enumerate(grid[r]):
            if value == 6:
                seeds.add(c)
    return seeds


def extendScaffolds(grid: Grid, scaffold_cols: Set[Column]) -> Grid:
    height = len(grid)
    result = [row[:] for row in grid]
    for c in scaffold_cols:
        for r in range(height):
            if grid[r][c] == 2:
                break
            if result[r][c] == 7:
                result[r][c] = 6
    return result


def collectRuns(grid: Grid) -> List[Run]:
    height = len(grid)
    runs: List[Run] = []
    for r in range(2, height):  # skip first two rows
        for left, right in _iter_runs(grid[r], target=2):
            runs.append((r, left, right))
    return runs


def filterRunsByScaffold(runs: List[Run], scaffolded: Grid) -> List[Run]:
    keep: List[Run] = []
    for r, left, right in runs:
        touches = any(
            scaffolded[r - 1][c] == 6 or scaffolded[r][c] == 6 for c in range(left, right + 1)
        )
        if touches:
            keep.append((r, left, right))
    return keep


def wrapRunsWithHalo(scaffolded: Grid, runs: List[Run]) -> Grid:
    height = len(scaffolded)
    width = len(scaffolded[0]) if height else 0
    result = [row[:] for row in scaffolded]

    for r, left, right in runs:
        # Connectivity check against current result (which accumulates halos)
        touches_scaffold = any(
            result[r - 1][c] == 6 or result[r][c] == 6 for c in range(left, right + 1)
        )
        if not touches_scaffold:
            continue
        run_len = right - left + 1

        left_neighbor = left - 1 if left > 0 else None
        right_neighbor = right + 1 if right + 1 < width else None

        if run_len > 1:
            for c in range(max(0, left - 1), min(width, right + 2)):
                if result[r - 1][c] == 7:
                    result[r - 1][c] = 6
        else:
            c = right + 1
            if c < width and result[r - 1][c] == 7:
                result[r - 1][c] = 6

        if run_len > 1 and left_neighbor is not None and result[r][left_neighbor] == 7:
            result[r][left_neighbor] = 6
        if right_neighbor is not None and result[r][right_neighbor] == 7:
            result[r][right_neighbor] = 6

        if run_len > 1 and left_neighbor is not None:
            for rr in range(r + 1, height):
                if scaffolded[rr][left_neighbor] == 2:
                    break
                if result[rr][left_neighbor] == 7:
                    result[rr][left_neighbor] = 6

        if right_neighbor is not None:
            for rr in range(r + 1, height):
                if scaffolded[rr][right_neighbor] == 2:
                    break
                if result[rr][right_neighbor] == 7:
                    result[rr][right_neighbor] = 6

    return result


# Main solver entry — must match abstractions.md Lambda Representation exactly
def solve_36a08778(grid: Grid) -> Grid:
    scaffold_cols = extractScaffoldColumns(grid)
    scaffolded = extendScaffolds(grid, scaffold_cols)
    runs = collectRuns(grid)
    return wrapRunsWithHalo(scaffolded, runs)


p = solve_36a08778
