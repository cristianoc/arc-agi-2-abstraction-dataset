"""Symmetrize ARC task 981571dc by reconstructing missing rows/columns."""

import numpy as np


def _find_completions(arr: np.ndarray) -> tuple[np.ndarray, bool]:
    """Fill rows that contain zeros using matching rows or columns."""
    n = arr.shape[0]
    arr = arr.copy()
    changed = False

    for i in range(n):
        row = arr[i]
        mask = row != 0
        if mask.all():
            continue

        candidates: list[tuple[int, int, int, np.ndarray]] = []

        # Candidate rows that already realise the visible colours.
        for j in range(n):
            if j == i:
                continue
            other = arr[j]
            if np.all(other[mask] == row[mask]):
                zero_count = int(np.sum(other == 0))
                candidates.append((zero_count, 0, j, other.copy()))

        # Candidate columns are evaluated against the same mask.
        for j in range(n):
            col = arr[:, j]
            if np.all(col[mask] == row[mask]):
                zero_count = int(np.sum(col == 0))
                candidates.append((zero_count, 1, j, col.copy()))

        if not candidates:
            continue

        zero_count, _, _, source = min(candidates, key=lambda item: (item[0], item[1], item[2]))
        before = row.copy()
        row[~mask] = source[~mask]
        if not np.array_equal(before, row):
            changed = True

    return arr, changed


def solve_981571dc(grid):
    """Rebuild the grid so that rows and columns agree and the matrix is symmetric."""
    arr = np.array(grid, dtype=int)
    while True:
        arr, row_changed = _find_completions(arr)
        arr_t, col_changed = _find_completions(arr.T)
        arr = arr_t.T
        if not (row_changed or col_changed):
            break

    # Mirror remaining zeros across the main diagonal to enforce symmetry.
    n = arr.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i, j] == 0 and arr[j, i] != 0:
                arr[i, j] = arr[j, i]
            elif arr[j, i] == 0 and arr[i, j] != 0:
                arr[j, i] = arr[i, j]

    return arr.tolist()


p = solve_981571dc
