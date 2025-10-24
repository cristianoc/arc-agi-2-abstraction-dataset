"""Solver for ARC-AGI-2 task 58490d8a (split: evaluation)."""

from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, List, Optional, Tuple


Grid = List[List[int]]
Component = Tuple[int, List[Tuple[int, int]]]


def _zero_rectangle(grid: Grid) -> Optional[Tuple[int, int, int, int]]:
    zero_cells = [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == 0]
    if not zero_cells:
        return None
    rows, cols = zip(*zero_cells)
    return min(rows), max(rows), min(cols), max(cols)


def extractScoreboard(grid: Grid) -> Grid:
    rect = _zero_rectangle(grid)
    if rect is None:
        return [row[:] for row in grid]
    r0, r1, c0, c1 = rect
    return [row[c0 : c1 + 1] for row in grid[r0 : r1 + 1]]


def enumerateArenaComponents(grid: Grid) -> List[Component]:
    rect = _zero_rectangle(grid)
    if rect is None:
        return []
    r0, r1, c0, c1 = rect
    h = len(grid)
    w = len(grid[0]) if h else 0
    seen = [[False] * w for _ in range(h)]
    comps: List[Component] = []

    def in_board(r: int, c: int) -> bool:
        return r0 <= r <= r1 and c0 <= c <= c1

    for r in range(h):
        for c in range(w):
            if in_board(r, c) or seen[r][c]:
                continue
            color = grid[r][c]
            queue = deque([(r, c)])
            seen[r][c] = True
            cells = [(r, c)]
            while queue:
                cr, cc = queue.popleft()
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = cr + dr, cc + dc
                        if not (0 <= nr < h and 0 <= nc < w):
                            continue
                        if in_board(nr, nc) or seen[nr][nc] or grid[nr][nc] != color:
                            continue
                        seen[nr][nc] = True
                        queue.append((nr, nc))
                        cells.append((nr, nc))
            comps.append((color, cells))
    return comps


def countComponentsByColor(components: List[Component]) -> Dict[int, int]:
    counts: Dict[int, int] = {}
    for color, _cells in components:
        counts[color] = counts.get(color, 0) + 1
    return counts


def writeCountsToBoard(board: Grid, counts: Dict[int, int]) -> Grid:
    if not board:
        return []
    h = len(board)
    w = len(board[0])
    out = [[0] * w for _ in range(h)]

    for r in range(h):
        indicator: Optional[int] = None
        for c in range(w):
            v = board[r][c]
            if v != 0:
                indicator = v
                break
        if indicator is None:
            continue
        repeats = counts.get(indicator, 0)
        if repeats <= 0:
            continue
        col = 1 if w > 1 else 0
        placed = 0
        while placed < repeats and col < w:
            out[r][col] = indicator
            placed += 1
            col += 2
        if placed < repeats:
            for c in range(w):
                if out[r][c] == 0:
                    out[r][c] = indicator
                    placed += 1
                    if placed == repeats:
                        break
    return out


def solve_58490d8a(grid: Grid) -> Grid:
    board = extractScoreboard(grid)
    components = enumerateArenaComponents(grid)
    counts = countComponentsByColor(components)
    return writeCountsToBoard(board, counts)


p = solve_58490d8a
