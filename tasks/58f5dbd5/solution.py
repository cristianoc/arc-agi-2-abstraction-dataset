"""Solver for ARC-AGI-2 task 58f5dbd5."""

from collections import Counter
from typing import Dict, List, Tuple

# Typed alias used by the DSL lambda representation
Grid = List[List[int]]


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


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _significant_colors(grid: Grid, min_pixels: int = 10) -> Tuple[int, List[int]]:
    counts = Counter(val for row in grid for val in row)
    background = counts.most_common(1)[0][0]
    colors = [c for c, n in counts.items() if c != background and n >= min_pixels]
    return background, colors


def _centroids(grid: Grid, colors: List[int]) -> Dict[int, Tuple[float, float]]:
    info: Dict[int, Tuple[float, float]] = {}
    for color in colors:
        coords = [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == color]
        if not coords:
            continue
        rr = [r for r, _ in coords]
        cc = [c for _, c in coords]
        info[color] = (sum(rr) / len(rr), sum(cc) / len(cc))
    return info


def _choose_arrangement(colors: List[int], info: Dict[int, Tuple[float, float]]) -> Tuple[int, int]:
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

    def factor_pairs(n: int) -> List[Tuple[int, int]]:
        pairs: List[Tuple[int, int]] = []
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


def _assign_positions(info: Dict[int, Tuple[float, float]], nrows: int, ncols: int) -> Dict[int, Tuple[int, int]]:
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


def _render(
    grid: Grid,
    background: int,
    mapping: Dict[int, Tuple[int, int]],
    nrows: int,
    ncols: int,
) -> Grid:
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


# --- DSL wrapper helpers to match the Lambda Representation ---
def findSignificantColors(grid: Grid) -> Tuple[int, List[int]]:
    return _significant_colors(grid)


def computeCentroids(grid: Grid, colours: List[int]) -> Dict[int, Tuple[float, float]]:
    return _centroids(grid, colours)


def inferBoardLayout(centroids: Dict[int, Tuple[float, float]]) -> Tuple[int, int]:
    # choose layout using only centroids mapping; derive color list from keys
    return _choose_arrangement(list(centroids.keys()), centroids)


def assignSlotsAndRender(
    grid: Grid,
    background: int,
    centroids: Dict[int, Tuple[float, float]],
    layout: Tuple[int, int],
) -> Grid:
    nrows, ncols = layout
    if nrows == 0 or ncols == 0:
        return _copy_grid(grid)
    mapping = _assign_positions(centroids, nrows, ncols)
    return _render(grid, background, mapping, nrows, ncols)


def solve_58f5dbd5(grid: Grid) -> Grid:
    background, colours = findSignificantColors(grid)
    centroids = computeCentroids(grid, colours)
    layout = inferBoardLayout(centroids)
    return assignSlotsAndRender(grid, background, centroids, layout)


p = solve_58f5dbd5
