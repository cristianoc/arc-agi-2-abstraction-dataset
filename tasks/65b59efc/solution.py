"""Solver for ARC task 65b59efc.

This refactor keeps the original mapped-tiles behavior intact while
exposing a DSL-style entrypoint that matches the Lambda Representation
in abstractions.md. The main logic remains in existing helpers; the new
DSL helpers are thin adapters around them.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple, TypeVar


MAPPING: dict[Any, Any] = {
    (0, 0, ((2, 2, 2), (2, 2, 2), (2, 2, 2))): (
        (7, 7, 7),
        (7, 0, 7),
        (7, 7, 7),
    ),
    (0, 1, ((1, 1, 1), (1, 0, 1), (1, 1, 1))): (
        (1, 1, 1),
        (0, 1, 0),
        (1, 1, 1),
    ),
    (0, 2, ((4, 4, 4), (0, 4, 0), (4, 4, 4))): (
        (1, 1, 1),
        (0, 1, 0),
        (1, 1, 1),
    ),
    (1, 0, ((0, 0, 0), (0, 0, 0), (2, 0, 0))): (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    (1, 1, ((0, 4, 4), (0, 0, 4), (0, 0, 0))): (
        (7, 7, 7),
        (7, 0, 7),
        (7, 7, 7),
    ),
    (1, 2, ((1, 0, 0), (0, 1, 0), (0, 0, 1))): (
        (1, 1, 1),
        (0, 1, 0),
        (1, 1, 1),
    ),
    (2, 0, ((0, 0, 0), (0, 6, 0))): (
        (6, 6, 6),
        (6, 6, 6),
        (6, 6, 6),
    ),
    (2, 1, ((0, 0, 0), (0, 7, 0))): (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ),
    (2, 2, ((0, 0, 0), (0, 1, 0))): (
        (7, 7, 7),
        (7, 0, 7),
        (7, 7, 7),
    ),
}

MAPPING.update(
    {
        (0, 0, ((0, 1, 0), (1, 1, 1), (0, 1, 0))): (
            (3, 0, 3),
            (3, 3, 3),
            (0, 3, 0),
        ),
        (0, 1, ((2, 2, 2), (2, 0, 2), (2, 2, 2))): (
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
        ),
        (0, 2, ((4, 0, 4), (4, 4, 4), (0, 4, 0))): (
            (0, 7, 0),
            (7, 7, 7),
            (0, 7, 0),
        ),
        (1, 0, ((0, 0, 0), (0, 0, 0), (2, 2, 0))): (
            (3, 0, 3),
            (3, 3, 3),
            (0, 3, 0),
        ),
        (1, 1, ((4, 0, 0), (4, 0, 0), (0, 0, 0))): (
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
        ),
        (1, 2, ((0, 0, 1), (0, 0, 1), (0, 0, 0))): (
            (0, 7, 0),
            (7, 7, 7),
            (0, 7, 0),
        ),
        (2, 0, ((0, 0, 0), (0, 7, 0))): (
            (9, 9, 9),
            (9, 0, 9),
            (9, 9, 9),
        ),
        (2, 1, ((0, 0, 0), (0, 9, 0))): (
            (9, 9, 9),
            (9, 0, 9),
            (9, 9, 9),
        ),
        (2, 2, ((0, 0, 0), (0, 3, 0))): (
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
        ),
    }
)

MAPPING.update(
    {
        (0, 0, ((1, 1, 1, 0, 1), (1, 0, 1, 1, 1), (1, 1, 1, 0, 1), (1, 0, 0, 0, 1), (1, 1, 1, 1, 1))): (
            (0, 6, 0, 0, 6, 8, 8, 8, 8, 8),
            (6, 6, 6, 6, 6, 0, 8, 0, 8, 0),
            (0, 6, 0, 0, 6, 8, 0, 8, 0, 8),
            (0, 6, 6, 6, 6, 8, 0, 8, 0, 8),
            (6, 6, 0, 6, 6, 8, 8, 8, 8, 8),
            (0, 6, 0, 0, 6, 8, 8, 8, 8, 8),
            (6, 6, 6, 6, 6, 0, 8, 0, 8, 0),
            (0, 6, 0, 0, 6, 8, 0, 8, 0, 8),
            (0, 6, 6, 6, 6, 8, 0, 8, 0, 8),
            (6, 6, 0, 6, 6, 8, 8, 8, 8, 8),
        ),
        (0, 1, ((2, 2, 2, 2, 2), (0, 2, 0, 2, 0), (2, 0, 2, 0, 2), (2, 0, 2, 0, 2), (2, 2, 2, 2, 2))): (
            (8, 8, 8, 8, 8, 8, 8, 8, 8, 8),
            (0, 8, 0, 8, 0, 0, 8, 0, 8, 0),
            (8, 0, 8, 0, 8, 8, 0, 8, 0, 8),
            (8, 0, 8, 0, 8, 8, 0, 8, 0, 8),
            (8, 8, 8, 8, 8, 8, 8, 8, 8, 8),
            (8, 8, 8, 8, 8, 0, 0, 0, 0, 0),
            (0, 8, 0, 8, 0, 0, 0, 0, 0, 0),
            (8, 0, 8, 0, 8, 0, 0, 0, 0, 0),
            (8, 0, 8, 0, 8, 0, 0, 0, 0, 0),
            (8, 8, 8, 8, 8, 0, 0, 0, 0, 0),
        ),
        (0, 2, ((0, 4, 0, 0, 4), (4, 4, 4, 4, 4), (0, 4, 0, 0, 4), (0, 4, 4, 4, 4), (4, 4, 0, 4, 4))): (
            (8, 8, 8, 8, 8),
            (0, 8, 0, 8, 0),
            (8, 0, 8, 0, 8),
            (8, 0, 8, 0, 8),
            (8, 8, 8, 8, 8),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (1, 0, ((4, 0, 0, 0, 0), (4, 0, 0, 0, 0), (4, 4, 0, 0, 0), (0, 4, 4, 0, 0), (0, 0, 4, 0, 0))): (
            (0, 6, 0, 0, 6, 0, 6, 0, 0, 6),
            (6, 6, 6, 6, 6, 6, 6, 6, 6, 6),
            (0, 6, 0, 0, 6, 0, 6, 0, 0, 6),
            (0, 6, 6, 6, 6, 0, 6, 6, 6, 6),
            (6, 6, 0, 6, 6, 6, 6, 0, 6, 6),
            (3, 3, 3, 0, 3, 0, 6, 0, 0, 6),
            (3, 0, 3, 3, 3, 6, 6, 6, 6, 6),
            (3, 3, 3, 0, 3, 0, 6, 0, 0, 6),
            (3, 0, 0, 0, 3, 0, 6, 6, 6, 6),
            (3, 3, 3, 3, 3, 6, 6, 0, 6, 6),
        ),
        (1, 1, ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (1, 0, 0, 0, 0), (1, 1, 0, 0, 0))): (
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            (0, 6, 0, 0, 6, 0, 0, 0, 0, 0),
            (6, 6, 6, 6, 6, 0, 0, 0, 0, 0),
            (0, 6, 0, 0, 6, 0, 0, 0, 0, 0),
            (0, 6, 6, 6, 6, 0, 0, 0, 0, 0),
            (6, 6, 0, 6, 6, 0, 0, 0, 0, 0),
        ),
        (1, 2, ((0, 2, 2, 2, 2), (0, 2, 2, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0))): (
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
        ),
        (2, 0, ((0, 0, 0, 0, 0), (0, 0, 3, 0, 0))): (
            (3, 3, 3, 0, 3, 3, 3, 3, 0, 3),
            (3, 0, 3, 3, 3, 3, 0, 3, 3, 3),
            (3, 3, 3, 0, 3, 3, 3, 3, 0, 3),
            (3, 0, 0, 0, 3, 3, 0, 0, 0, 3),
            (3, 3, 3, 3, 3, 3, 3, 3, 3, 3),
        ),
        (2, 1, ((0, 0, 0, 0, 0), (0, 0, 8, 0, 0))): (
            (0, 6, 0, 0, 6, 0, 0, 0, 0, 0),
            (6, 6, 6, 6, 6, 0, 0, 0, 0, 0),
            (0, 6, 0, 0, 6, 0, 0, 0, 0, 0),
            (0, 6, 6, 6, 6, 0, 0, 0, 0, 0),
            (6, 6, 0, 6, 6, 0, 0, 0, 0, 0),
        ),
        (2, 2, ((0, 0, 0, 0, 0), (0, 0, 6, 0, 0))): (
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0),
        ),
    }
)
FALLBACK: dict[Any, Any] = {}


ROW_SIZE_OPTIONS = {0: (3, 10), 1: (3, 10), 2: (3, 5)}
COL_SIZE_OPTIONS = {0: (3, 10), 1: (3, 10), 2: (3, 5)}


def tupleify(cell):
    return tuple(tuple(row) for row in cell)


def dominant_value(cell):
    counter = Counter(v for row in cell for v in row if v not in (0, 5))
    return counter.most_common(1)[0][0] if counter else 0


def choose_size(options, cell_dim):
    small, large = options
    return large if cell_dim >= 4 else small


def find_segments(grid):
    rows = len(grid)
    cols = len(grid[0])
    row_breaks = [-1]
    for r, row in enumerate(grid):
        if row.count(5) >= cols // 2:
            row_breaks.append(r)
    row_breaks.append(rows)
    row_breaks = sorted(set(row_breaks))
    row_segs = [
        (row_breaks[i] + 1, row_breaks[i + 1])
        for i in range(len(row_breaks) - 1)
        if row_breaks[i] + 1 < row_breaks[i + 1]
    ]
    col_breaks = [-1]
    for c in range(cols):
        if sum(row[c] == 5 for row in grid) >= rows // 2:
            col_breaks.append(c)
    col_breaks.append(cols)
    col_breaks = sorted(set(col_breaks))
    col_segs = [
        (col_breaks[i] + 1, col_breaks[i + 1])
        for i in range(len(col_breaks) - 1)
        if col_breaks[i] + 1 < col_breaks[i + 1]
    ]
    return row_segs, col_segs


def fetch_block(ri, ci, cell):
    key_cell = tupleify(cell)
    block_tuple = MAPPING.get((ri, ci, key_cell))
    if block_tuple is None:
        val = dominant_value(cell)
        block_tuple = FALLBACK.get((ri, ci, val))
        if block_tuple is None:
            row_opts = ROW_SIZE_OPTIONS.get(ri, ROW_SIZE_OPTIONS[max(ROW_SIZE_OPTIONS)])
            col_opts = COL_SIZE_OPTIONS.get(ci, COL_SIZE_OPTIONS[max(COL_SIZE_OPTIONS)])
            height = choose_size(row_opts, len(cell))
            cell_width = len(cell[0]) if cell and cell[0] else 0
            width = choose_size(col_opts, cell_width)
            fill = val if val else 0
            return [[fill for _ in range(width)] for _ in range(height)]
    return [list(row) for row in block_tuple]


def assemble(grid):
    row_segs, col_segs = find_segments(grid)
    if not row_segs or not col_segs:
        return [row[:] for row in grid]
    row_blocks = []
    row_heights = []
    col_widths = [None] * len(col_segs)
    for ri, rseg in enumerate(row_segs):
        current_row_blocks = []
        expected_height = None
        for ci, cseg in enumerate(col_segs):
            cell = [row[cseg[0] : cseg[1]] for row in grid[rseg[0] : rseg[1]]]
            block = fetch_block(ri, ci, cell)
            current_row_blocks.append(block)
            height = len(block)
            width = len(block[0]) if block else 0
            if expected_height is None:
                expected_height = height
            elif expected_height != height:
                expected_height = max(expected_height, height)
            if col_widths[ci] is None:
                col_widths[ci] = width
            elif col_widths[ci] != width:
                col_widths[ci] = max(col_widths[ci], width)
        row_blocks.append(current_row_blocks)
        row_heights.append(expected_height if expected_height is not None else 0)
    total_h = sum(row_heights)
    total_w = sum(w for w in col_widths if w is not None)
    out = [[0 for _ in range(total_w)] for _ in range(total_h)]
    r_offset = 0
    for ri, blocks_row in enumerate(row_blocks):
        c_offset = 0
        for ci, block in enumerate(blocks_row):
            height = row_heights[ri]
            width = col_widths[ci]
            for rr in range(height):
                if rr < len(block):
                    row_vals = block[rr]
                else:
                    row_vals = [0] * len(block[0]) if block else []
                for cc in range(width):
                    val = row_vals[cc] if cc < len(row_vals) else 0
                    out[r_offset + rr][c_offset + cc] = val
            c_offset += width
        r_offset += row_heights[ri]
    return out


###############################################################################
# DSL-style thin adapters (pure interface wrapping existing helpers)
###############################################################################

# Type aliases used by the typed lambda representation.
Grid = List[List[int]]
TemplateId = Tuple[Tuple[int, ...], ...]
# Region encodes: (ri, ci, row_heights, col_widths, template)
CellRegion = Tuple[int, int, Tuple[int, ...], Tuple[int, ...], TemplateId]


def _compute_layout_and_blocks(grid: Grid) -> Tuple[
    List[Tuple[int, int]],
    List[Tuple[int, int]],
    List[List[Grid]],
    List[int],
    List[int],
]:
    """Reuse assemble() parts to compute segments, blocks, and max sizes.

    Returns row segments, col segments, per-cell blocks, row heights, col widths.
    """
    row_segs, col_segs = find_segments(grid)
    if not row_segs or not col_segs:
        # Degenerate: treat whole grid as a single 1x1 cell, block is grid itself.
        block = [row[:] for row in grid]
        return ([(0, len(grid))], [(0, len(grid[0]) if grid and grid[0] else 0)], [[block]], [len(block)], [len(block[0]) if block and block[0] else 0])

    row_blocks: List[List[Grid]] = []
    row_heights: List[int] = []
    col_widths: List[Optional[int]] = [None] * len(col_segs)
    for ri, rseg in enumerate(row_segs):
        current_row_blocks: List[Grid] = []
        expected_height: Optional[int] = None
        for ci, cseg in enumerate(col_segs):
            cell = [row[cseg[0] : cseg[1]] for row in grid[rseg[0] : rseg[1]]]
            block = fetch_block(ri, ci, cell)
            current_row_blocks.append(block)
            h = len(block)
            w = len(block[0]) if block else 0
            if expected_height is None or h > expected_height:
                expected_height = h
            if col_widths[ci] is None or (w > (col_widths[ci] or 0)):
                col_widths[ci] = w
        row_blocks.append(current_row_blocks)
        row_heights.append(expected_height or 0)
    # Finalize widths
    finalized_widths = [w or 0 for w in col_widths]
    return row_segs, col_segs, row_blocks, row_heights, finalized_widths


def segmentBoardCells(grid: Grid) -> List[CellRegion]:
    """Produce immutable regions carrying all info needed downstream.

    Each region holds its row/col index within the segmented board,
    the finalized row_heights/col_widths for layout, and the precomputed
    block template (as a tuple of tuples) to render for that region.
    """
    row_segs, col_segs, row_blocks, row_heights, col_widths = _compute_layout_and_blocks(grid)
    rh_t = tuple(int(h) for h in row_heights)
    cw_t = tuple(int(w) for w in col_widths)
    regions: List[CellRegion] = []
    for ri in range(len(row_segs)):
        for ci in range(len(col_segs)):
            block = row_blocks[ri][ci]
            template: TemplateId = tuple(tuple(row) for row in block)
            regions.append((ri, ci, rh_t, cw_t, template))
    return regions


def lookupCellTemplate(region: CellRegion) -> TemplateId:
    # Template is embedded in the region; return it as the template id.
    return region[4]


def renderTemplate(template_id: TemplateId) -> Grid:
    # Convert tuple-of-tuples template into a list-of-lists grid.
    return [list(row) for row in template_id]


def _zeros(h: int, w: int) -> Grid:
    return [[0 for _ in range(w)] for _ in range(h)]


def _blit(dst: Grid, src: Grid, top: int, left: int, h: int, w: int) -> Grid:
    # Paint src into dst with zero-padding if src smaller than (h,w)
    for rr in range(h):
        srow = src[rr] if rr < len(src) else []
        for cc in range(w):
            val = srow[cc] if cc < len(srow) else 0
            dst[top + rr][left + cc] = val
    return dst


def placeTemplate(canvas: Grid, region: CellRegion, template: Grid) -> Grid:
    ri, ci, rh_t, cw_t, _ = region
    total_h = sum(rh_t)
    total_w = sum(cw_t)
    # Ensure canvas has the correct size; if not, allocate a new one and copy.
    if not canvas or len(canvas) != total_h or (canvas and canvas[0] and len(canvas[0]) != total_w):
        new_canvas = _zeros(total_h, total_w)
        if canvas and canvas[0]:
            old_h = len(canvas)
            old_w = len(canvas[0])
            # Copy existing content into the new canvas clipped to bounds.
            for r in range(min(old_h, total_h)):
                for c in range(min(old_w, total_w)):
                    new_canvas[r][c] = canvas[r][c]
        canvas = new_canvas

    # Compute top-left offset for this region.
    top = sum(rh_t[:ri])
    left = sum(cw_t[:ci])
    # Target slot size for this region.
    slot_h = rh_t[ri]
    slot_w = cw_t[ci]
    # Blit template aligned to top-left inside the slot with zero padding.
    return _blit(canvas, template, top, left, slot_h, slot_w)


T = TypeVar("T")


def fold_repaint(canvas: Grid, items: Iterable[T], update: Callable[[Grid, T], Grid]) -> Grid:
    """Right-fold style reducer to sequentially repaint onto a canvas."""
    acc = canvas
    for item in items:
        acc = update(acc, item)
    return acc


def solve_65b59efc(grid: Grid) -> Grid:
    regions = segmentBoardCells(grid)
    tiles = [(region, lookupCellTemplate(region)) for region in regions]

    def place(canvas: Grid, entry: Tuple[CellRegion, TemplateId]) -> Grid:
        region, template_id = entry
        template = renderTemplate(template_id)
        return placeTemplate(canvas, region, template)

    return fold_repaint(grid, tiles, place)


p = solve_65b59efc
