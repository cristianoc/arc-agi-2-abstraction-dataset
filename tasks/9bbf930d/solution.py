"""Solver for ARC-AGI-2 task 9bbf930d (split: evaluation)."""

from __future__ import annotations

from collections import Counter
from typing import List, Optional, Tuple


# Local type alias to satisfy typing/static checks in this repository
Grid = List[List[int]]


ROW_MOSTLY7_THRESHOLD = 4
COL_NON_THRESHOLD = 4


def _dominant_color(sequence: List[int]) -> Optional[int]:
    """Return the unique most common non-(6,7) color or None if tied/absent."""
    counts = Counter(value for value in sequence if value not in (6, 7))
    if not counts:
        return None
    ranked = counts.most_common()
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return None
    return ranked[0][0]


def _row_non_count(row: List[int]) -> int:
    return sum(1 for value in row if value not in (6, 7))


# --- DSL-aligned helper operations ----------------------------------------

def analyseRows(grid: Grid) -> Tuple[List[int], List[Optional[int]]]:
    """Compute per-row non-(6,7) counts and dominant colours."""
    row_non_counts = [_row_non_count(row) for row in grid]
    row_dominants = [_dominant_color(row) for row in grid]
    return row_non_counts, row_dominants


def adjustSeparatorRows(grid: Grid, metrics: Tuple[List[int], List[Optional[int]]]) -> Grid:
    """Recolour separator rows when neighbouring dominant colours match."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    result = [row[:] for row in grid]
    row_non_counts, row_dominants = metrics

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
    return result


def selectSparseColumns(grid: Grid) -> List[int]:
    """Find columns with few non-(6,7) cells to inspect for 6 placement."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    column_counts = [Counter(val for val in column if val not in (6, 7)) for column in zip(*grid)]
    return [
        c
        for c, counts in enumerate(column_counts)
        if 2 <= c < cols - 1 and 0 < sum(counts.values()) <= COL_NON_THRESHOLD
    ]


def markColumnJunctions(grid: Grid, metrics: Tuple[List[int], List[Optional[int]]], sparse_columns: List[int]) -> Grid:
    """Place colour-6 markers in sparse columns using learnt heuristics (caps, thin towers)."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    result = [row[:] for row in grid]
    row_non_counts, row_dominants = metrics

    for c in sparse_columns:
        # Top boundary: move the topmost 6 to the far edge when the column starts with 7s.
        if (
            grid[0][c] == 7
            and rows > 1
            and grid[1][c] == 7
            and row_non_counts[1] <= ROW_MOSTLY7_THRESHOLD
            and any(grid[r][c] != 7 for r in range(2, rows))
        ):
            result[0][c] = 6

        for r in range(rows):
            if result[r][c] != 7:
                continue

            down_val = grid[r + 1][c] if r + 1 < rows else None

            # Rows that already contain non-7 content: mark when the colour band below is symmetric.
            if r + 1 < rows - 1 and down_val != 7 and row_non_counts[r] >= 1:
                down_dom = row_dominants[r + 1]
                up_dom = row_dominants[r - 1] if r > 0 else None
                if (
                    down_dom is not None
                    and down_dom != up_dom
                    and grid[r + 1][c - 1] == grid[r + 1][c + 1]
                ):
                    result[r][c] = 6
                    continue

            # Nearly pure separator rows: only mark when the new colour is small and symmetric.
            if (
                r + 1 < rows - 1
                and down_val != 7
                and row_non_counts[r] <= 1
                and down_val is not None
                and down_val <= 6
                and grid[r + 1][c - 1] == grid[r + 1][c + 1] == down_val
            ):
                down_dom = row_dominants[r + 1]
                up_dom = row_dominants[r - 1] if r > 0 else None
                if down_dom is not None and down_dom != up_dom:
                    result[r][c] = 6
                    continue

            # Bottom boundary always ends with a 6 when the column is sparse.
            if r == rows - 1:
                result[r][c] = 6

    return result


# --- Solver entrypoint (must match abstractions.md Lambda Representation) ---

def solve_9bbf930d(grid: Grid) -> Grid:
    metrics = analyseRows(grid)
    adjusted = adjustSeparatorRows(grid, metrics)
    sparse_columns = selectSparseColumns(adjusted)
    return markColumnJunctions(adjusted, metrics, sparse_columns)


p = solve_9bbf930d
