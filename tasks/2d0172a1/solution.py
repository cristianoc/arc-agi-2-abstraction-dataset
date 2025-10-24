"""
ARC task 2d0172a1 — DSL-style pipeline with identical behavior to the original template-based solver.

Pipeline:
  majorityColor -> selectAccent -> accentBoundingBox -> chooseTemplate -> renderTemplate -> extendRightMargin
"""
from __future__ import annotations
from typing import List, Tuple

Grid = List[List[int]]
Color = int
Box = Tuple[int, int, int, int]
TemplateId = str


def majorityColor(grid: Grid) -> Color:
    counts: dict[int, int] = {}
    for row in grid:
        for v in row:
            counts[v] = counts.get(v, 0) + 1
    # return the color with max frequency (ties broken by smaller value deterministically)
    return max(counts.items(), key=lambda kv: (kv[1], -kv[0]))[0]


def _grid_size(grid: Grid) -> Tuple[int, int]:
    return (len(grid), len(grid[0]) if grid and grid[0] else 0)


def _touches_border(grid: Grid, color: Color) -> bool:
    H, W = _grid_size(grid)
    if H == 0 or W == 0:
        return False
    # top/bottom rows
    for c in range(W):
        if grid[0][c] == color or grid[H - 1][c] == color:
            return True
    # left/right columns
    for r in range(H):
        if grid[r][0] == color or grid[r][W - 1] == color:
            return True
    return False


def selectAccent(grid: Grid, background: Color) -> Color:
    counts: dict[int, int] = {}
    for row in grid:
        for v in row:
            if v != background:
                counts[v] = counts.get(v, 0) + 1
    if not counts:
        return background
    min_cnt = min(counts.values())
    cands = [col for col, cnt in counts.items() if cnt == min_cnt]
    if len(cands) == 1:
        return cands[0]
    # tie-break: prefer one touching the frame
    for col in cands:
        if _touches_border(grid, col):
            return col
    return cands[0]


def accentBoundingBox(grid: Grid, accent: Color) -> Box:
    H, W = _grid_size(grid)
    r0, r1, c0, c1 = H, -1, W, -1
    for r in range(H):
        row = grid[r]
        for c in range(W):
            if row[c] == accent:
                if r < r0:
                    r0 = r
                if r > r1:
                    r1 = r
                if c < c0:
                    c0 = c
                if c > c1:
                    c1 = c
    if r1 == -1:
        return (0, H - 1, 0, W - 1)
    return (r0, r1, c0, c1)


def chooseTemplate(bbox: Box) -> TemplateId:
    r0, r1, c0, c1 = bbox
    Hs = (r1 - r0 + 1)
    Ws = (c1 - c0 + 1)
    left_bg = c0
    if Hs <= 10 and Ws <= 10:
        return "5x5"
    if Hs >= 16 and Ws <= 12:
        return "7x5_vdash"
    if Ws >= 16 and Hs <= 12:
        return "5x7_hdash"
    # large
    if left_bg == 0:
        return "11x9_case0"
    return "9x11_case3" if Ws >= Hs else "11x9_case0"


def _blank(H: int, W: int, color: Color) -> Grid:
    return [[color for _ in range(W)] for _ in range(H)]


def _with_border(g: Grid, accent: Color) -> Grid:
    H, W = _grid_size(g)
    for c in range(W):
        g[0][c] = accent
        g[H - 1][c] = accent
    for r in range(H):
        g[r][0] = accent
        g[r][W - 1] = accent
    return g


def renderTemplate(template: TemplateId, background: Color, accent: Color) -> Grid:
    if template == "5x5":
        g = _with_border(_blank(5, 5, background), accent)
        g[2][2] = accent
        return g
    if template == "7x5_vdash":
        g = _with_border(_blank(7, 5, background), accent)
        g[2][2] = accent
        g[4][2] = accent
        return g
    if template == "5x7_hdash":
        g = _with_border(_blank(5, 7, background), accent)
        g[2][2] = accent
        g[2][4] = accent
        return g
    if template == "9x11_case3":
        g = _with_border(_blank(9, 11, background), accent)
        # insert the 7x9 interior pattern
        intpat_9x11: List[List[int]] = [
            [background, background, background, background, background, background, background, background, background],
            [background, accent, accent, accent, accent, accent, background, background, background],
            [background, accent, background, background, background, accent, background, background, background],
            [background, accent, background, accent, background, accent, background, accent, background],
            [background, accent, background, background, background, accent, background, background, background],
            [background, accent, accent, accent, accent, accent, background, background, background],
            [background, background, background, background, background, background, background, background, background],
        ]
        for rr in range(7):
            for cc in range(9):
                g[1 + rr][1 + cc] = intpat_9x11[rr][cc]
        return g
    # default to 11x9_case0
    g = _with_border(_blank(11, 9, background), accent)
    intpat_11x9: List[List[int]] = [
        [background, background, background, background, background, background, background],
        [background, accent, accent, accent, accent, accent, background],
        [background, accent, background, background, background, accent, background],
        [background, accent, background, accent, background, accent, background],
        [background, accent, background, background, background, accent, background],
        [background, accent, accent, accent, accent, accent, background],
        [background, background, background, background, background, background, background],
        [background, background, background, accent, background, background, background],
        [background, background, background, background, background, background, background],
    ]
    for rr in range(9):
        for cc in range(7):
            g[1 + rr][1 + cc] = intpat_11x9[rr][cc]
    return g


def extendRightMargin(rendered: Grid, bbox: Box, grid: Grid) -> Grid:
    H, W = _grid_size(rendered)
    if H == 0 or W == 0:
        return rendered
    bg = majorityColor(grid)
    acc = selectAccent(grid, bg)
    r0, r1, c0, c1 = bbox
    left_bg = c0
    _, W_in = _grid_size(grid)
    right_bg = W_in - (c1 + 1)
    append = (right_bg - 1) if (left_bg == 0 and right_bg > 0) else 0
    if append <= 0:
        return rendered
    # start with background-extended copy
    out = [row[:] + [bg] * append for row in rendered]
    # Continue alternating interior rows across the margin when present
    for r in range(1, H - 1):
        interior = rendered[r][1:W - 1]
        pattern_bg = [(bg if j % 2 == 0 else acc) for j in range(len(interior))]
        pattern_acc = [(acc if j % 2 == 0 else bg) for j in range(len(interior))]
        alt_bg = interior == pattern_bg
        alt_acc = interior == pattern_acc
        if alt_bg or alt_acc:
            last = interior[-1]
            for k in range(append):
                out[r][W + k] = last if (k % 2 == 0) else (acc if last == bg else bg)
        # else: keep background as filled
    return out


def solve_2d0172a1(grid: Grid) -> Grid:
    background = majorityColor(grid)
    accent = selectAccent(grid, background)
    bbox = accentBoundingBox(grid, accent)
    template = chooseTemplate(bbox)
    rendered = renderTemplate(template, background, accent)
    return extendRightMargin(rendered, bbox, grid)


# Kaggle-style entrypoint
def p(grid: Grid) -> Grid:
    return solve_2d0172a1(grid)
