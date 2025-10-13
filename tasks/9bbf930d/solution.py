"""Solver for ARC-AGI-2 task 9bbf930d (split: evaluation)."""

from collections import Counter


ROW_MOSTLY7_THRESHOLD = 4
COL_NON_THRESHOLD = 4


def _dominant_color(sequence):
    """Return the unique most common non-(6,7) color or None if tied/absent."""
    counts = Counter(value for value in sequence if value not in (6, 7))
    if not counts:
        return None
    ranked = counts.most_common()
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return None
    return ranked[0][0]


def _row_non_count(row):
    return sum(1 for value in row if value not in (6, 7))


def solve_9bbf930d(grid):
    """Recolour separator rows/columns to highlight repeated row bands."""
    rows = len(grid)
    cols = len(grid[0])
    result = [row[:] for row in grid]

    row_non_counts = [_row_non_count(row) for row in grid]
    row_dominants = [_dominant_color(row) for row in grid]

    # Step 1: adjust separator rows that sit between identical dominant rows.
    for r in range(1, rows - 1):
        if row_non_counts[r] > ROW_MOSTLY7_THRESHOLD:
            continue
        up_dom = row_dominants[r - 1]
        down_dom = row_dominants[r + 1]
        if up_dom is None or down_dom is None or up_dom != down_dom:
            continue
        result[r][0] = 7
        if result[r][cols - 1] == 7:
            result[r][cols - 1] = 6

    # Step 2: analyse sparse columns of 7s to move 6-markers to key junctions.
    column_counts = [Counter(val for val in column if val not in (6, 7))
                     for column in zip(*grid)]
    candidate_columns = [
        c for c, counts in enumerate(column_counts)
        if 2 <= c < cols - 1 and 0 < sum(counts.values()) <= COL_NON_THRESHOLD
    ]

    for c in candidate_columns:
        # Top boundary: move the topmost 6 to the far edge when the column starts with 7s.
        if (grid[0][c] == 7 and rows > 1 and grid[1][c] == 7
                and row_non_counts[1] <= ROW_MOSTLY7_THRESHOLD
                and any(grid[r][c] != 7 for r in range(2, rows))):
            result[0][c] = 6

        for r in range(rows):
            if result[r][c] != 7:
                continue

            down_val = grid[r + 1][c] if r + 1 < rows else None

            # Rows that already contain non-7 content: mark when the colour band below is symmetric.
            if (r + 1 < rows - 1 and down_val != 7
                    and row_non_counts[r] >= 1):
                down_dom = row_dominants[r + 1]
                up_dom = row_dominants[r - 1] if r > 0 else None
                if (down_dom is not None and down_dom != up_dom
                        and grid[r + 1][c - 1] == grid[r + 1][c + 1]):
                    result[r][c] = 6
                    continue

            # Nearly pure separator rows: only mark when the new colour is small and symmetric.
            if (r + 1 < rows - 1 and down_val != 7
                    and row_non_counts[r] <= 1 and down_val is not None and down_val <= 6
                    and grid[r + 1][c - 1] == grid[r + 1][c + 1] == down_val):
                down_dom = row_dominants[r + 1]
                up_dom = row_dominants[r - 1] if r > 0 else None
                if down_dom is not None and down_dom != up_dom:
                    result[r][c] = 6
                    continue

            # Bottom boundary always ends with a 6 when the column is sparse.
            if r == rows - 1:
                result[r][c] = 6

    return result


p = solve_9bbf930d
