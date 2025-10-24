"""Typed-DSL style solver for ARC-AGI-2 task eee78d87 (evaluation split).

Refactored to match the Lambda Representation in abstractions.md while
preserving original semantics.
"""

from typing import List, Tuple

Grid = List[List[int]]
Cell = Tuple[int, int]

# Static row/column type maps and 4-value template palette.
ROW_TYPE_MAP: List[int] = [0, 1, 1, 0, 1, 2, 3, 2, 2, 3, 2, 1, 0, 1, 1, 0]
COL_TYPE_MAP: List[int] = ROW_TYPE_MAP

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


# --- Pure helpers (DSL-friendly) ---

def locateForegroundCenter(grid: Grid) -> Cell:
    # Compute center of the bounding box of non-7 cells
    coords = [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v != 7]
    if not coords:
        return (0, 0)
    rs = [r for r, _ in coords]
    cs = [c for _, c in coords]
    return ((min(rs) + max(rs)) // 2, (min(cs) + max(cs)) // 2)


def countNeighbourDirections(grid: Grid, centre: Cell) -> Tuple[int, int]:
    r0, c0 = centre

    def in_bounds(r: int, c: int) -> bool:
        return 0 <= r < len(grid) and 0 <= c < len(grid[0])

    def is_foreground(r: int, c: int) -> bool:
        return in_bounds(r, c) and grid[r][c] != 7

    orth = sum(1 for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)] if is_foreground(r0 + dr, c0 + dc))
    diag = sum(1 for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)] if is_foreground(r0 + dr, c0 + dc))
    return orth, diag


def selectTemplateKey(neighbour_counts: Tuple[int, int]) -> str:
    orth, diag = neighbour_counts
    if orth == 4:
        return "plus"
    if orth == 2:
        return "H"
    if diag == 4:
        return "X"
    return "plus"


def renderTemplate(template_id: str) -> Grid:
    table = TEMPLATES[template_id]
    h = len(ROW_TYPE_MAP)
    w = len(COL_TYPE_MAP)
    return [[table[ROW_TYPE_MAP[r]][COL_TYPE_MAP[c]] for c in range(w)] for r in range(h)]


def solve_eee78d87(grid: Grid) -> Grid:
    centre = locateForegroundCenter(grid)
    neighbour_counts = countNeighbourDirections(grid, centre)
    template_id = selectTemplateKey(neighbour_counts)
    return renderTemplate(template_id)


p = solve_eee78d87
