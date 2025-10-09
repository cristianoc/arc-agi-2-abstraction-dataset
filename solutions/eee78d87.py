"""Auto-generated identity stub for ARC-AGI-2 task eee78d87 (split: evaluation)."""

ROW_TYPE_MAP = [0, 1, 1, 0, 1, 2, 3, 2, 2, 3, 2, 1, 0, 1, 1, 0]
COL_TYPE_MAP = ROW_TYPE_MAP

TEMPLATES = {
    "plus": (
        (0, 0, 0, 0),
        (0, 7, 7, 0),
        (0, 7, 7, 9),
        (0, 0, 9, 9),
    ),
    "H": (
        (0, 0, 0, 0),
        (7, 0, 0, 7),
        (7, 0, 9, 7),
        (0, 0, 9, 9),
    ),
    "X": (
        (0, 7, 7, 0),
        (7, 0, 0, 7),
        (7, 0, 9, 7),
        (0, 7, 7, 9),
    ),
}

def solve_eee78d87(grid):
    """Select the appropriate 16x16 template based on the shape around the center."""
    coords = [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val != 7]
    if not coords:
        return [row[:] for row in grid]

    rows = [r for r, _ in coords]
    cols = [c for _, c in coords]
    center = ((min(rows) + max(rows)) // 2, (min(cols) + max(cols)) // 2)

    def count_neighbors(offsets):
        total = 0
        for dr, dc in offsets:
            rr, cc = center[0] + dr, center[1] + dc
            if 0 <= rr < len(grid) and 0 <= cc < len(grid[0]) and grid[rr][cc] != 7:
                total += 1
        return total

    orth = count_neighbors([(-1, 0), (1, 0), (0, -1), (0, 1)])
    diag = count_neighbors([(-1, -1), (-1, 1), (1, -1), (1, 1)])

    if orth == 4:
        key = "plus"
    elif orth == 2:
        key = "H"
    elif diag == 4:
        key = "X"
    else:
        key = "plus"

    template = TEMPLATES[key]
    return [
        [template[ROW_TYPE_MAP[r]][COL_TYPE_MAP[c]] for c in range(16)]
        for r in range(16)
    ]


p = solve_eee78d87
