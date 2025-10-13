"""Solver for ARC-AGI-2 task 36a08778."""


def _iter_runs(row, target=2):
    """Yield [start, end] column spans of consecutive `target` values."""
    start = None
    for idx, value in enumerate(row):
        if value == target:
            if start is None:
                start = idx
        elif start is not None:
            yield start, idx - 1
            start = None
    if start is not None:
        yield start, len(row) - 1


def solve_36a08778(grid):
    """
    Grow the scaffolding colour (6) downward from the seed columns and wrap
    2-runs that are connected to that scaffolding with a one-cell halo of 6s.
    """
    height = len(grid)
    width = len(grid[0])
    result = [row[:] for row in grid]

    # Identify seed columns: the columns that already contain colour 6
    # in the top two rows act as the vertical scaffolding sources.
    seed_cols = set()
    for r in range(min(2, height)):
        for c, value in enumerate(grid[r]):
            if value == 6:
                seed_cols.add(c)

    # Extend each scaffold column downward until a colour-2 barrier is hit.
    for c in seed_cols:
        for r in range(height):
            if grid[r][c] == 2:
                break
            if result[r][c] == 7:
                result[r][c] = 6

    # Process horizontal runs of 2s from top to bottom (skipping the first two
    # rows which stay unchanged). Only runs already touched by scaffolding are
    # wrapped with the 6 halo.
    for r in range(2, height):
        for left, right in _iter_runs(grid[r], target=2):
            run_len = right - left + 1
            touches_scaffold = any(
                result[r - 1][c] == 6 or result[r][c] == 6
                for c in range(left, right + 1)
            )
            if not touches_scaffold:
                continue

            left_neighbor = left - 1 if left > 0 else None
            right_neighbor = right + 1 if right + 1 < width else None

            if run_len > 1:
                for c in range(max(0, left - 1), min(width, right + 2)):
                    if result[r - 1][c] == 7:
                        result[r - 1][c] = 6
            else:
                c = right + 1
                if c < width and result[r - 1][c] == 7:
                    result[r - 1][c] = 6

            if run_len > 1 and left_neighbor is not None and result[r][left_neighbor] == 7:
                result[r][left_neighbor] = 6
            if right_neighbor is not None and result[r][right_neighbor] == 7:
                result[r][right_neighbor] = 6

            if run_len > 1 and left_neighbor is not None:
                for rr in range(r + 1, height):
                    if grid[rr][left_neighbor] == 2:
                        break
                    if result[rr][left_neighbor] == 7:
                        result[rr][left_neighbor] = 6

            if right_neighbor is not None:
                for rr in range(r + 1, height):
                    if grid[rr][right_neighbor] == 2:
                        break
                    if result[rr][right_neighbor] == 7:
                        result[rr][right_neighbor] = 6

    return result


p = solve_36a08778
