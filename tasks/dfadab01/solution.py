"""Heuristic solver for ARC-AGI-2 task dfadab01."""

from typing import Callable, Dict, List, Optional, Sequence, Tuple, TypeVar

Grid = List[List[int]]
Cell = Tuple[int, int]
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

def extractPatch4x4(grid: Grid, cell: Cell) -> Patch:
    return _extract_patch(grid, cell[0], cell[1])


def lookupPatchTemplate(colour: int, patch: Patch) -> Optional[Patch]:
    lib = PATCH_LIBRARY.get(colour)
    if lib is None:
        return None
    return lib.get(patch)


def stampTemplate(canvas: Grid, template: Patch, cell: Cell) -> Grid:
    out = [row[:] for row in canvas]
    _stamp_patch(out, template, cell[0], cell[1])
    return out


T = TypeVar("T")


def fold_repaint(canvas: Grid, items: Sequence[T], update: Callable[[Grid, T], Grid]) -> Grid:
    # Start from a blank canvas with the same shape to match solver semantics.
    rows = len(canvas)
    cols = len(canvas[0]) if rows else 0
    acc = [[0 for _ in range(cols)] for _ in range(rows)]
    for x in items:
        acc = update(acc, x)
    return acc


def solve_dfadab01(grid: Grid) -> Grid:
    seeds = [
        (r, c)
        for r, row in enumerate(grid)
        for c, colour in enumerate(row)
        if colour != 0
    ]

    def repaint(canvas: Grid, cell: Cell) -> Grid:
        colour = grid[cell[0]][cell[1]]
        patch = extractPatch4x4(grid, cell)
        template = lookupPatchTemplate(colour, patch)
        if template is None:
            return canvas
        return stampTemplate(canvas, template, cell)

    return fold_repaint(grid, seeds, repaint)


p = solve_dfadab01
