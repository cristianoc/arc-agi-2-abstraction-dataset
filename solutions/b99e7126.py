"""Solver for ARC-AGI-2 task b99e7126."""

from __future__ import annotations

from collections import Counter
from typing import List

Grid = List[List[int]]


def _split_into_cells(grid: Grid):
    """Return the 4x4-aligned 3x3 tiles and their frequency."""
    rows = len(grid)
    cols = len(grid[0])
    cell_rows = (rows - 1) // 4
    cell_cols = (cols - 1) // 4
    tiles = []
    freq = Counter()
    for cr in range(cell_rows):
        row_tiles = []
        rb = 1 + 4 * cr
        for cc in range(cell_cols):
            cb = 1 + 4 * cc
            tile = tuple(tuple(grid[rb + dr][cb:cb + 3]) for dr in range(3))
            row_tiles.append(tile)
            freq[tile] += 1
        tiles.append(row_tiles)
    return tiles, freq


def solve_b99e7126(grid: Grid) -> Grid:
    """Infer the macro letter encoded in the minority tile and complete it."""
    result = [row[:] for row in grid]
    tiles, freq = _split_into_cells(grid)
    if len(freq) <= 1:
        return result

    # The non-background 3x3 pattern appears only a handful of times – find it.
    target_tile, _ = min(freq.items(), key=lambda item: item[1])
    rows = len(grid)
    cols = len(grid[0])
    cell_rows = (rows - 1) // 4
    cell_cols = (cols - 1) // 4

    # Build the binary mask given by the majority colour inside the 3x3 tile.
    colour_counts = Counter(value for row in target_tile for value in row)
    majority_colour = colour_counts.most_common(1)[0][0]
    mask = {(r, c) for r in range(3) for c in range(3) if target_tile[r][c] == majority_colour}

    # Locate the 3x3 window whose mask currently contains the observed tiles.
    present = [(cr, cc) for cr in range(cell_rows) for cc in range(cell_cols) if tiles[cr][cc] == target_tile]
    placement = None
    for r0 in range(cell_rows - 2):
        for c0 in range(cell_cols - 2):
            if all((cr - r0, cc - c0) in mask for cr, cc in present):
                placement = (r0, c0)
                break
        if placement is not None:
            break
    if placement is None:
        return result

    r0, c0 = placement
    # Paint the target tile into every position requested by the mask.
    for dr, dc in mask:
        cr = r0 + dr
        cc = c0 + dc
        rb = 1 + 4 * cr
        cb = 1 + 4 * cc
        for rr in range(3):
            for cc2 in range(3):
                result[rb + rr][cb + cc2] = target_tile[rr][cc2]

    return result


p = solve_b99e7126
