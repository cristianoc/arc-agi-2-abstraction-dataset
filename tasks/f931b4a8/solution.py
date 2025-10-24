"""Solver for ARC-AGI-2 task f931b4a8 (evaluation split)."""

from collections import defaultdict
from typing import List, Tuple


# Shared type aliases
Grid = List[List[int]]
RowPlan = Tuple[List[int], List[List[int]]]


def _clone(grid):
    return [row[:] for row in grid]


def _transpose(grid):
    return [list(col) for col in zip(*grid)]


def _nonzero_positions_col_major(mask):
    h = len(mask)
    w = len(mask[0]) if h else 0
    coords = []
    for c in range(w):
        for r in range(h):
            if mask[r][c] != 0:
                coords.append((r, c))
    return coords


def _nonzero_positions_row_major(mask):
    coords = []
    for r, row in enumerate(mask):
        for c, val in enumerate(row):
            if val != 0:
                coords.append((r, c))
    return coords


def _compute_tile(grid):
    h = len(grid)
    w = len(grid[0]) if h else 0
    hh = h // 2
    hw = w // 2
    bl = [row[:hw] for row in grid[hh:]]
    br = [row[hw:] for row in grid[hh:]]
    tile = []
    for r in range(hh):
        row = []
        for c in range(hw):
            val = br[r][c]
            if val == 0:
                val = bl[r][c]
            row.append(val)
        tile.append(row)
    return tile, bl, br


def _zero_signature(br_row):
    return tuple(idx for idx, val in enumerate(br_row) if val == 0)


def _build_variant_orders(tile, br):
    variants = defaultdict(dict)
    for idx, row in enumerate(tile):
        zero_sig = _zero_signature(br[idx])
        fill = tuple(row[c] for c in zero_sig)
        base = row[0] if row else 0
        key = tuple(row)
        score = (fill, -base, idx)
        stored = variants[zero_sig].get(key)
        if stored is None or score < stored[0]:
            variants[zero_sig][key] = (score, idx)
    orders = {}
    for zero_sig, mapping in variants.items():
        ordered = sorted(mapping.values(), key=lambda item: item[0])
        orders[zero_sig] = [idx for _, idx in ordered]
    return orders


def _collect_group_meta(br):
    meta = defaultdict(list)
    for r, row in enumerate(br):
        meta[_zero_signature(row)].append(r)
    return meta


def _ensure_unique_patterns(rows):
    patterns = []
    mapping = {}
    for row in rows:
        t = tuple(row)
        if t not in mapping:
            mapping[t] = len(patterns)
            patterns.append(row)
    return patterns, mapping


def _borrow_pool(orders, exclude):
    pool = []
    for zero_sig, order in orders.items():
        if zero_sig == exclude:
            continue
        if order:
            pool.append(order[0])
    return pool


def _compute_row_ids(grid):
    tile, bl, br = _compute_tile(grid)
    hh = len(tile)
    hw = len(tile[0]) if tile else 0
    tl = [row[:hw] for row in grid[:hh]]
    row_patterns, row_to_id = _ensure_unique_patterns(tile)
    variant_orders = _build_variant_orders(tile, br)
    zero_groups = _collect_group_meta(br)
    coords = _nonzero_positions_col_major(tl)
    if not coords:
        return [], row_patterns, row_to_id

    full_sig = tuple(range(hw))
    borrow_default = _borrow_pool(variant_orders, full_sig)
    borrow_all = _borrow_pool(variant_orders, None)
    min_index_per_group = {sig: min(rows) for sig, rows in zero_groups.items()}
    row_ids = []
    for r, c in coords:
        zero_sig = _zero_signature(br[r])
        order = variant_orders.get(zero_sig, [])
        variant_idx = 0
        if not order:
            variant_row = r
        elif zero_sig == full_sig:
            base_variant = order[0]
            if c % 2 == 0:
                variant_row = base_variant
            else:
                borrows = borrow_default or [base_variant]
                offset = (r - min_index_per_group.get(zero_sig, r)) % len(borrows)
                variant_row = borrows[offset]
        else:
            if len(order) == 1 and len(borrow_all) > 1 and full_sig in variant_orders:
                alternate = next((val for val in borrow_all if val != order[0]), order[0])
                variant_row = order[0] if len(row_ids) % 2 == 0 else alternate
            else:
                variant_idx = c % len(order)
                variant_row = order[variant_idx]
        row_ids.append(row_to_id[tuple(tile[variant_row])])
    return row_ids, row_patterns, row_to_id


def _compute_col_ids(grid, row_patterns, row_to_id):
    tile, _, _ = _compute_tile(grid)
    hh = len(tile)
    hw = len(tile[0]) if tile else 0
    tr = [row[hw:] for row in grid[:hh]]
    coords = _nonzero_positions_row_major(tr)
    if not coords or hw == 0:
        return [], []

    col_ids = [idx % hw for idx, _ in enumerate(coords)]
    return col_ids, _transpose(tile)


def solve_f931b4a8(grid: Grid) -> Grid:
    quadrants = extractTileQuadrants(grid)
    row_plan = deriveRowOrder(quadrants)
    col_ids = deriveColumnOrder(quadrants, row_plan)
    return renderByIds(row_plan, col_ids)


p = solve_f931b4a8


# === DSL-style helper surface ===


def extractTileQuadrants(grid: Grid) -> Tuple[Grid, Grid, Grid, Grid, Grid]:
    """Return (grid, tile, tl, tr, br) for downstream pure steps.

    - tile: base tile computed by preferring BR over BL and falling back
    - tl: top-left quadrant region used to derive row anchors
    - tr: top-right quadrant region used to derive column anchors
    - br: bottom-right quadrant region used for zero-signature analysis
    """
    tile, bl, br = _compute_tile(grid)
    hh = len(tile)
    hw = len(tile[0]) if tile else 0
    tl = [row[:hw] for row in grid[:hh]]
    tr = [row[hw:] for row in grid[:hh]]
    return (grid, tile, tl, tr, br)


def deriveRowOrder(quadrants: Tuple[Grid, Grid, Grid, Grid, Grid]) -> RowPlan:
    grid, _tile, _tl, _tr, _br = quadrants
    row_ids, row_patterns, _row_to_id = _compute_row_ids(grid)
    return (row_ids, row_patterns)


def deriveColumnOrder(
    quadrants: Tuple[Grid, Grid, Grid, Grid, Grid], row_plan: RowPlan
) -> List[int]:
    _grid, tile, _tl, tr, _br = quadrants
    hw = len(tile[0]) if tile else 0
    coords = _nonzero_positions_row_major(tr)
    if not coords or hw == 0:
        return []
    return [idx % hw for idx, _ in enumerate(coords)]


def renderByIds(row_plan: RowPlan, col_ids: List[int]) -> Grid:
    row_ids, row_patterns = row_plan
    if not row_ids or not col_ids:
        return []
    return [[row_patterns[row_id][c] for c in col_ids] for row_id in row_ids]
