"""Solver for ARC-AGI-2 task 135a2760."""

from collections import Counter
from typing import List

Grid = List[List[int]]


def _periodic_row_fix(row: List[int], border: int, walkway: int | None, max_period: int = 6) -> None:
    """Replace the inner segment of ``row`` by its dominant repeating pattern."""

    start = None
    end = None
    for c, value in enumerate(row):
        if value != border and (walkway is None or value != walkway):
            start = c
            break
    for c in range(len(row) - 1, -1, -1):
        value = row[c]
        if value != border and (walkway is None or value != walkway):
            end = c
            break

    if start is None or end is None or start > end:
        return

    inner = row[start : end + 1]
    if not inner:
        return

    best_pattern: List[int] = [inner[0]]
    best_p = 1
    best_score = (1.0, len(inner), len(inner))
    limit = min(max_period, len(inner))

    for p in range(1, limit + 1):
        groups: List[List[int]] = [[] for _ in range(p)]
        for idx, value in enumerate(inner):
            groups[idx % p].append(value)

        mismatch = 0
        pattern: List[int] = []
        for bucket in groups:
            value, freq = Counter(bucket).most_common(1)[0]
            pattern.append(value)
            mismatch += len(bucket) - freq

        score = (mismatch / len(inner), mismatch, p)
        if score < best_score:
            best_score = score
            best_pattern = pattern
            best_p = p

    for offset in range(len(inner)):
        row[start + offset] = best_pattern[offset % best_p]


def solve_135a2760(grid: Grid) -> Grid:
    """Repair stray cells that break the repeating row patterns inside the frame."""

    result = [row[:] for row in grid]
    border = grid[0][0]
    walkway = grid[1][1] if len(grid) > 1 and len(grid[0]) > 1 else None

    for row in result:
        _periodic_row_fix(row, border, walkway)

    return result


p = solve_135a2760
