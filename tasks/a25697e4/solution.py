"""Solver for ARC-AGI-2 task a25697e4 (evaluation split)."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

Grid = List[List[int]]


def _sign(value: float) -> int:
    return (value > 0) - (value < 0)


def _collect_colors(grid: Grid):
    h = len(grid)
    w = len(grid[0])
    counts: Dict[int, int] = Counter()
    positions: Dict[int, List[Tuple[int, int]]] = {}
    for r in range(h):
        for c in range(w):
            color = grid[r][c]
            counts[color] += 1
            positions.setdefault(color, []).append((r, c))
    return counts, positions


def _select_bridge_color(
    anchor: int,
    colors: Sequence[int],
    counts: Dict[int, int],
    positions: Dict[int, List[Tuple[int, int]]],
    hole_diff: float,
    anchor_mean_row: float,
):
    candidates = []
    for color in colors:
        if color == anchor:
            continue
        pts = positions[color]
        avg_row = sum(r for r, _ in pts) / len(pts)
        row_diff = avg_row - anchor_mean_row
        if (hole_diff > 0 and row_diff >= 0) or (hole_diff < 0 and row_diff <= 0):
            candidates.append((abs(row_diff - hole_diff), color))
    if not candidates:
        for color in colors:
            if color == anchor:
                continue
            pts = positions[color]
            avg_row = sum(r for r, _ in pts) / len(pts)
            row_diff = avg_row - anchor_mean_row
            candidates.append((abs(row_diff - hole_diff), color))
    candidates.sort()
    return candidates[0][1]


def _place_third_color(out_grid: Grid, params):
    (
        need,
        h_main,
        v_steps,
        rem,
        hd,
        hole_diff,
        holes_extreme,
        anchor_set,
        hole_set,
        r_bounds,
        colors_bundle,
    ) = params

    h, w = len(out_grid), len(out_grid[0])
    (r0, r1) = r_bounds
    third = colors_bundle["third"]
    base_info = colors_bundle["base_info"]

    def make_cells(base_row, base_col, vd):
        horizontal = []
        for i in range(h_main):
            c = base_col + hd * i
            if not (0 <= c < w):
                return None
            horizontal.append((base_row, c))
        if not horizontal:
            return None
        corner_row, corner_col = horizontal[-1]
        vertical = []
        for step in range(1, v_steps + 1):
            r = corner_row + vd * step
            if not (0 <= r < h):
                return None
            vertical.append((r, corner_col))
        tail = []
        if rem > 0:
            if v_steps > 0:
                anchor_cell = vertical[-1] if hd > 0 else vertical[0]
            else:
                anchor_cell = (corner_row, corner_col)
            tr, tc = anchor_cell
            for i in range(1, rem + 1):
                nc = tc + hd * i
                if not (0 <= nc < w):
                    return None
                tail.append((tr, nc))
        cells = horizontal + vertical + tail
        if len(cells) != need or len(set(cells)) != len(cells):
            return None
        return cells

    solutions = []
    desired_vd = _sign(hole_diff) or (-1 if hd > 0 else 1)

    if hd > 0:
        for vd in (-1, 1):
            if vd < 0:
                hole = max(holes_extreme, key=lambda rc: rc[0])
            else:
                hole = min(holes_extreme, key=lambda rc: rc[0])
            base_row = hole[0]
            base_col = hole[1] + 1
            base_row = max(0, min(len(out_grid) - 1, base_row))
            cells = make_cells(base_row, base_col, vd)
            if not cells:
                continue
            penalty = sum(
                (20 if cell in anchor_set else 0) + (10 if cell in hole_set else 0)
                for cell in cells
            )
            preference = abs(vd - desired_vd)
            solutions.append((penalty, preference, cells))
    else:
        for vd in (-1, 1):
            for hole in {
                min(holes_extreme, key=lambda rc: rc[0]),
                max(holes_extreme, key=lambda rc: rc[0]),
            }:
                base_row = hole[0]
                if hd < 0 and vd < 0:
                    base_row -= 1
                base_row = max(0, min(len(out_grid) - 1, base_row))
                base_col = hole[1]
                cells = make_cells(base_row, base_col, vd)
                if not cells:
                    continue
                penalty = sum(
                    (20 if cell in anchor_set else 0) + (10 if cell in hole_set else 0)
                    for cell in cells
                )
                preference = abs(vd - desired_vd) + abs(base_row - hole[0])
                solutions.append((penalty, preference, cells))

    if not solutions:
        return
    solutions.sort(key=lambda tpl: (tpl[0], tpl[1]))
    chosen = solutions[0][2]
    for r, c in chosen:
        out_grid[r][c] = third


# === Typed-DSL friendly helpers ===

@dataclass(frozen=True)
class ColourStats:
    background: int
    colors: List[int]
    counts: Dict[int, int]
    positions: Dict[int, List[Tuple[int, int]]]
    anchor: int
    anchor_cells: List[Tuple[int, int]]


@dataclass(frozen=True)
class HoleStats:
    holes: List[Tuple[int, int]]
    hole_set: set[Tuple[int, int]]
    r_bounds: Tuple[int, int]
    c_bounds: Tuple[int, int]
    anchor_mean_row: float
    hole_mean_row: float
    hole_diff: float


def collectColorStats(grid: Grid) -> ColourStats:
    counts, positions = _collect_colors(grid)
    background = max(counts.items(), key=lambda kv: kv[1])[0]
    colors = [color for color in counts if color != background]
    anchor = max(colors, key=lambda color: counts[color])
    anchor_cells = positions[anchor]
    return ColourStats(
        background=background,
        colors=colors,
        counts=dict(counts),
        positions=positions,
        anchor=anchor,
        anchor_cells=anchor_cells,
    )


def analyseHoles(anchor_cells: List[Tuple[int, int]]) -> HoleStats:
    rows = [r for r, _ in anchor_cells]
    cols = [c for _, c in anchor_cells]
    r0, r1 = min(rows), max(rows)
    c0, c1 = min(cols), max(cols)
    anchor_set = set(anchor_cells)
    holes = [
        (r, c)
        for r in range(r0, r1 + 1)
        for c in range(c0, c1 + 1)
        if (r, c) not in anchor_set
    ]
    if holes:
        anchor_mean_row = sum(r for r, _ in anchor_cells) / len(anchor_cells)
        hole_mean_row = sum(r for r, _ in holes) / len(holes)
        hole_diff = hole_mean_row - anchor_mean_row
    else:
        anchor_mean_row = sum(r for r, _ in anchor_cells) / len(anchor_cells)
        hole_mean_row = anchor_mean_row
        hole_diff = 0.0
    return HoleStats(
        holes=holes,
        hole_set=set(holes),
        r_bounds=(r0, r1),
        c_bounds=(c0, c1),
        anchor_mean_row=anchor_mean_row,
        hole_mean_row=hole_mean_row,
        hole_diff=hole_diff,
    )


def placeThirdComponent(grid: Grid, colour_stats: ColourStats, hole_stats: HoleStats) -> Grid:
    if not hole_stats.holes:
        return [row[:] for row in grid]

    background = colour_stats.background
    colors = colour_stats.colors
    counts = colour_stats.counts
    positions = colour_stats.positions
    anchor = colour_stats.anchor
    anchor_pts = colour_stats.anchor_cells
    anchor_set = set(anchor_pts)

    holes = hole_stats.holes
    holes_set = hole_stats.hole_set
    (r0, r1) = hole_stats.r_bounds

    bridge = _select_bridge_color(
        anchor, colors, counts, positions, hole_stats.hole_diff, hole_stats.anchor_mean_row
    )
    third = next(color for color in colors if color not in {anchor, bridge})

    h = len(grid)
    w = len(grid[0])
    out_grid = [[background for _ in range(w)] for _ in range(h)]

    for r, c in anchor_pts:
        out_grid[r][c] = anchor
    for r, c in holes:
        out_grid[r][c] = bridge

    total_other = sum(counts[color] for color in colors if color != anchor)
    need = total_other - len(holes)
    if need <= 0:
        return out_grid

    h_main = max(2, need - 3)
    if h_main > need:
        h_main = need
    v_steps = min(2, max(0, need - h_main))
    rem = need - h_main - v_steps

    anchor_mean_col = sum(c for _, c in anchor_pts) / len(anchor_pts)
    third_mean_col = sum(c for _, c in positions[third]) / len(positions[third])
    hd = _sign(third_mean_col - anchor_mean_col)
    if hd == 0:
        hd = 1 if anchor_mean_col < (w - 1) / 2 else -1

    holes_extreme = [
        hole for hole in holes if hole[1] == (max(holes, key=lambda rc: hd * rc[1])[1])
    ]
    params = (
        need,
        h_main,
        v_steps,
        rem,
        hd,
        hole_stats.hole_diff,
        holes_extreme,
        anchor_set,
        holes_set,
        (r0, r1),
        {"third": third, "base_info": (hole_stats.anchor_mean_row, anchor_mean_col)},
    )
    _place_third_color(out_grid, params)

    return out_grid


def solve_a25697e4(grid: Grid) -> Grid:
    colour_stats = collectColorStats(grid)
    hole_stats = analyseHoles(colour_stats.anchor_cells)
    return placeThirdComponent(grid, colour_stats, hole_stats)


p = solve_a25697e4
