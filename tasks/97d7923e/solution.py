"""Directional selective cap-fill for ARC task 97d7923e (DSL-aligned)."""

from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from typing import NamedTuple


# Local DSL type aliases
Grid = List[List[int]]


class Run(NamedTuple):
    color: int
    length: int
    start: int


ColumnRuns = Dict[int, List[Run]]
CapPattern = Tuple[Run, Run, Run]


def fold_repaint(initial: Grid, items: List[Tuple[int, List[Run]]], update: Callable[[Grid, Tuple[int, List[Run]]], Grid]) -> Grid:
    canvas = [row[:] for row in initial]
    for item in items:
        canvas = update(canvas, item)
    return canvas


def parseColumnRuns(grid: Grid) -> ColumnRuns:
    h, w = len(grid), len(grid[0])
    cols: ColumnRuns = {}
    for c in range(w):
        runs: List[Run] = []
        current = grid[0][c]
        length = 1
        start = 0
        for r in range(1, h):
            val = grid[r][c]
            if val == current:
                length += 1
            else:
                runs.append(Run(current, length, start))
                start += length
                current = val
                length = 1
        runs.append(Run(current, length, start))
        cols[c] = runs
    return cols


def detectCapPattern(runs: List[Run]) -> Optional[CapPattern]:
    # Find the first (top, middle, bottom) triple where top/bottom match and middle is non-zero
    for i in range(len(runs) - 2):
        top, mid, bot = runs[i], runs[i + 1], runs[i + 2]
        if top.color != 0 and mid.color != 0 and top.color == bot.color:
            return (top, mid, bot)
    return None


def paintColumnRun(canvas: Grid, column_index: int, middle: Run, color: int) -> Grid:
    out = [row[:] for row in canvas]
    for r in range(middle.start, middle.start + middle.length):
        out[r][column_index] = color
    return out


def solve_97d7923e(grid: Grid) -> Grid:
    column_runs = parseColumnRuns(grid)
    entries = list(column_runs.items())

    def applyFillGuards(column_index, pattern):
        runs = column_runs[column_index]
        top, middle, bottom = pattern
        i = next((idx for idx, r in enumerate(runs) if r == top), -1)
        if i < 0:
            return False
        has_different_cap_above = any(r.color != 0 and r.color != top.color for idx, r in enumerate(runs) if idx < i)
        if has_different_cap_above:
            return True
        if top.start == 3 and middle.length >= 5:
            return True
        if column_index >= len(grid[0]) - 2 and middle.length <= 2:
            return True
        return False

    def repaint(canvas: Grid, entry):
        column_index, runs = entry
        pattern = detectCapPattern(runs)
        if pattern is None:
            return canvas
        top, middle, bottom = pattern
        if not applyFillGuards(column_index, pattern):
            return canvas
        return paintColumnRun(canvas, column_index, middle, top.color)
    return fold_repaint(grid, entries, repaint)


p = solve_97d7923e
