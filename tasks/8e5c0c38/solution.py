"""Solver for ARC-AGI-2 task 8e5c0c38 (evaluation split)."""

from collections import Counter, defaultdict


def solve_8e5c0c38(grid):
    """Remove asymmetric pixels so each color becomes horizontally symmetric."""

    background = Counter(pixel for row in grid for pixel in row).most_common(1)[0][0]

    result = [row[:] for row in grid]
    by_color = defaultdict(list)

    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value != background:
                by_color[value].append((r, c))

    for _, cells in by_color.items():
        if not cells:
            continue

        min_c = min(c for _, c in cells)
        max_c = max(c for _, c in cells)
        cells_set = set(cells)
        preferred_axis2 = min_c + max_c

        best_key = None
        best_removals = ()

        for axis2 in range(2 * min_c, 2 * max_c + 1):
            to_remove = [
                (r, c)
                for (r, c) in cells
                if (r, axis2 - c) not in cells_set
            ]
            key = (len(to_remove), abs(axis2 - preferred_axis2), axis2)
            if best_key is None or key < best_key:
                best_key = key
                best_removals = to_remove

        for r, c in best_removals:
            result[r][c] = background

    return result


p = solve_8e5c0c38
