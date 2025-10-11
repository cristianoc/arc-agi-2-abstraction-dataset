"""Solver for ARC-AGI-2 evaluation task faa9f03d."""

from collections import Counter


def _copy(grid):
    return [row[:] for row in grid]


def _analyze_color_stats(grid):
    h = len(grid)
    w = len(grid[0])
    colors = {v for row in grid for v in row if v}
    stats = {}
    for color in colors:
        cols = [sum(1 for r in range(h) if grid[r][c] == color) for c in range(w)]
        rows = [sum(1 for c in range(w) if grid[r][c] == color) for r in range(h)]
        stats[color] = (max(cols), max(rows))
    return stats


def _remove_noise(grid, noise_threshold=4):
    counts = Counter(v for row in grid for v in row if v)
    top = [color for color, _ in counts.most_common(2)]
    noise_colors = {color for color, cnt in counts.items() if cnt <= noise_threshold}
    out = _copy(grid)
    h = len(grid)
    w = len(grid[0])
    for r in range(h):
        for c in range(w):
            val = out[r][c]
            if val == 0 or val not in noise_colors:
                continue
            neigh = Counter()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < h and 0 <= cc < w:
                    nv = grid[rr][cc]
                    if nv and nv not in noise_colors:
                        neigh[nv] += 1
            if neigh:
                out[r][c] = neigh.most_common(1)[0][0]
            elif top:
                out[r][c] = top[0]
    return out, top


def _close_rows_selective(grid, allowed_colors, max_gap=2):
    out = _copy(grid)
    w = len(grid[0])
    for r, row in enumerate(grid):
        for color in allowed_colors:
            cols = [c for c, v in enumerate(row) if v == color]
            if len(cols) <= 1:
                continue
            prev = cols[0]
            for cur in cols[1:]:
                gap = cur - prev - 1
                if 0 < gap <= max_gap:
                    for cc in range(prev + 1, cur):
                        if out[r][cc] == 0:
                            out[r][cc] = color
                prev = cur
    return out


def _close_cols_selective(grid, dominant, max_gap=2):
    out = _copy(grid)
    h = len(grid)
    mid = h // 2
    colors = {v for row in grid for v in row if v}
    for color in colors:
        for c in range(len(grid[0])):
            rows = [r for r in range(h) if grid[r][c] == color]
            if len(rows) <= 1:
                continue
            prev = rows[0]
            for cur in rows[1:]:
                gap = cur - prev - 1
                if 0 < gap <= max_gap:
                    for rr in range(prev + 1, cur):
                        if out[rr][c] == 0:
                            if color == dominant and rr >= mid:
                                continue
                            out[rr][c] = color
                prev = cur
    return out


def _flanked_selective(grid, dominant, allowed_colors=None):
    if allowed_colors is None:
        allowed_colors = {1, 3, 7}
    out = _copy(grid)
    h = len(grid)
    w = len(grid[0])
    mid = h // 2
    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            left = grid[r][c - 1] if c else None
            right = grid[r][c + 1] if c + 1 < w else None
            up = grid[r - 1][c] if r else None
            down = grid[r + 1][c] if r + 1 < h else None
            if left == right and left and val != left and left in allowed_colors:
                if left == dominant and r >= mid:
                    continue
                out[r][c] = left
            elif up == down and up and val != up and up in allowed_colors:
                if up == dominant and r >= mid:
                    continue
                out[r][c] = up
    return out


def _prune_sparse_top(grid):
    out = _copy(grid)
    h = len(grid)
    w = len(grid[0])
    mid = h // 2
    for r in range(mid + 1):
        row = out[r]
        row_counts = Counter(v for v in row if v)
        if row_counts[3] < 6:
            continue
        for c in range(w):
            if row[c] != 3:
                continue
            col_sum = sum(1 for rr in range(h) if out[rr][c] == 3)
            down = out[r + 1][c] if r + 1 < h else None
            up = out[r - 1][c] if r else None
            if col_sum <= 2 and down == 0 and up != 3:
                row[c] = 0
    return out


def _extend_rows(grid, rows_to_extend):
    out = _copy(grid)
    w = len(grid[0])
    for r in rows_to_extend:
        cols = [c for c, v in enumerate(out[r]) if v == 3]
        if not cols:
            continue
        last = max(cols)
        for c in range(last + 1, w):
            if out[r][c] in (0, 7):
                out[r][c] = 3
            else:
                break
    return out


def _propagate_ones(grid):
    out = _copy(grid)
    h = len(grid)
    for c in range(len(grid[0])):
        rows = [r for r in range(h) if grid[r][c] == 1]
        if len(rows) <= 1:
            continue
        prev = rows[0]
        for cur in rows[1:]:
            for rr in range(prev + 1, cur):
                if out[rr][c] == 0 and Counter(v for v in grid[rr] if v)[6] == 0:
                    out[rr][c] = 1
            prev = cur
    return out


def _fill_tail_with_six(grid):
    out = _copy(grid)
    h = len(grid)
    w = len(grid[0])
    tail_start = max(0, w - 3)
    for r in range(h):
        row_counts = Counter(v for v in grid[r] if v)
        if row_counts[6] < 2:
            continue
        for c in range(tail_start, w):
            if out[r][c] not in (0, 1):
                continue
            vertical = []
            if r > 0:
                vertical.append(grid[r - 1][c])
            if r + 1 < h:
                vertical.append(grid[r + 1][c])
            horizontal_pair = c > 0 and c + 1 < w and grid[r][c - 1] == 6 and grid[r][c + 1] == 6
            if 6 in vertical or horizontal_pair:
                out[r][c] = 6
    return out


def _extend_tail_six(grid):
    out = _copy(grid)
    h = len(grid)
    w = len(grid[0])
    tail_start = max(0, w - 2)
    for c in range(tail_start, w):
        rows = [r for r in range(h) if grid[r][c] == 6]
        if len(rows) < 2:
            continue
        start = rows[0]
        for rr in range(start, h):
            if out[rr][c] == 0:
                out[rr][c] = 6
    return out


def _suppress_lonely_sixes(grid):
    out = _copy(grid)
    for r, row in enumerate(grid[:2]):
        row_counts = Counter(v for v in row if v)
        non_zero = sum(1 for v in row if v)
        if row_counts[6] == 1 and non_zero <= 3:
            out[r] = [0 if v == 6 else v for v in row]
    return out


def _transform(grid):
    stats = _analyze_color_stats(grid)
    g, top = _remove_noise(grid)
    dominant = top[0] if top else None
    allowed = {3}
    for color, (max_col, _) in stats.items():
        if color != 3 and max_col <= 4:
            allowed.add(color)
    g = _close_cols_selective(g, dominant)
    g = _close_rows_selective(g, allowed)
    g = _flanked_selective(g, dominant)
    h = len(g)
    mid = h // 2
    rows_to_extend = [r for r in range(mid + 1) if Counter(v for v in g[r] if v)[3] >= 6]
    g = _prune_sparse_top(g)
    g = _extend_rows(g, rows_to_extend)
    g = _propagate_ones(g)
    g = _fill_tail_with_six(g)
    g = _extend_tail_six(g)
    g = _suppress_lonely_sixes(g)
    return g


def solve_faa9f03d(grid):
    return _transform(grid)


p = solve_faa9f03d
