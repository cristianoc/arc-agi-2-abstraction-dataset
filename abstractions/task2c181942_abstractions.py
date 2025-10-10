"""Abstractions explored for ARC task 2c181942."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

Grid = List[List[int]]
Coord = Tuple[int, int]

DATA_PATH = Path(__file__).resolve().parents[1] / "arc2_samples" / "2c181942.json"
BACKGROUND = 8


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def gather_stats(grid: Grid) -> Tuple[Counter[int], Dict[int, List[int]], Dict[int, List[int]]]:
    counts: Counter[int] = Counter()
    rows: Dict[int, List[int]] = defaultdict(list)
    cols: Dict[int, List[int]] = defaultdict(list)
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == BACKGROUND:
                continue
            counts[val] += 1
            rows[val].append(r)
            cols[val].append(c)
    return counts, rows, cols


def detect_axis(grid: Grid) -> Tuple[int, Dict[int, int], Dict[int, List[Coord]]]:
    height, width = len(grid), len(grid[0])
    best: Tuple[int, int] | None = None
    best_counts: Dict[int, int] = {}
    best_cells: Dict[int, List[Coord]] = {}
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
        key = (score, c)
        if best is None or key < best:
            best = key
            best_counts = eligible
            best_cells = col_cells
    if best is None:
        raise ValueError("Axis detection failed for this grid")
    return best[1], best_counts, best_cells


def select_vertical(axis_counts: Dict[int, int], total_counts: Counter[int], axis_cells: Dict[int, List[Coord]]) -> Tuple[int, int]:
    ranked: List[Tuple[float, int, int]] = []
    for color, cnt in axis_counts.items():
        ratio = cnt / total_counts[color]
        ranked.append((ratio, total_counts[color], color))
    ranked.sort(key=lambda item: (-item[0], item[1], item[2]))
    chosen = [item[2] for item in ranked[:2]]
    rows = {color: mean(r for r, _ in axis_cells[color]) for color in chosen}
    chosen.sort(key=lambda color: rows[color])
    return chosen[0], chosen[-1]


def normalise_rows(mid_start: int, mid_end: int, height: int) -> List[int]:
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


def axis_cross_solver(grid: Grid, allow_top_shift: bool) -> Grid:
    counts, rows_by_color, cols_by_color = gather_stats(grid)
    if not counts:
        return copy_grid(grid)

    axis_left, axis_counts, axis_cells = detect_axis(grid)
    axis_right = axis_left + 1

    top_color, bottom_color = select_vertical(axis_counts, counts, axis_cells)
    top_axis_rows = [r for r, _ in axis_cells[top_color]]
    bottom_axis_rows = [r for r, _ in axis_cells[bottom_color]]
    mid_rows = normalise_rows(min(top_axis_rows), max(bottom_axis_rows), len(grid))
    mid_start, mid_end = mid_rows[0], mid_rows[-1]

    axis_centre_row = (mid_start + mid_end) / 2
    axis_centre_col = axis_left + 0.5

    width = len(grid[0])
    output = [[BACKGROUND] * width for _ in range(len(grid))]

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

    top_axis_ratio = axis_counts[top_color] / counts[top_color]
    if allow_top_shift and len(top_rows_used) == 3 and top_axis_ratio < 0.5:
        topmost = min(top_rows_used)
        for col in (axis_left, axis_right):
            if output[topmost][col] == top_color:
                output[topmost][col] = BACKGROUND
        for col in (axis_left - 1, axis_right + 1):
            if 0 <= col < width:
                output[topmost][col] = top_color

    horizontal_colors = [c for c in counts if c not in (top_color, bottom_color)]
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


def abstraction_identity(grid: Grid) -> Grid:
    return copy_grid(grid)


def abstraction_axis_cross_no_shift(grid: Grid) -> Grid:
    return axis_cross_solver(grid, allow_top_shift=False)


def abstraction_axis_cross(grid: Grid) -> Grid:
    return axis_cross_solver(grid, allow_top_shift=True)


ABSTRACTIONS: Sequence[Tuple[str, Callable[[Grid], Grid]]] = (
    ("identity", abstraction_identity),
    ("axis-cross-no-shift", abstraction_axis_cross_no_shift),
    ("axis-cross-final", abstraction_axis_cross),
)


def grids_equal(a: Grid, b: Grid) -> bool:
    return all(row_a == row_b for row_a, row_b in zip(a, b))


def format_grid(grid: Grid) -> str:
    return "\n".join("".join("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[cell] for cell in row) for row in grid)


def evaluate() -> None:
    data = json.loads(DATA_PATH.read_text())
    train = data["train"]
    test = data.get("test", [])

    for name, solver in ABSTRACTIONS:
        train_matches: List[bool] = []
        for pair in train:
            pred = solver(pair["input"])
            train_matches.append(grids_equal(pred, pair["output"]))
        first_failure = next((i for i, ok in enumerate(train_matches) if not ok), None)
        solved = sum(train_matches)
        print(f"{name}: train {solved}/{len(train_matches)}", end="")
        if first_failure is not None:
            print(f"  first failure idx={first_failure}")
        else:
            print("  all correct")

        for idx, pair in enumerate(test):
            pred = solver(pair["input"])
            print(f"  test[{idx}] prediction:\n{format_grid(pred)}\n")


if __name__ == "__main__":
    evaluate()
