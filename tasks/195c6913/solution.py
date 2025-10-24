"""Solver for ARC-AGI-2 task 195c6913 (split: evaluation)."""

from collections import deque
from typing import Any, Callable, Dict, Iterable, List, Sequence, Tuple

Grid = List[List[int]]
Anchor = Any  # anchor payload assembled by locateAnchors


def _iter_components(grid: Sequence[Sequence[int]]) -> Iterable[Tuple[int, List[Tuple[int, int]]]]:
    """Yield 4-connected components as (color, cells)."""

    height = len(grid)
    width = len(grid[0]) if height else 0
    seen = [[False] * width for _ in range(height)]

    for r in range(height):
        for c in range(width):
            if seen[r][c]:
                continue
            color = grid[r][c]
            queue = deque([(r, c)])
            seen[r][c] = True
            cells = [(r, c)]

            while queue:
                cr, cc = queue.popleft()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not seen[nr][nc] and grid[nr][nc] == color:
                        seen[nr][nc] = True
                        queue.append((nr, nc))
                        cells.append((nr, nc))

            yield color, cells


# === DSL-style helpers ===

def iterComponents(grid: Grid) -> List[Tuple[int, List[Tuple[int, int]]]]:
    return list(_iter_components(grid))


def extractPalette(components: List[Tuple[int, List[Tuple[int, int]]]]) -> List[int]:
    palette_infos: List[Tuple[int, int, List[Tuple[int, int]]]] = []
    for color, cells in components:
        if len(cells) != 4:
            continue
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        if max(rows) - min(rows) != 1 or max(cols) - min(cols) != 1:
            continue
        if min(rows) > 2:
            continue
        palette_infos.append((min(cols), color, cells))
    palette_infos.sort(key=lambda item: item[0])
    return [color for _, color, _ in palette_infos]


def _color_totals(grid: Grid) -> Dict[int, int]:
    totals: Dict[int, int] = {}
    for row in grid:
        for v in row:
            totals[v] = totals.get(v, 0) + 1
    return totals


def stripPalette(grid: Grid, pattern: List[int]) -> Grid:
    if not grid or not grid[0]:
        return [row[:] for row in grid]

    height = len(grid)
    width = len(grid[0])
    background = grid[0][0]

    components = list(_iter_components(grid))
    totals = _color_totals(grid)

    # identify palette cells (2x2 legend at the top rows)
    palette_infos: List[Tuple[int, int, List[Tuple[int, int]]]] = []
    for color, cells in components:
        if len(cells) != 4:
            continue
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        if max(rows) - min(rows) != 1 or max(cols) - min(cols) != 1:
            continue
        if min(rows) > 2:
            continue
        palette_infos.append((min(cols), color, cells))
    palette_infos.sort(key=lambda item: item[0])
    pattern_cells = [cells for _, _, cells in palette_infos]

    # choose fill and cap colours from remaining palette
    candidates = [
        (totals[c], c)
        for c in totals
        if c != background and c not in set(pattern)
    ]
    if not candidates:
        return [row[:] for row in grid]
    fill_color = max(candidates)[1]
    remaining = [item for item in candidates if item[1] != fill_color]
    cap_color = min(remaining)[1] if remaining else None

    cap_component: List[Tuple[int, int]] = []
    if cap_color is not None:
        cap_comps = [cells for color, cells in components if color == cap_color]
        if cap_comps:
            cap_component = min(cap_comps, key=len)

    out = [row[:] for row in grid]
    for cells in pattern_cells:
        for r, c in cells:
            out[r][c] = background
    for r, c in cap_component:
        out[r][c] = background
    return out


def locateAnchors(grid: Grid, pattern: List[int]) -> List[Tuple[int, int, int, str, int, int, Grid]]:
    # returns anchors as (row, boundary, start_idx, role, fill_color, cap_color, base_grid)
    if not grid or not grid[0]:
        return []
    height = len(grid)
    width = len(grid[0])
    background = grid[0][0]

    totals = _color_totals(grid)
    candidates = [
        (totals[c], c)
        for c in totals
        if c != background and c not in set(pattern)
    ]
    if not candidates:
        return []
    fill_color = max(candidates)[1]
    remaining = [item for item in candidates if item[1] != fill_color]
    cap_color = min(remaining)[1] if remaining else None

    anchors_basic: List[Tuple[int, int, int]] = []
    for r, row in enumerate(grid):
        first = row[0]
        if first not in pattern:
            continue
        start_idx = pattern.index(first)
        c = 1
        while c < width and row[c] == fill_color:
            c += 1
        if c <= 1:
            continue
        anchors_basic.append((r, c, start_idx))

    if not anchors_basic:
        return []

    anchors_basic.sort()
    if len(anchors_basic) == 1:
        r, b, s = anchors_basic[0]
        role = "both"
        return [(r, b, s, role, fill_color, cap_color if cap_color is not None else -1, grid)]

    enriched: List[Tuple[int, int, int, str, int, int, Grid]] = []
    for i, (r, b, s) in enumerate(anchors_basic):
        if i == 0:
            role = "top"
        elif i == len(anchors_basic) - 1:
            role = "bottom"
        else:
            role = "middle"
        enriched.append((r, b, s, role, fill_color, cap_color if cap_color is not None else -1, grid))
    return enriched


