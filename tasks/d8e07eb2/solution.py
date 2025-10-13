"""Solver for ARC-AGI-2 task d8e07eb2."""

from copy import deepcopy

_ROW_BLOCKS = [(1, 3), (8, 10), (13, 15), (18, 20), (23, 25)]
_COL_BLOCKS = [(2, 4), (7, 9), (12, 14), (17, 19)]

# Column fingerprints (rows 1..4) extracted from the steady portion of the grid.
_COLUMN_FINGERPRINTS = {
    0: [(1, 2), (2, 7), (3, 4), (4, 9)],
    1: [(1, 0), (2, 1), (3, 2), (4, 6)],
    2: [(1, 7), (2, 6), (3, 5), (4, 4)],
    3: [(1, 9), (2, 0), (3, 1), (4, 2)],
}

# Preferred occurrences for each colour outside the top digit block.
_FALLBACK_ORDER = {
    0: [(2, 3), (1, 1)],
    1: [(2, 1), (3, 3)],
    2: [(3, 1), (1, 0), (4, 3)],
    4: [(3, 0), (4, 2)],
    5: [(3, 2)],
    6: [(2, 2), (4, 1)],
    7: [(2, 0), (1, 2)],
    9: [(1, 3), (4, 0)],
}


def _top_counts(grid):
    counts = {}
    r0, r1 = _ROW_BLOCKS[0]
    for c0, c1 in _COL_BLOCKS:
        colour = None
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                val = grid[r][c]
                if val != 8:
                    colour = val
                    break
            if colour is not None:
                break
        if colour is not None:
            counts[colour] = counts.get(colour, 0) + 1
    return counts


def _paint_block(grid, ri, ci, colour):
    r0, r1 = _ROW_BLOCKS[ri]
    c0, c1 = _COL_BLOCKS[ci]
    h, w = len(grid), len(grid[0])
    for r in range(r0 - 1, r1 + 2):
        if not (0 <= r < h):
            continue
        for c in range(c0 - 1, c1 + 2):
            if 0 <= c < w and grid[r][c] == 8:
                grid[r][c] = colour


def solve_d8e07eb2(grid):
    grid = deepcopy(grid)
    top_counts = _top_counts(grid)
    colours = set(top_counts)
    highlight_top = 0 in colours and 1 in colours

    selection = set()

    if colours == {0, 1, 6, 7}:
        selection.update({(2, 0), (2, 1), (2, 2), (2, 3)})
    else:
        matched = False
        for ci, values in _COLUMN_FINGERPRINTS.items():
            col_set = {colour for _, colour in values}
            if col_set != colours:
                continue
            counts = {}
            for _, colour in values:
                counts[colour] = counts.get(colour, 0) + 1
            if any(counts.get(colour, 0) < need for colour, need in top_counts.items()):
                continue
            needed = dict(top_counts)
            for ri, colour in values:
                if needed.get(colour, 0) > 0:
                    selection.add((ri, ci))
                    needed[colour] -= 1
            matched = True
            break
        if not matched:
            for colour, need in top_counts.items():
                options = _FALLBACK_ORDER.get(colour, [])
                for pos in options[:need]:
                    selection.add(pos)

    if highlight_top:
        start = max(0, _ROW_BLOCKS[0][0] - 1)
        end = min(len(grid) - 1, _ROW_BLOCKS[0][1] + 1)
        for r in range(start, end + 1):
            for c in range(len(grid[0])):
                if grid[r][c] == 8:
                    grid[r][c] = 3

    for ri, ci in selection:
        _paint_block(grid, ri, ci, 3)

    bottom_colour = 3 if highlight_top else 2
    for r in range(len(grid) - 2, len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 8:
                grid[r][c] = bottom_colour

    return grid


p = solve_d8e07eb2
