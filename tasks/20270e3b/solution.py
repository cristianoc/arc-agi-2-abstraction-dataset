"""Solution for ARC-AGI-2 task 20270e3b."""

from __future__ import annotations

from typing import List, Optional


BG = 1
SPECIAL = 7
FILL = 4

Grid = List[List[int]]


def _copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _vertical_fold(grid: Grid) -> Optional[Grid]:
    """Overlay the right block onto the left block across a background column."""

    h = len(grid)
    w = len(grid[0])
    sep_cols = [c for c in range(w) if all(grid[r][c] == BG for r in range(h))]
    if not sep_cols:
        return None

    left_edge = sep_cols[0]
    right_edge = sep_cols[-1]
    left = [row[:left_edge] for row in grid]
    right = [row[right_edge + 1 :] for row in grid]
    if not left or not left[0]:
        return None

    out = _copy(left)
    for r in range(h):
        for c in range(len(out[0])):
            if out[r][c] == SPECIAL:
                out[r][c] = FILL

    if not right or not right[0]:
        return out

    left_cols_with_special = [
        c for c in range(len(out[0])) if any(grid[r][c] == SPECIAL for r in range(h))
    ]
    if left_cols_with_special:
        start = min(left_cols_with_special)
    else:
        start = max(0, len(out[0]) - len(right[0]))

    left_rows_with_special = [
        r for r in range(h) if any(grid[r][c] == SPECIAL for c in range(left_edge))
    ]
    right_rows_with_special = [
        r for r in range(h) if any(grid[r][c] == SPECIAL for c in range(right_edge + 1, w))
    ]
    left_anchor = min(left_rows_with_special) if left_rows_with_special else 0
    right_anchor = min(right_rows_with_special) if right_rows_with_special else 0
    row_offset = left_anchor - right_anchor - 1

    for r in range(h):
        rr = r + row_offset
        if rr < 0 or rr >= h:
            continue
        for k in range(len(right[0])):
            cc = start + k
            if cc >= len(out[0]):
                break
            if right[r][k] == FILL:
                out[rr][cc] = FILL

    return out


def _horizontal_fold(grid: Grid) -> Optional[Grid]:
    """Remove the special band and glue the remaining parts with an offset."""

    h = len(grid)
    w = len(grid[0])
    rows_with_special = [r for r, row in enumerate(grid) if any(v == SPECIAL for v in row)]
    if not rows_with_special:
        return None

    top = min(rows_with_special)
    bottom = max(rows_with_special)
    span = bottom - top + 1

    cols_with_special = [
        c for c in range(w) if any(grid[r][c] == SPECIAL for r in range(h))
    ]
    if cols_with_special:
        c0, c1 = min(cols_with_special), max(cols_with_special)
        extend = (c1 - c0) if c1 < w - 1 else 0
    else:
        extend = 0

    new_w = w + extend
    out_height = h - span
    if out_height <= 0:
        return None

    out = [[BG] * new_w for _ in range(out_height)]

    def paste_row(src_row: List[int], tgt_r: int, shift: int = 0, fill_only: bool = False) -> None:
        for c, val in enumerate(src_row):
            if fill_only and val != FILL:
                continue
            cc = c + shift
            if 0 <= cc < new_w:
                out[tgt_r][cc] = FILL if val == SPECIAL else val

    for r in range(top):
        paste_row(grid[r], r)

    for r in range(bottom + 1, h):
        paste_row(grid[r], r - span, extend)

    for r in range(top, bottom + 1):
        tgt = r - span
        if 0 <= tgt < out_height:
            paste_row(grid[r], tgt, extend, fill_only=True)

    return out


def solve_20270e3b(grid: Grid) -> Grid:
    attempt = _vertical_fold(grid)
    if attempt is not None:
        return attempt

    attempt = _horizontal_fold(grid)
    if attempt is not None:
        return attempt

    # Fallback: recolour specials when no folding pattern is detected.
    return [[FILL if v == SPECIAL else v for v in row] for row in grid]


p = solve_20270e3b
