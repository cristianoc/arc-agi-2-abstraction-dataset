"""Solver for ARC-AGI-2 task 2c181942.

Refactored to align the main solver with the typed-DSL lambda while
preserving original behaviour via pure helpers.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Dict, List, Optional, Sequence, Tuple

Grid = List[List[int]]
Coord = Tuple[int, int]
Stats = Tuple[Counter[int], Dict[int, List[int]], Dict[int, List[int]], Dict[int, List[Coord]]]
Axis = Optional[Tuple[int, Dict[int, int], Dict[int, List[Coord]]]]


BACKGROUND = 8


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def gatherColorStats(grid: Grid) -> Stats:
    counts: Counter[int] = Counter()
    rows: Dict[int, List[int]] = defaultdict(list)
    cols: Dict[int, List[int]] = defaultdict(list)
    cells: Dict[int, List[Coord]] = defaultdict(list)
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == BACKGROUND:
                continue
            counts[val] += 1
            rows[val].append(r)
            cols[val].append(c)
            cells[val].append((r, c))
    return counts, rows, cols, cells


def detectAxis(grid: Grid) -> Axis:
    """Return (axis_left_col, per-color counts, per-color cells) or None."""
    height, width = len(grid), len(grid[0])
    best: Optional[Tuple[int, int, Dict[int, int]]] = None
    best_cells: Optional[Dict[int, List[Coord]]] = None
    for c in range(width - 1):
        col_counts: Counter[int] = Counter()
        col_cells: Dict[int, List[Coord]] = defaultdict(list)
        for r in range(height):
            for dc in (0, 1):
                val = grid[r][c + dc]
                if val == BACKGROUND:
                    continue
                col_counts[val] += 1
                col_cells[val].append((r, c + dc))
        eligible = {color: cnt for color, cnt in col_counts.items() if cnt >= 2}
        if len(eligible) < 2:
            continue
        score = sum(eligible.values())
        if best is None or score < best[0] or (score == best[0] and c < best[1]):
            best = (score, c, eligible)
            best_cells = col_cells
    if best is None or best_cells is None:
        return None
    return best[1], best[2], best_cells


def _select_vertical_colors(axis_counts: Dict[int, int], total_counts: Counter[int], axis_cells: Dict[int, List[Coord]]) -> Tuple[int, int]:
    ranked: List[Tuple[float, int, int]] = []
    for color, cnt in axis_counts.items():
        ratio = cnt / total_counts[color]
        ranked.append((ratio, total_counts[color], color))
    ranked.sort(key=lambda item: (-item[0], item[1], item[2]))
    chosen = [item[2] for item in ranked[:2]]
    rows = {color: mean(r for r, _ in axis_cells[color]) for color in chosen}
    chosen.sort(key=lambda color: rows[color])
    return chosen[0], chosen[-1]


def selectVerticalColors(stats: Stats, axis: Axis) -> Tuple[int, int]:
    counts, _rows_by_color, _cols_by_color, _cells_by_color = stats
    if axis is None or not counts:
        return BACKGROUND, BACKGROUND
    axis_left, axis_counts, axis_cells_map = axis
    _ = axis_left  # unused here, kept for symmetry
    return _select_vertical_colors(axis_counts, counts, axis_cells_map)


def _normalise_rows(mid_start: int, mid_end: int, height: int) -> List[int]:
    rows = list(range(mid_start, mid_end + 1))
    while len(rows) < 4 and rows[0] > 0:
        rows.insert(0, rows[0] - 1)
    while len(rows) < 4 and rows[-1] < height - 1:
        rows.append(rows[-1] + 1)
    while len(rows) > 4:
        centre = (rows[0] + rows[-1]) / 2
        if abs(rows[0] - centre) > abs(rows[-1] - centre):
            rows.pop(0)
        else:
            rows.pop()
    return rows


def fillVerticalArms(grid: Grid, colors: Tuple[int, int], axis: Axis) -> Grid:
    # Preserve original guards inside helper
    counts, _rows_by_color, _cols_by_color, _cells_by_color = gatherColorStats(grid)
    if not counts or axis is None:
        return _copy_grid(grid)

    axis_left, axis_counts, axis_cells_map = axis
    axis_right = axis_left + 1

    top_color, bottom_color = colors
    # Find mid rows between extreme occurrences on the axis
    top_axis_rows = [r for r, _ in axis_cells_map[top_color]]
    bottom_axis_rows = [r for r, _ in axis_cells_map[bottom_color]]
    mid_rows = _normalise_rows(min(top_axis_rows), max(bottom_axis_rows), len(grid))
    mid_start, mid_end = mid_rows[0], mid_rows[-1]

    width = len(grid[0])
    output: Grid = [[BACKGROUND] * width for _ in range(len(grid))]

    def fill_vertical(color: int, start_row: int, step: int) -> List[int]:
        remaining = counts[color]
        row = start_row
        used_rows: List[int] = []
        while remaining > 0 and 0 <= row < len(grid):
            for col in (axis_left, axis_right):
                if remaining <= 0:
                    break
                output[row][col] = color
                if row not in used_rows:
                    used_rows.append(row)
                remaining -= 1
            row += step
        return used_rows

    top_rows_used = fill_vertical(top_color, mid_start, -1)
    fill_vertical(bottom_color, mid_end, 1)

    # Selective top-row flare adjustment
    top_axis_ratio = axis_counts[top_color] / counts[top_color]
    if len(top_rows_used) == 3 and top_axis_ratio < 0.5:
        topmost = min(top_rows_used)
        for col in (axis_left, axis_right):
            if output[topmost][col] == top_color:
                output[topmost][col] = BACKGROUND
        left_target = axis_left - 1
        right_target = axis_right + 1
        if 0 <= left_target < width:
            output[topmost][left_target] = top_color
        if 0 <= right_target < width:
            output[topmost][right_target] = top_color

    return output


def placeHorizontalArms(grid: Grid, stats: Stats, axis: Axis) -> Grid:
    counts, rows_by_color, cols_by_color, _cells_by_color = stats
    if axis is None:
        return _copy_grid(grid)
    axis_left, axis_counts, axis_cells_map = axis
    axis_right = axis_left + 1

    # Recompute mid rows and centres deterministically from stats+axis
    top_color, bottom_color = _select_vertical_colors(axis_counts, counts, axis_cells_map)
    top_axis_rows = [r for r, _ in axis_cells_map[top_color]]
    bottom_axis_rows = [r for r, _ in axis_cells_map[bottom_color]]
    mid_rows = _normalise_rows(min(top_axis_rows), max(bottom_axis_rows), len(grid))
    mid_start, mid_end = mid_rows[0], mid_rows[-1]
    axis_centre_row = (mid_start + mid_end) / 2
    axis_centre_col = axis_left + 0.5

    width = len(grid[0])
    output: Grid = [row[:] for row in grid]

    horizontal_colors = [color for color in counts if color not in (top_color, bottom_color)]
    if not horizontal_colors:
        return output

    def centroid(color: int) -> Tuple[float, float]:
        rs = rows_by_color[color]
        cs = cols_by_color[color]
        return sum(rs) / len(rs), sum(cs) / len(cs)

    deltas: List[Tuple[float, float, int]] = []
    for color in horizontal_colors:
        r_cent, c_cent = centroid(color)
        deltas.append((c_cent - axis_centre_col, r_cent - axis_centre_row, color))

    left_side = [item for item in deltas if item[0] < 0]
    right_side = [item for item in deltas if item[0] >= 0]
    if left_side and right_side:
        left_color = max(left_side, key=lambda item: item[0])[2]
        right_color = min(right_side, key=lambda item: item[0])[2]
    elif left_side:
        left_side.sort(key=lambda item: item[0], reverse=True)
        left_color = left_side[0][2]
        right_color = left_side[-1][2] if len(left_side) > 1 else left_color
    else:
        right_side.sort(key=lambda item: item[0])
        left_color = right_side[0][2]
        right_color = right_side[-1][2] if len(right_side) > 1 else left_color
    if left_color == right_color:
        for _, _, color in deltas:
            if color != left_color:
                right_color = color
                break

    def row_counts(color: int) -> List[int]:
        total = counts[color]
        delta_col, delta_row, _ = next(item for item in deltas if item[2] == color)
        if delta_row < 0:
            outer = 1
        else:
            if delta_col >= 0:
                outer = 1
            else:
                outer = min(2, max(1, total // 4))
        inner = max(0, (total - 2 * outer) // 2)
        return [outer, inner, inner, outer]

    left_counts = row_counts(left_color)
    right_counts = row_counts(right_color)

    def place_run(row: int, start_col: int, count: int, color: int) -> None:
        if count <= 0:
            return
        start = max(0, min(start_col, width - count))
        for offset in range(count):
            col = start + offset
            if 0 <= row < len(grid):
                output[row][col] = color

    right_inner_width = right_counts[1]
    for idx, row in enumerate(mid_rows):
        left_count = left_counts[idx]
        if left_count:
            start = axis_left - left_count if idx in (1, 2) else axis_left - 4
            place_run(row, start, left_count, left_color)
        right_count = right_counts[idx]
        if right_count:
            start = axis_right + 1 if idx in (1, 2) else axis_right + right_inner_width
            place_run(row, start, right_count, right_color)

    return output


def solve_2c181942(grid: Grid) -> Grid:
    stats = gatherColorStats(grid)
    axis = detectAxis(grid)
    top_color, bottom_color = selectVerticalColors(stats, axis)

    result = fillVerticalArms(grid, (top_color, bottom_color), axis)
    return placeHorizontalArms(result, stats, axis)


# Alias used by the framework
p = solve_2c181942
