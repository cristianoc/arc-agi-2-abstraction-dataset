"""Solver for ARC-AGI-2 task 247ef758 (split: evaluation)."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple


# Typed aliases for the DSL subset
Grid = List[List[int]]
Color = int
Row = int
Column = int
Glyph = List[Tuple[int, int, int]]  # list of (r, c, color) cells


def deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def fold_repaint(
    initial: Grid,
    items: List[Tuple[Color, Glyph]],
    update: Callable[[Grid, Tuple[Color, Glyph]], Grid],
) -> Grid:
    canvas = initial
    for item in items:
        canvas = update(canvas, item)
    return canvas


def findAxisColumn(grid: Grid) -> Optional[Column]:
    h = len(grid)
    w = len(grid[0]) if h else 0
    for c in range(w):
        column = [grid[r][c] for r in range(h)]
        if column and column[0] != 0 and all(v == column[0] for v in column):
            return c
    return None


def extractGlyphs(grid: Grid, axis_col: Column) -> Dict[Color, Glyph]:
    acc: Dict[Color, Glyph] = {}
    # collect
    for r, row in enumerate(grid):
        for c in range(axis_col):
            val = row[c]
            if val != 0:
                acc.setdefault(val, []).append((r, c, val))
    # reorder by min-row descending to match solver semantics
    order = sorted(acc.keys(), key=lambda col: min(rcv[0] for rcv in acc[col]), reverse=True)
    return {col: acc[col] for col in order}


def extractColumnMarkers(grid: Grid, axis_col: Column) -> Dict[Color, List[Column]]:
    top = grid[0] if grid else []
    mapping: Dict[Color, List[Column]] = {}
    for c in range(axis_col + 1, len(top)):
        v = top[c]
        if v != 0:
            mapping.setdefault(v, []).append(c)
    for k in list(mapping.keys()):
        mapping[k] = sorted(mapping[k])
    return mapping


def extractRowMarkers(grid: Grid) -> Dict[Color, List[Row]]:
    h = len(grid)
    w = len(grid[0]) if h else 0
    mapping: Dict[Color, List[Row]] = {}
    if w == 0:
        return mapping
    last = w - 1
    for r in range(h):
        v = grid[r][last]
        if v != 0:
            mapping.setdefault(v, []).append(r)
    for k in list(mapping.keys()):
        mapping[k] = sorted(mapping[k])
    return mapping


def glyphMinRow(glyph: Glyph) -> int:
    return min(r for r, _, _ in glyph) if glyph else 0


def placeGlyphs(canvas: Grid, glyph: Glyph, rows: List[Row], cols: List[Column]) -> Grid:
    if not glyph:
        return canvas
    h = len(canvas)
    w = len(canvas[0]) if h else 0
    # colour is stored within the glyph cells
    r0, c0, color = glyph[0]
    g = deep_copy(canvas)
    # clear source glyph cells
    for r, c, _ in glyph:
        if 0 <= r < h and 0 <= c < w:
            g[r][c] = 0
    # compute centre and offsets
    rows_list = [r for r, _, _ in glyph]
    cols_list = [c for _, c, _ in glyph]
    min_r, max_r = min(rows_list), max(rows_list)
    min_c, max_c = min(cols_list), max(cols_list)
    cr = (min_r + max_r) // 2
    cc = (min_c + max_c) // 2
    offsets = [(r - cr, c - cc) for r, c, _ in glyph]
    # stamp at every row/column combination
    for tr in rows:
        for tc in cols:
            for dr, dc in offsets:
                rr = tr + dr
                cc2 = tc + dc
                if 0 <= rr < h and 0 <= cc2 < w:
                    g[rr][cc2] = color
    return g


def solve_247ef758(grid: Grid) -> Grid:
    axis_col = findAxisColumn(grid)
    if axis_col is None:
        return grid

    glyphs = extractGlyphs(grid, axis_col)
    col_markers = extractColumnMarkers(grid, axis_col)
    row_markers = extractRowMarkers(grid)
    glyph_entries = list(glyphs.items())

    def place(canvas: Grid, entry: Tuple[Color, Glyph]) -> Grid:
        color, glyph = entry
        if color not in col_markers or color not in row_markers:
            return canvas
        return placeGlyphs(canvas, glyph, row_markers[color], col_markers[color])

    return fold_repaint(grid, glyph_entries, place)


p = solve_247ef758
