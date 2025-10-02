"""Solver for ARC-AGI-2 task dd6b8c4b (split: evaluation)."""

from collections import Counter


def solve_dd6b8c4b(grid):
    """Rebalance scattered 9s by relocating them toward the central ring."""
    height = len(grid)
    width = len(grid[0])
    center_row, center_col = height // 2, width // 2

    left_quadrants = 0
    right_quadrants = 0
    nine_cells = []
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value != 9:
                continue
            dr = r - center_row
            dc = c - center_col
            abs_dr = abs(dr)
            abs_dc = abs(dc)
            if dc > 0 and dr != 0:
                right_quadrants += 1
            elif dc < 0 and dr != 0:
                left_quadrants += 1
            boundary_flag = int(r in (0, height - 1) or c in (0, width - 1))
            score = -3 * dr - abs_dr + abs_dc - boundary_flag
            nine_cells.append((score, r, c))

    diff = right_quadrants - left_quadrants
    ring_order = [
        (center_row - 1, center_col - 1),
        (center_row - 1, center_col),
        (center_row - 1, center_col + 1),
        (center_row, center_col - 1),
        (center_row + 1, center_col - 1),
        (center_row + 1, center_col),
        (center_row + 1, center_col + 1),
        (center_row, center_col + 1),
        (center_row, center_col),
    ]
    steps = max(0, min(len(ring_order), 2 * diff))

    palette = Counter(val for row in grid for val in row)
    background = palette.most_common(1)[0][0]

    result = [row[:] for row in grid]

    for idx in range(steps):
        r, c = ring_order[idx]
        result[r][c] = 9

    nine_cells.sort()
    for idx in range(min(steps, len(nine_cells))):
        _, r, c = nine_cells[idx]
        result[r][c] = background

    return result


p = solve_dd6b8c4b
