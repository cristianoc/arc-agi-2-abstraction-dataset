"""Solver for ARC-AGI-2 task 62593bfd."""

from typing import Dict, List, Tuple, Optional, TypedDict


Grid = List[List[int]]
Color = int


class ColorRecord(TypedDict):
    cells: List[Tuple[int, int]]
    min_row: int
    max_row: int
    column_counts: Dict[int, int]


ColumnStats = Dict[int, ColorRecord]
ShiftPlan = Dict[int, str]


def _mode_background(grid: Grid) -> int:
    counts: Dict[int, int] = {}
    for row in grid:
        for v in row:
            counts[v] = counts.get(v, 0) + 1
    # choose the value with max frequency; ties broken by larger color id for determinism
    return max(counts.items(), key=lambda kv: (kv[1], kv[0]))[0] if counts else 0


def aggregateColumnCounts(grid: Grid) -> ColumnStats:
    """Aggregate per-colour cells, min/max rows, and counts per column (background excluded)."""
    if not grid or not grid[0]:
        return {}
    h = len(grid)
    w = len(grid[0])
    bg = _mode_background(grid)
    info: ColumnStats = {}
    # single pass over the grid; connectivity not required for aggregate stats
    for r in range(h):
        row = grid[r]
        for c in range(w):
            v = row[c]
            if v == bg:
                continue
            rec = info.setdefault(v, {"cells": [], "min_row": h, "max_row": -1, "column_counts": {}})
            rec["cells"].append((r, c))
            rec["min_row"] = min(rec["min_row"], r)
            rec["max_row"] = max(rec["max_row"], r)
            cc = rec["column_counts"]
            cc[c] = cc.get(c, 0) + 1
    return info


def rankColorsByDominance(column_counts: ColumnStats) -> List[Color]:
    """Order colours by total occupancy (sum across columns), descending, tiebreak by id."""
    totals = {color: sum(column_counts[color]["column_counts"].values()) for color in column_counts}
    return sorted(totals, key=lambda color: (-totals[color], color))


def computeShiftTargets(grid: Grid, ordered_colors: List[Color]) -> ShiftPlan:
    """Decide per-colour orientation ('top' or 'bottom') using aggregated overlap logic."""
    info = aggregateColumnCounts(grid)
    height = len(grid)
    colors = sorted(info)
    forced: Dict[int, Tuple[str, int]] = {}

    for i, ca in enumerate(colors):
        counts_a = info[ca]["column_counts"]
        for cb in colors[i + 1 :]:
            counts_b = info[cb]["column_counts"]
            common = set(counts_a) & set(counts_b)
            if not common:
                continue
            area_a = sum(counts_a[col] for col in common)
            area_b = sum(counts_b[col] for col in common)
            if area_a == area_b:
                if info[ca]["min_row"] == info[cb]["min_row"]:
                    top_color = max(ca, cb)
                else:
                    top_color = ca if info[ca]["min_row"] > info[cb]["min_row"] else cb
                weight = 1
            else:
                top_color = ca if area_a > area_b else cb
                weight = 1 + abs(area_a - area_b)
            bottom_color = cb if top_color == ca else ca
            for color, orient in ((top_color, "top"), (bottom_color, "bottom")):
                cur = forced.get(color)
                if cur is None or weight > cur[1]:
                    forced[color] = (orient, weight)

    orientations: Dict[int, Optional[str]] = {color: (forced[color][0] if color in forced else None) for color in colors}

    free = [color for color, orient in orientations.items() if orient is None]
    if free:
        min_rows = [info[color]["min_row"] for color in free]
        if len(min_rows) > 1:
            # median without numpy
            sorted_vals = sorted(float(x) for x in min_rows)
            mid = len(sorted_vals) // 2
            threshold = (sorted_vals[mid] if len(sorted_vals) % 2 == 1 else (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0)
        else:
            threshold = (height - 1) / 2.0
        for color, min_row in zip(free, min_rows):
            orientations[color] = "top" if min_row >= threshold else "bottom"

    return {k: orientations[k] or "bottom" for k in colors}


def applyColorShifts(grid: Grid, targets: ShiftPlan) -> Grid:
    """Translate each colour's cells to the top/bottom edge as decided by the targets."""
    if not grid or not grid[0]:
        return []
    h = len(grid)
    w = len(grid[0])
    bg = _mode_background(grid)
    info = aggregateColumnCounts(grid)
    out = [[bg for _ in range(w)] for _ in range(h)]

    for color in sorted(info):
        orient = targets.get(color)
        if orient not in {"top", "bottom"}:
            continue
        min_row = info[color]["min_row"]
        max_row = info[color]["max_row"]
        delta = (-min_row) if orient == "top" else ((h - 1) - max_row)
        for r, c in info[color]["cells"]:
            nr = r + delta
            if 0 <= nr < h:
                out[nr][c] = color
    return out


def solve_62593bfd(grid: Grid) -> Grid:
    column_counts = aggregateColumnCounts(grid)
    ordered_colors = rankColorsByDominance(column_counts)
    targets = computeShiftTargets(grid, ordered_colors)
    return applyColorShifts(grid, targets)


p = solve_62593bfd
