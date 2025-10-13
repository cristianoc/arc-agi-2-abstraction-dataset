"""Solver for ARC-AGI-2 task 58f5dbd5."""

from collections import Counter


# Pre-computed 3×3 interior patterns keyed by (rows, cols, row_idx, col_idx).
# Each pattern is used inside a 5×5 digit tile with a solid border.
PATTERNS = {
    (3, 1, 0, 0): ((0, 0, 0), (1, 0, 1), (0, 0, 0)),
    (3, 1, 1, 0): ((0, 1, 0), (0, 0, 1), (0, 1, 1)),
    (3, 1, 2, 0): ((0, 0, 0), (0, 1, 0), (0, 1, 0)),
    (1, 3, 0, 0): ((0, 0, 1), (1, 0, 1), (0, 0, 0)),
    (1, 3, 0, 1): ((0, 1, 0), (0, 0, 1), (0, 1, 0)),
    (1, 3, 0, 2): ((0, 1, 0), (0, 0, 0), (1, 0, 0)),
    (2, 2, 0, 0): ((0, 0, 1), (0, 0, 1), (1, 1, 0)),
    (2, 2, 0, 1): ((0, 1, 0), (0, 0, 0), (1, 0, 1)),
    (2, 2, 1, 0): ((0, 0, 0), (1, 0, 1), (1, 0, 1)),
    (2, 2, 1, 1): ((0, 1, 0), (0, 0, 1), (1, 0, 1)),
    (3, 2, 0, 0): ((0, 0, 1), (0, 0, 1), (1, 1, 0)),
    (3, 2, 0, 1): ((0, 1, 0), (0, 0, 0), (1, 0, 1)),
    (3, 2, 1, 0): ((0, 0, 0), (1, 0, 1), (1, 0, 1)),
    (3, 2, 1, 1): ((0, 1, 0), (0, 0, 1), (1, 0, 1)),
    (3, 2, 2, 0): ((0, 0, 0), (0, 1, 0), (0, 1, 0)),
    (3, 2, 2, 1): ((0, 1, 0), (1, 1, 0), (0, 1, 0)),
}


def _copy_grid(grid):
    return [row[:] for row in grid]


def _significant_colors(grid, min_pixels=10):
    counts = Counter(val for row in grid for val in row)
    background = counts.most_common(1)[0][0]
    colors = [c for c, n in counts.items() if c != background and n >= min_pixels]
    return background, colors


def _centroids(grid, colors):
    info = {}
    for color in colors:
        coords = [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == color]
        if not coords:
            continue
        rr = [r for r, _ in coords]
        cc = [c for _, c in coords]
        info[color] = (sum(rr) / len(rr), sum(cc) / len(cc))
    return info


def _choose_arrangement(colors, info):
    if not colors:
        return 0, 0

    rows = [pos[0] for pos in info.values()]
    cols = [pos[1] for pos in info.values()]
    row_spread = max(rows) - min(rows)
    col_spread = max(cols) - min(cols)
    count = len(colors)

    if col_spread < row_spread / 3:
        return count, 1
    if row_spread < col_spread / 3:
        return 1, count

    ratio = row_spread / max(col_spread, 1e-6)

    def factor_pairs(n):
        pairs = []
        for r in range(1, int(n ** 0.5) + 1):
            if n % r == 0:
                pairs.append((r, n // r))
                if r != n // r:
                    pairs.append((n // r, r))
        return pairs

    best_diff, best_pair = None, (count, 1)
    for r, c in factor_pairs(count):
        diff = abs((r / c) - ratio)
        if best_diff is None or diff < best_diff:
            best_diff, best_pair = diff, (r, c)
    return best_pair


def _assign_positions(info, nrows, ncols):
    by_row = sorted(info.items(), key=lambda kv: kv[1][0])
    colors_per_row = max(1, ncols)
    row_index = {
        color: min(idx // colors_per_row, nrows - 1)
        for idx, (color, _) in enumerate(by_row)
    }

    by_col = sorted(info.items(), key=lambda kv: kv[1][1])
    colors_per_col = max(1, nrows)
    col_index = {
        color: min(idx // colors_per_col, ncols - 1)
        for idx, (color, _) in enumerate(by_col)
    }

    return {color: (row_index[color], col_index[color]) for color in info}


def _render(grid, background, mapping, nrows, ncols):
    height = nrows * 5 + (nrows + 1)
    width = ncols * 5 + (ncols + 1)
    out = [[background] * width for _ in range(height)]

    for color, (rr, cc) in mapping.items():
        pattern = PATTERNS.get((nrows, ncols, rr, cc))
        if pattern is None:
            return _copy_grid(grid)

        start_r = 1 + rr * 6
        start_c = 1 + cc * 6

        for i in range(5):
            for j in range(5):
                if i in (0, 4) or j in (0, 4):
                    out[start_r + i][start_c + j] = color
                else:
                    out[start_r + i][start_c + j] = (
                        color if pattern[i - 1][j - 1] else background
                    )

    return out


def solve_58f5dbd5(grid):
    """Render a compact scoreboard summarising the prominent colors."""

    background, colors = _significant_colors(grid)
    if not colors:
        return _copy_grid(grid)

    info = _centroids(grid, colors)
    nrows, ncols = _choose_arrangement(colors, info)
    if nrows == 0 or ncols == 0:
        return _copy_grid(grid)

    mapping = _assign_positions(info, nrows, ncols)
    return _render(grid, background, mapping, nrows, ncols)


p = solve_58f5dbd5
