"""Solver for ARC-AGI-2 task 31f7f899 (evaluation split)."""

from collections import Counter
from typing import List, Sequence, Tuple

Grid = List[List[int]]
Stripe = Tuple[int, int, int]  # (column, color, height)


def _clone(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def pinBackboneRow(grid: Grid) -> Tuple[int, List[int]]:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return 0, []

    background = max(
        Counter(cell for row in grid for cell in row).items(),
        key=lambda item: (item[1], -item[0]),
    )[0]

    def non_bg_count(row: Sequence[int]) -> int:
        return sum(cell != background for cell in row)

    center_row_idx = max(range(rows), key=lambda r: (non_bg_count(grid[r]), -r))
    return center_row_idx, grid[center_row_idx]


def collectStripeSpans(grid: Grid, center_row_idx: int, center_row: Sequence[int]) -> List[Stripe]:
    rows = len(grid)
    if rows == 0 or not center_row:
        return []

    background = max(
        Counter(cell for row in grid for cell in row).items(),
        key=lambda item: (item[1], -item[0]),
    )[0]
    dominant_color = max(
        Counter(center_row).items(),
        key=lambda item: (item[1], -item[0]),
    )[0]

    stripes: List[Stripe] = []
    for c, color in enumerate(center_row):
        if color == background or color == dominant_color:
            continue
        top = bottom = center_row_idx
        while top > 0 and grid[top - 1][c] == color:
            top -= 1
        while bottom + 1 < rows and grid[bottom + 1][c] == color:
            bottom += 1
        height = bottom - top + 1
        stripes.append((c, color, height))
    return stripes


def sortStripesByHeight(stripes: List[Stripe]) -> List[Stripe]:
    lengths = sorted([h for (_, _, h) in stripes])
    cols_colors = [(c, color) for (c, color, _) in stripes]
    return [(c, color, h) for (c, color), h in zip(cols_colors, lengths)]


def renderSortedStripes(grid: Grid, center_row_idx: int, stripes: List[Stripe]) -> Grid:
    rows = len(grid)
    if rows == 0:
        return _clone(grid)

    background = max(
        Counter(cell for row in grid for cell in row).items(),
        key=lambda item: (item[1], -item[0]),
    )[0]

    output = _clone(grid)
    for c, color, target_len in stripes:
        radius = target_len // 2
        top = center_row_idx - radius
        bottom = center_row_idx + radius
        for r in range(rows):
            output[r][c] = background
        for r in range(top, bottom + 1):
            output[r][c] = color
    return output


def solve_31f7f899(grid: Grid) -> Grid:
    center_row_idx, center_row = pinBackboneRow(grid)
    stripes = collectStripeSpans(grid, center_row_idx, center_row)
    sorted_stripes = sortStripesByHeight(stripes)
    return renderSortedStripes(grid, center_row_idx, sorted_stripes)


p = solve_31f7f899