def fold_repaint(initial: Grid, items: List[Anchor], update: Callable[[Grid, Anchor], Grid]) -> Grid:
    canvas = [row[:] for row in initial]
    for item in items:
        canvas = update(canvas, item)
    return canvas


def propagatePattern(canvas: Grid, pattern: List[int], anchor: Tuple[int, int, int, str, int, int, Grid]) -> Grid:
    # anchor = (row, boundary, start_idx, role, fill_color, cap_color, base_grid)
    r_anchor, boundary, start_idx, role, fill_color, cap_color, base = anchor
    height = len(canvas)
    width = len(canvas[0]) if height else 0
    pattern_len = len(pattern)

    def paint_anchor_row(g: Grid, r: int, boundary: int, start_idx: int) -> Grid:
        out = [row[:] for row in g]
        idx = start_idx
        for c in range(boundary):
            out[r][c] = pattern[idx]
            idx = (idx + 1) % pattern_len
        if cap_color != -1 and boundary < width:
            out[r][boundary] = cap_color
        return out

    def propagate_dir(g: Grid, direction: int) -> Grid:
        if not (0 <= r_anchor < height):
            return g
        out = [row[:] for row in g]
        col_last = boundary - 1
        if col_last < 0 or col_last >= width:
            return out
        idx_anchor = (start_idx + col_last) % pattern_len

        rows_col: List[Tuple[int, int]] = []
        r = r_anchor + direction
        current_idx = (idx_anchor - direction) % pattern_len
        while 0 <= r < height and out[r][col_last] == fill_color:
            out[r][col_last] = pattern[current_idx]
            rows_col.append((r, current_idx))
            r += direction
            current_idx = (current_idx - direction) % pattern_len
        if rows_col and cap_color != -1 and 0 <= r < height:
            out[r][col_last] = cap_color

        if not rows_col:
            return out

        boundary_row, idx_boundary = rows_col[-1]

        run_end = col_last
        while run_end < width and base[boundary_row][run_end] == fill_color:
            run_end += 1
        if run_end == col_last:
            return out

        idx = idx_boundary
        for c in range(col_last, run_end):
            out[boundary_row][c] = pattern[idx]
            idx = (idx + 1) % pattern_len
        if cap_color != -1 and run_end < width:
            out[boundary_row][run_end] = cap_color

        col_right = run_end - 1
        idx_right = (idx_boundary + (run_end - col_last - 1)) % pattern_len
        rows_edge: List[Tuple[int, int]] = []
        r = boundary_row + direction
        current_idx = (idx_right - direction) % pattern_len
        while 0 <= r < height and base[r][col_right] == fill_color:
            out[r][col_right] = pattern[current_idx]
            rows_edge.append((r, current_idx))
            r += direction
            current_idx = (current_idx - direction) % pattern_len
        if rows_edge and cap_color != -1 and 0 <= r < height:
            out[r][col_right] = cap_color

        if not rows_edge:
            return out

        row_idx, idx_value = rows_edge[-1]
        neighbor_row = row_idx + direction
        if not (0 <= neighbor_row < height) or base[neighbor_row][col_right] == fill_color:
            return out

        c = col_right + 1
        next_idx = (idx_value + 1) % pattern_len
        while c < width and base[row_idx][c] == fill_color:
            out[row_idx][c] = pattern[next_idx]
            next_idx = (next_idx + 1) % pattern_len
            c += 1
        if cap_color != -1 and c < width:
            out[row_idx][c] = cap_color
        return out

    # fill the anchor row first
    filled = paint_anchor_row(canvas, r_anchor, boundary, start_idx)
    if role == "both":
        return propagate_dir(propagate_dir(filled, direction=-1), direction=1)
    if role == "top":
        return propagate_dir(filled, direction=-1)
    if role == "bottom":
        return propagate_dir(filled, direction=-1)
    # default for any middle anchors: upward only as conservative choice
    return propagate_dir(filled, direction=-1)


def solve_195c6913(grid: Grid) -> Grid:
    components = iterComponents(grid)
    pattern = extractPalette(components)
    result = stripPalette(grid, pattern)
    anchors = locateAnchors(grid, pattern)

    def propagate(canvas: Grid, anchor: Anchor) -> Grid:
        return propagatePattern(canvas, pattern, anchor)

    return fold_repaint(result, anchors, propagate)


p = solve_195c6913
