"""Solver for ARC-AGI-2 task 221dfab4 (evaluation split)."""

from collections import Counter


def solve_221dfab4(grid):
    """Apply the row-stripe recoloring observed in the training cases."""
    height = len(grid)
    width = len(grid[0])

    counts = Counter(value for row in grid for value in row)
    background = counts.most_common(1)[0][0]

    stripe_columns = {
        c for c in range(width) if any(row[c] == 4 for row in grid)
    }
    object_colors = {color for color in counts if color not in (background, 4)}

    result = [row[:] for row in grid]

    for c in stripe_columns:
        for r in range(height):
            stripe_phase = r % 6
            if stripe_phase == 0:
                result[r][c] = 3
            elif stripe_phase in (2, 4):
                result[r][c] = 4
            else:
                result[r][c] = background

    for r in range(0, height, 6):
        for c in range(width):
            if c in stripe_columns:
                continue
            if grid[r][c] in object_colors:
                result[r][c] = 3

    return result


p = solve_221dfab4
