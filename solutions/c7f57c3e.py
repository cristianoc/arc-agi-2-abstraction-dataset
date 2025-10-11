"""Solver for ARC-AGI-2 task c7f57c3e (evaluation split)."""

from collections import Counter, deque


def _copy_grid(grid):
    return [row[:] for row in grid]


def _most_common_color(grid):
    counts = Counter()
    for row in grid:
        counts.update(row)
    return counts.most_common(1)[0][0]


def _palette_without(grid, background):
    colors = {val for row in grid for val in row if val != background}
    return sorted(colors)


def _has_adjacent_colors(grid, color_a, color_b):
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


def _components(grid, target_color):
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


def _apply_variant_a(grid, background, c1, c2, mid, high):
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


def _apply_variant_b(grid, background, c2, mid, high):
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


def solve_c7f57c3e(grid):
    background = _most_common_color(grid)
    palette = _palette_without(grid, background)
    if not palette:
        return _copy_grid(grid)

    if len(palette) == 1:
        return _copy_grid(grid)

    high = palette[-1]
    candidates = [c for c in palette if c < high]
    if not candidates:
        return _copy_grid(grid)
    mid = max(candidates)

    pivot = palette[1] if len(palette) > 1 else palette[0]
    c1 = palette[0]

    if mid == pivot:
        return _copy_grid(grid)

    if _has_adjacent_colors(grid, mid, pivot):
        return _apply_variant_a(grid, background, c1, pivot, mid, high)

    return _apply_variant_b(grid, background, pivot, mid, high)


p = solve_c7f57c3e
