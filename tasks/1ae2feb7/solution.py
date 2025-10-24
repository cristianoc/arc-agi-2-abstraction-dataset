"""Solver for ARC-AGI-2 task 1ae2feb7 (split: evaluation)."""

from typing import List, Tuple, Optional

Grid = List[List[int]]
Row = List[int]


def _last_barrier(row: Row) -> Optional[int]:
    try:
        return max(idx for idx, val in enumerate(row) if val == 2)
    except ValueError:
        return None


def collectSegments(row: Row) -> List[Tuple[int, int]]:
    barrier = _last_barrier(row)
    if barrier is None:
        return []
    segments: List[Tuple[int, int]] = []
    idx = 0
    while idx < barrier:
        color = row[idx]
        if color == 0:
            idx += 1
            continue
        start = idx
        while idx < barrier and row[idx] == color:
            idx += 1
        segments.append((color, idx - start))
    return segments


def repeatSegments(row: Row, segments: List[Tuple[int, int]]) -> Row:
    barrier = _last_barrier(row)
    if barrier is None:
        return row[:]
    extended = row[:]
    width = len(row)
    for color, length in reversed(segments):
        if length <= 0:
            continue
        pos = barrier + 1
        while pos < width:
            if extended[pos] == 0:
                extended[pos] = color
            pos += length
    return extended


def solve_1ae2feb7(grid: Grid) -> Grid:
    def processRow(row: Row) -> Row:
        segments = collectSegments(row)
        return repeatSegments(row, segments)
    
    return [processRow(row) for row in grid]


p = solve_1ae2feb7
