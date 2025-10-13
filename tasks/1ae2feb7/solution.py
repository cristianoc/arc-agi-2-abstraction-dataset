"""Solver for ARC-AGI-2 task 1ae2feb7 (split: evaluation)."""

from typing import List, Tuple

Grid = List[List[int]]


def _extend_row_with_blocks(row: List[int]) -> List[int]:
    """Extend non-zero blocks found to the left of the final 2 across the row."""

    try:
        barrier_col = max(idx for idx, val in enumerate(row) if val == 2)
    except ValueError:
        return row[:]  # no barrier; leave the row unchanged

    extended = row[:]
    idx = 0
    segments: List[Tuple[int, int]] = []

    while idx < barrier_col:
        color = row[idx]
        if color == 0:
            idx += 1
            continue

        start = idx
        while idx < barrier_col and row[idx] == color:
            idx += 1

        segments.append((color, idx - start))

    width = len(row)
    for color, length in reversed(segments):
        if length <= 0:
            continue

        pos = barrier_col + 1
        while pos < width:
            if extended[pos] == 0:
                extended[pos] = color
            pos += length

    return extended


def solve_1ae2feb7(grid: Grid) -> Grid:
    """Propagate left-hand blocks across the barrier column of 2s."""

    return [_extend_row_with_blocks(row) for row in grid]


p = solve_1ae2feb7
