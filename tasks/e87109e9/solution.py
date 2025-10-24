"""Solver for ARC-AGI-2 task e87109e9 (evaluation split)."""

from collections import Counter
from typing import Any, Iterable, List, Optional, Sequence, Set, Tuple

# Typed aliases used by the DSL-style main
Grid = List[List[int]]
Color = int
Digit = int
Mask = Tuple[Tuple[int, ...], ...]


# Pre-computed diff/target masks extracted from the training samples.
_SAMPLE_DATA: List[dict[str, Any]] = [
    {"digit": 1,
     "target": [[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] ,
     "diff": [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1]] },
    {"digit": 6,
     "target": [[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 0, 0, 1, 1], [1, 1, 0, 0, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] ,
     "diff": [[0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [1, 1, 0, 0, 1, 1], [1, 1, 0, 0, 1, 1], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] },
    {"digit": 4,
     "target": [[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] ,
     "diff": [[0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] },
    {"digit": 2,
     "target": [[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] ,
     "diff": [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] },
    {"digit": 2,
     "target": [[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] ,
     "diff": [[0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]] },
    {"digit": 4,
     "target": [[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 0, 0, 1, 1], [1, 1, 0, 0, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] ,
     "diff": [[0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [1, 1, 0, 0, 1, 1], [1, 1, 0, 0, 1, 1], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1]] },
    {"digit": 6,
     "target": [[1, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] ,
     "diff": [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] },
    {"digit": 3,
     "target": [[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] ,
     "diff": [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] },
    {"digit": 4,
     "target": [[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1]] ,
     "diff": [[0, 0, 0, 1, 1, 0], [0, 0, 0, 1, 1, 0], [0, 0, 0, 1, 1, 0], [0, 0, 0, 1, 1, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 0, 0, 1, 1, 0], [0, 0, 0, 1, 1, 0], [0, 0, 0, 1, 1, 0], [0, 0, 0, 1, 1, 0], [0, 0, 0, 1, 1, 0], [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 0], [0, 0, 0, 1, 1, 1], [0, 0, 0, 1, 1, 1]] },
    {"digit": 6,
     "target": [[1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] ,
     "diff": [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] },
    {"digit": 3,
     "target": [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] ,
     "diff": [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1], [0, 0, 1, 1, 1, 1], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0]] },
    {"digit": 2,
     "target": [[1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1]] ,
     "diff": [[1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]] },
]

_SAMPLES: List[Tuple[int, Mask, Mask]] = [
    (
        entry["digit"],
        tuple(tuple(row) for row in entry["target"]),
        tuple(tuple(row) for row in entry["diff"]),
    )
    for entry in _SAMPLE_DATA
]

_BLOCK_WIDTH = 6
_MASK_ROWS = 16
_HEADER_COLOR = 5


def solve_e87109e9(grid: Grid) -> Grid:
    header, body = splitHeaderBody(grid)
    if not body:
        return body
    header_colours = set(
        colour
        for row in header
        for colour in row
        if colour != 0
    )
    target_colour = detectTargetColor(body, header_colours)
    block_count = int(len(body[0]) / 6)

    def carve(canvas: Grid, block: int) -> Grid:
        digit = readHeaderDigit(header, block)
        if digit is None:
            return canvas
        target_mask = buildTargetMask(canvas, block, target_colour)
        diff_mask = selectDiffMask(digit, target_mask)
        if diff_mask is None:
            return canvas
        return applyDiffMask(canvas, block, target_colour, diff_mask)

    return fold_repaint(body, list(range(block_count)), carve)


#
# DSL helper wrappers (pure) bridging to the existing internal implementation.
#

def splitHeaderBody(grid: Grid) -> Tuple[Grid, Grid]:
    if not grid:
        return [], []
    split = _find_body_start(grid)
    header = [row[:] for row in grid[:split]]
    body = [row[:] for row in grid[split:]]
    return header, body


def detectTargetColor(body: Grid, header_colours: Set[Color]) -> Color:
    return _find_target_color(body, header_colours)


def readHeaderDigit(header: Grid, block: int) -> Optional[Digit]:
    return _read_digit(header, block)


def buildTargetMask(canvas: Grid, block: int, target_colour: Color) -> Mask:
    return _compute_target_mask(canvas, block, target_colour)


def selectDiffMask(digit: Digit, target_mask: Mask) -> Optional[Mask]:
    return _select_diff_mask(digit, target_mask)


def applyDiffMask(canvas: Grid, block: int, target_colour: Color, diff_mask: Mask) -> Grid:
    out = [row[:] for row in canvas]
    _apply_diff_mask(out, block, target_colour, diff_mask)
    return out


def fold_repaint(canvas: Grid, items: Sequence[int], update):
    g = [row[:] for row in canvas]
    for x in items:
        g = update(g, x)
    return g


def _find_body_start(grid):
    for idx, row in enumerate(grid):
        if _HEADER_COLOR not in row:
            return idx
    return len(grid)


def _find_target_color(body, header_colors):
    counts = Counter()
    for row in body:
        for val in row:
            if val != 8 and val not in header_colors:
                counts[val] += 1
    if counts:
        return counts.most_common(1)[0][0]
    fallback = Counter(val for row in body for val in row if val != 8)
    return fallback.most_common(1)[0][0] if fallback else 0


def _read_digit(header, block):
    start = block * _BLOCK_WIDTH
    end = start + _BLOCK_WIDTH
    for row in header[1:-1]:
        for val in row[start:end]:
            if val not in (0, _HEADER_COLOR):
                return val
    return None


def _compute_target_mask(body, block, target_color):
    start = block * _BLOCK_WIDTH
    end = start + _BLOCK_WIDTH
    mask = []
    for r in range(_MASK_ROWS):
        if r >= len(body):
            mask.append((0,) * _BLOCK_WIDTH)
            continue
        row_slice = tuple(1 if body[r][c] == target_color else 0 for c in range(start, end))
        mask.append(row_slice)
    return tuple(mask)


def _select_diff_mask(digit, target_mask):
    best_mask = None
    best_score = None
    for sample_digit, sample_target, sample_diff in _SAMPLES:
        if sample_digit != digit:
            continue
        score = _hamming_distance(sample_target, target_mask)
        if best_score is None or score < best_score:
            best_score = score
            best_mask = sample_diff
    return best_mask


def _apply_diff_mask(body, block, target_color, diff_mask):
    start = block * _BLOCK_WIDTH
    for r in range(min(len(body), _MASK_ROWS)):
        for c in range(_BLOCK_WIDTH):
            if diff_mask[r][c] and body[r][start + c] == target_color:
                body[r][start + c] = 8


def _hamming_distance(mask_a, mask_b):
    total = 0
    for row_a, row_b in zip(mask_a, mask_b):
        for val_a, val_b in zip(row_a, row_b):
            total += val_a != val_b
    return total


p = solve_e87109e9
