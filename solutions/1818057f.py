"""Solver for ARC-AGI-2 task 1818057f.

The puzzle replaces every `4`-colored plus (a center cell whose four
von-Neumann neighbours are also `4`) with the color `8`. All other cells remain
untouched. The plus detection is performed on the original grid so overlapping
updates do not interfere with one another.
"""


def solve_1818057f(grid):
    height = len(grid)
    width = len(grid[0]) if height else 0
    result = [row[:] for row in grid]

    for r in range(1, height - 1):
        for c in range(1, width - 1):
            if grid[r][c] != 4:
                continue

            if all(grid[r + dr][c + dc] == 4 for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                result[r][c] = 8
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    result[r + dr][c + dc] = 8

    return result


p = solve_1818057f
