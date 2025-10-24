"""Solver for ARC-AGI-2 task b99e7126."""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Set, Tuple, TypedDict

Grid = List[List[int]]
Tile = Tuple[Tuple[int, ...], ...]


class MacroGrid(TypedDict):
    tiles: List[List[Tile]]
    freq: Dict[Tile, int]
    rows: int
    cols: int


def splitMacroTiles(grid: Grid) -> MacroGrid:
    """Partition the board into 4-step aligned 3x3 tiles and tally them."""
    rows = len(grid)
    cols = len(grid[0])
    cell_rows = (rows - 1) // 4
    cell_cols = (cols - 1) // 4
    tiles: List[List[Tile]] = []
    freq: Dict[Tile, int] = {}
    for cr in range(cell_rows):
        row_tiles: List[Tile] = []
        rb = 1 + 4 * cr
        for cc in range(cell_cols):
            cb = 1 + 4 * cc
            tile: Tile = tuple(tuple(grid[rb + dr][cb:cb + 3]) for dr in range(3))
            row_tiles.append(tile)
            freq[tile] = freq.get(tile, 0) + 1
        tiles.append(row_tiles)
    return {"tiles": tiles, "freq": freq, "rows": cell_rows, "cols": cell_cols}


def chooseMinorityTile(macro_grid: MacroGrid) -> Optional[Tile]:
    """Select the least frequent tile (the motif); None if degenerate."""
    freq = macro_grid["freq"]
    if len(freq) <= 1:
        return None
    # The non-background 3x3 pattern appears only a handful of times – find it.
    return min(freq.items(), key=lambda item: item[1])[0]


def _majority_colour(tile: Tile) -> int:
    colour_counts = Counter(value for row in tile for value in row)
    return colour_counts.most_common(1)[0][0]


def alignMask(macro_grid: MacroGrid, motif: Optional[Tile]) -> Optional[List[Tuple[int, int]]]:
    """Locate the macro 3x3 window and return absolute macro cells to paint."""
    if motif is None:
        return None

    tiles = macro_grid["tiles"]
    cell_rows = macro_grid["rows"]
    cell_cols = macro_grid["cols"]

    majority_colour = _majority_colour(motif)
    mask: Set[Tuple[int, int]] = {(r, c) for r in range(3) for c in range(3) if motif[r][c] == majority_colour}

    present = [(cr, cc) for cr in range(cell_rows) for cc in range(cell_cols) if tiles[cr][cc] == motif]
    if not present:
        return None

    r0c0: Optional[Tuple[int, int]] = None
    for r0 in range(cell_rows - 2):
        for c0 in range(cell_cols - 2):
            if all((cr - r0, cc - c0) in mask for cr, cc in present):
                r0c0 = (r0, c0)
                break
        if r0c0 is not None:
            break
    if r0c0 is None:
        return None

    r0, c0 = r0c0
    return [(r0 + dr, c0 + dc) for (dr, dc) in mask]


def paintMotifTiles(grid: Grid, motif: Optional[Tile], alignment: Optional[List[Tuple[int, int]]]) -> Grid:
    """Copy the motif tile into every aligned macro cell position; no-op if unset."""
    result = [row[:] for row in grid]
    if motif is None or alignment is None:
        return result

    for cr, cc in alignment:
        rb = 1 + 4 * cr
        cb = 1 + 4 * cc
        for rr in range(3):
            for cc2 in range(3):
                result[rb + rr][cb + cc2] = motif[rr][cc2]
    return result


def solve_b99e7126(grid: Grid) -> Grid:
    macro_grid = splitMacroTiles(grid)
    motif = chooseMinorityTile(macro_grid)
    alignment = alignMask(macro_grid, motif)
    return paintMotifTiles(grid, motif, alignment)


p = solve_b99e7126
