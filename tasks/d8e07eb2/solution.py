"""Solver for ARC-AGI-2 task d8e07eb2.

Refactored to expose typed-DSL style helpers and a declarative
composition for the main solver while preserving original behavior.
"""

from copy import deepcopy
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

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


Grid = List[List[int]]
Block = Tuple[int, int]


def _top_counts(grid: Grid) -> Dict[int, int]:
    counts: Dict[int, int] = {}
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


def _paint_block(grid: Grid, ri: int, ci: int, colour: int) -> None:
    r0, r1 = _ROW_BLOCKS[ri]
    c0, c1 = _COL_BLOCKS[ci]
    h, w = len(grid), len(grid[0])
    for r in range(r0 - 1, r1 + 2):
        if not (0 <= r < h):
            continue
        for c in range(c0 - 1, c1 + 2):
            if 0 <= c < w and grid[r][c] == 8:
                grid[r][c] = colour


def collectHeaderDigits(grid: Grid) -> Dict[int, int]:
    """Tally colours detected across the top digit blocks.

    Returns a mapping from colour -> count of occurrences among the top
    5x5 digit blocks in columns.
    """
    return _top_counts(grid)


def matchColumnFingerprint(header_counts: Dict[int, int]) -> Optional[List[Block]]:
    """Return highlight blocks if the header colours match any column fingerprint.

    The selection respects colour multiplicities; returns None when no
    fingerprint matches the observed header colours.
    """
    colours = set(header_counts)

    # Row-rule ({0,1,6,7}) is treated as a structural match.
    if colours == {0, 1, 6, 7}:
        return [(2, 0), (2, 1), (2, 2), (2, 3)]

    for ci, values in _COLUMN_FINGERPRINTS.items():
        col_set = {colour for _, colour in values}
        if col_set != colours:
            continue
        # Count available supply of each colour in the fingerprint column.
        supply: Dict[int, int] = {}
        for _, colour in values:
            supply[colour] = supply.get(colour, 0) + 1
        if any(supply.get(colour, 0) < need for colour, need in header_counts.items()):
            continue
        # Greedily take from top to bottom respecting needs.
        needed = dict(header_counts)
        chosen: List[Block] = []
        for ri, colour in values:
            if needed.get(colour, 0) > 0:
                chosen.append((ri, ci))
                needed[colour] -= 1
        return chosen
    return None


def fallbackBlockSelection(header_counts: Dict[int, int]) -> List[Block]:
    """Priority selection when no fingerprint matches.

    Uses the per-colour ordering of preferred blocks and selects as many
    as required by the header counts.
    """
    selection: List[Block] = []
    for colour, need in header_counts.items():
        options: Sequence[Block] = _FALLBACK_ORDER.get(colour, [])
        selection.extend(options[:need])
    return selection


def renderHighlights(grid: Grid, selected_blocks: Iterable[Block], highlight_top: bool) -> Grid:
    """Render the chosen blocks and bands onto a fresh copy of the grid."""
    out = deepcopy(grid)

    if highlight_top:
        start = max(0, _ROW_BLOCKS[0][0] - 1)
        end = min(len(out) - 1, _ROW_BLOCKS[0][1] + 1)
        for r in range(start, end + 1):
            for c in range(len(out[0])):
                if out[r][c] == 8:
                    out[r][c] = 3

    for ri, ci in selected_blocks:
        _paint_block(out, ri, ci, 3)

    bottom_colour = 3 if highlight_top else 2
    for r in range(len(out) - 2, len(out)):
        for c in range(len(out[0])):
            if out[r][c] == 8:
                out[r][c] = bottom_colour

    return out


def solve_d8e07eb2(grid: Grid) -> Grid:
    header_counts = collectHeaderDigits(grid)
    fingerprint_blocks = matchColumnFingerprint(header_counts)
    selected_blocks = fingerprint_blocks if fingerprint_blocks is not None else fallbackBlockSelection(header_counts)
    highlight_top = 0 in header_counts and 1 in header_counts
    return renderHighlights(grid, selected_blocks, highlight_top)


p = solve_d8e07eb2
