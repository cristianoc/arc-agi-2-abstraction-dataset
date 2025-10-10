"""Auto-generated identity stub for ARC-AGI-2 task 31f7f899 (split: evaluation)."""

from collections import Counter


def solve_31f7f899(grid):
    """Transform the central stripes so their vertical spans increase left→right."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return [row[:] for row in grid]

    background = max(
        Counter(cell for row in grid for cell in row).items(),
        key=lambda item: (item[1], -item[0]),
    )[0]

    def non_bg_count(row):
        return sum(cell != background for cell in row)

    center_row_idx = max(range(rows), key=lambda r: (non_bg_count(grid[r]), -r))
    center_row = grid[center_row_idx]

    dominant_color = max(
        Counter(center_row).items(),
        key=lambda item: (item[1], -item[0]),
    )[0]

    special_cols = []
    col_lengths = []
    for c, color in enumerate(center_row):
        if color == background or color == dominant_color:
            continue
        top = bottom = center_row_idx
        while top > 0 and grid[top - 1][c] == color:
            top -= 1
        while bottom + 1 < rows and grid[bottom + 1][c] == color:
            bottom += 1
        col_lengths.append(bottom - top + 1)
        special_cols.append((c, color))

    target_lengths = sorted(col_lengths)

    output = [row[:] for row in grid]
    for (c, color), length in zip(special_cols, target_lengths):
        radius = length // 2
        top = center_row_idx - radius
        bottom = center_row_idx + radius
        for r in range(rows):
            output[r][c] = background
        for r in range(top, bottom + 1):
            output[r][c] = color

    return output


p = solve_31f7f899
