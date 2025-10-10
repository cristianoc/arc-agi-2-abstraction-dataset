"""Solver for ARC-AGI-2 task 4c3d4a41 (split: evaluation)."""


def solve_4c3d4a41(grid):
    """Shift the right pattern upward and mirror the left wedge to the right."""
    height = len(grid)
    width = len(grid[0])

    # Clone so we can build the answer in-place.
    result = [row[:] for row in grid]

    # Identify the vertical split: first non-zero cell on the top row.
    top_row = grid[0]
    split_col = next((c for c, value in enumerate(top_row) if value != 0), width // 2)
    offset = split_col + 1

    # Copy the right-side details upward wherever the row below still has left-side 5s.
    rows_with_left_fives = [r for r in range(height) if any(grid[r][c] == 5 for c in range(split_col))]
    for src_row in rows_with_left_fives:
        dst_row = src_row - 1
        if dst_row < 0:
            continue
        for col in range(split_col + 1, width):
            result[dst_row][col] = grid[src_row][col]

    # Erase the left wedge and stamp it on the right with color 5.
    for r in range(height):
        for c in range(split_col):
            if c + offset < width and grid[r][c] == 5:
                result[r][c + offset] = 5
            result[r][c] = 0

    return result


p = solve_4c3d4a41
