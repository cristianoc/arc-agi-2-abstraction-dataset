"""Solver for ARC-AGI-2 task c7f57c3e (evaluation split)."""

from collections import Counter, deque
from typing import List, Tuple

Grid = List[List[int]]
Color = int


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _most_common_color(grid: Grid) -> Color:
    counts: Counter[int] = Counter()
    for row in grid:
        counts.update(row)
    return counts.most_common(1)[0][0]


def _palette_without(grid: Grid, background: Color) -> list[int]:
    colors = {val for row in grid for val in row if val != background}
    return sorted(colors)


def _has_adjacent_colors(grid: Grid, color_a: Color, color_b: Color) -> bool:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != color_a:
                continue
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == color_b:
                    return True
    return False


def _components(grid: Grid, target_color: Color):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    visited = [[False] * cols for _ in range(rows)]
    comps = []
    for r in range(rows):
        for c in range(cols):
            if visited[r][c] or grid[r][c] != target_color:
                continue
            q = deque([(r, c)])
            visited[r][c] = True
            cells = []
            while q:
                x, y = q.popleft()
                cells.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < rows and 0 <= ny < cols and not visited[nx][ny] and grid[nx][ny] == target_color:
                        visited[nx][ny] = True
                        q.append((nx, ny))
            comps.append(cells)
    return comps


def _apply_variant_a(grid: Grid, background: Color, c1: Color, c2: Color, mid: Color, high: Color) -> Grid:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    out = _copy_grid(grid)
    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            if val == mid:
                out[r][c] = high
            elif val == high:
                up = grid[r - 1][c] if r > 0 else None
                out[r][c] = c2 if up == c2 else mid
            elif val == c2:
                neighbors = [
                    grid[nr][nc]
                    for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                    if 0 <= nr < rows and 0 <= nc < cols
                ]
                out[r][c] = c2 if c1 in neighbors else high
            else:
                out[r][c] = val
    return out


def _apply_variant_b(grid: Grid, background: Color, c2: Color, mid: Color, high: Color) -> Grid:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    out = _copy_grid(grid)

    pivot_comps = _components(grid, c2)
    if not pivot_comps:
        return out

    pivot_info = []
    for cells in pivot_comps:
        row_vals = [r for r, _ in cells]
        col_vals = {c for _, c in cells}
        pivot_info.append(
            {
                "rows_min": min(row_vals),
                "rows_max": max(row_vals),
                "cols": col_vals,
                "axis_sum": min(row_vals) + max(row_vals),
            }
        )

    mid_comps = _components(grid, mid)
    high_comps = _components(grid, high)

    def find_pivot_for_mid(r, c):
        candidates = [p for p in pivot_info if c in p["cols"] and p["rows_max"] < r]
        if not candidates:
            return None
        return max(candidates, key=lambda p: p["rows_max"])

    def find_pivot_for_high(r, c):
        candidates = [p for p in pivot_info if c in p["cols"] and p["rows_min"] > r]
        if not candidates:
            return None
        return min(candidates, key=lambda p: p["rows_min"])

    for cells in mid_comps:
        for r, c in cells:
            pivot = find_pivot_for_mid(r, c)
            out[r][c] = background
            if pivot is None:
                continue
            new_r = pivot["axis_sum"] - r
            if 0 <= new_r < rows:
                out[new_r][c] = high

    for cells in high_comps:
        for r, c in cells:
            pivot = find_pivot_for_high(r, c)
            out[r][c] = background
            if pivot is None:
                continue
            new_r = pivot["axis_sum"] - r
            if 0 <= new_r < rows:
                out[new_r][c] = mid

    return out


# --- DSL-style wrappers ----------------------------------------------------

def analysePalette(grid: Grid) -> Tuple[Color, Color, Color, Color]:
    background = _most_common_color(grid)
    pal = _palette_without(grid, background)
    if not pal:
        return background, background, background, background
    high = pal[-1]
    candidates = [c for c in pal if c < high]
    mid = max(candidates) if candidates else high
    pivot = pal[1] if len(pal) > 1 else pal[0]
    return background, pivot, mid, high


def checkAdjacency(grid: Grid, mid: Color, pivot: Color) -> bool:
    return _has_adjacent_colors(grid, mid, pivot)


def applyVariantA(grid: Grid, palette: Tuple[Color, Color, Color, Color]) -> Grid:
    background, pivot, mid, high = palette
    pal = _palette_without(grid, background)
    if len(pal) < 3 or mid == pivot:
        return _copy_grid(grid)
    c1 = pal[0]
    return _apply_variant_a(grid, background, c1, pivot, mid, high)


def applyVariantB(grid: Grid, palette: Tuple[Color, Color, Color, Color]) -> Grid:
    background, pivot, mid, high = palette
    pal = _palette_without(grid, background)
    if len(pal) < 3 or mid == pivot:
        return _copy_grid(grid)
    return _apply_variant_b(grid, background, pivot, mid, high)


def solve_c7f57c3e(grid: Grid) -> Grid:
    background, pivot, mid, highlight = analysePalette(grid)
    palette = (background, pivot, mid, highlight)
    if checkAdjacency(grid, mid, pivot):
        return applyVariantA(grid, palette)
    return applyVariantB(grid, palette)


p = solve_c7f57c3e
