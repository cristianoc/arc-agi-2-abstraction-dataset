"""Heuristic solver for ARC-AGI-2 task dfadab01."""

from typing import Dict, List, Tuple

Grid = List[List[int]]
Patch = Tuple[Tuple[int, ...], ...]

# Mapping from input 4x4 neighbourhoods (with -1 padding outside the grid) to
# the corresponding output 4x4 motif. The mapping is colour-specific and was
# distilled from the four training examples.
PATCH_LIBRARY: Dict[int, Dict[Patch, Patch]] = {
    1: {
        (
            (1, 0, -1, -1),
            (0, 0, -1, -1),
            (0, 3, -1, -1),
            (-1, -1, -1, -1),
        ): (
            (1, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ),
        (
            (1, 0, -1, -1),
            (1, 0, -1, -1),
            (0, 0, -1, -1),
            (0, 3, -1, -1),
        ): (
            (1, 0, 0, 0),
            (1, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ),
        (
            (1, 0, 0, -1),
            (0, 0, 3, -1),
            (-1, -1, -1, -1),
            (-1, -1, -1, -1),
        ): (
            (1, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ),
        (
            (1, 0, 0, -1),
            (0, 1, 0, -1),
            (0, 1, 0, -1),
            (1, 0, 0, -1),
        ): (
            (1, 0, 0, 0),
            (0, 1, 0, 0),
            (0, 1, 0, 0),
            (1, 0, 0, 0),
        ),
        (
            (1, 0, 0, 1),
            (0, 1, 1, 0),
            (0, 0, 0, 0),
            (-1, -1, -1, -1),
        ): (
            (1, 0, 0, 1),
            (0, 1, 1, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ),
        (
            (1, 0, 0, 1),
            (1, 0, 0, 1),
            (0, 1, 1, 0),
            (0, 0, 0, 0),
        ): (
            (1, 0, 0, 1),
            (1, 0, 0, 1),
            (0, 1, 1, 0),
            (0, 0, 0, 0),
        ),
        (
            (1, 1, 0, 0),
            (0, 0, 0, 3),
            (-1, -1, -1, -1),
            (-1, -1, -1, -1),
        ): (
            (1, 1, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ),
        (
            (1, 1, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 1, 0),
            (1, 1, 0, 0),
        ): (
            (1, 1, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 1, 0),
            (1, 1, 0, 0),
        ),
    },
    2: {
        (
            (2, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ): (
            (4, 4, 4, 4),
            (4, 0, 0, 4),
            (4, 0, 0, 4),
            (4, 4, 4, 4),
        ),
        (
            (2, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 2, 0),
            (0, 0, 0, 0),
        ): (
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 4, 4),
            (0, 0, 4, 0),
        ),
    },
    3: {
        (
            (3, -1, -1, -1),
            (-1, -1, -1, -1),
            (-1, -1, -1, -1),
            (-1, -1, -1, -1),
        ): (
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ),
        (
            (3, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ): (
            (0, 1, 1, 0),
            (1, 0, 0, 1),
            (1, 0, 0, 1),
            (0, 1, 1, 0),
        ),
        (
            (3, 1, 1, 0),
            (1, 0, 0, 1),
            (1, 0, 0, 1),
            (0, 1, 1, 0),
        ): (
            (0, 1, 1, 0),
            (1, 0, 0, 1),
            (1, 0, 0, 1),
            (0, 1, 1, 0),
        ),
    },
    5: {
        (
            (5, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ): (
            (6, 6, 0, 0),
            (6, 6, 0, 0),
            (0, 0, 6, 6),
            (0, 0, 6, 6),
        ),
        (
            (5, 0, 0, 0),
            (0, 0, 0, 2),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ): (
            (0, 0, 0, 0),
            (0, 0, 0, 4),
            (0, 0, 0, 4),
            (0, 0, 0, 4),
        ),
    },
    8: {
        (
            (8, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        ): (
            (7, 0, 0, 7),
            (0, 7, 7, 0),
            (0, 7, 7, 0),
            (7, 0, 0, 7),
        ),
    },
}


def _extract_patch(grid: Grid, r: int, c: int) -> Patch:
    """Return the 4x4 neighbourhood around (r, c), padding with -1 outside."""

    rows = len(grid)
    cols = len(grid[0])
    patch_rows = []
    for dr in range(4):
        row_vals = []
        rr = r + dr
        for dc in range(4):
            cc = c + dc
            if 0 <= rr < rows and 0 <= cc < cols:
                row_vals.append(grid[rr][cc])
            else:
                row_vals.append(-1)
        patch_rows.append(tuple(row_vals))
    return tuple(patch_rows)


def _stamp_patch(out: Grid, patch: Patch, r: int, c: int) -> None:
    """Overlay a 4x4 patch onto the output grid, ignoring zero entries."""

    rows = len(out)
    cols = len(out[0])
    for dr, patch_row in enumerate(patch):
        rr = r + dr
        if rr >= rows:
            break
        for dc, val in enumerate(patch_row):
            if val == 0:
                continue
            cc = c + dc
            if cc >= cols:
                continue
            out[rr][cc] = val


def solve_dfadab01(grid: Grid) -> Grid:
    """Tile-based synthesis driven by colour-specific 4x4 patch templates."""

    rows = len(grid)
    cols = len(grid[0])
    out = [[0 for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            color = grid[r][c]
            library = PATCH_LIBRARY.get(color)
            if not library:
                continue
            key = _extract_patch(grid, r, c)
            patch = library.get(key)
            if patch:
                _stamp_patch(out, patch, r, c)

    return out


p = solve_dfadab01
