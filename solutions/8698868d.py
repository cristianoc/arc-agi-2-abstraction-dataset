"""Solver for ARC-AGI-2 task 8698868d (split: evaluation)."""

from collections import Counter, deque
from itertools import permutations
from typing import Dict, Iterable, List, Sequence, Tuple

Grid = List[List[int]]


def _clone(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _most_common_color(grid: Grid) -> int:
    return Counter(val for row in grid for val in row).most_common(1)[0][0]


def _extract_components(grid: Grid, *, ignore: Iterable[int]) -> List[Dict]:
    h, w = len(grid), len(grid[0])
    ignore_set = set(ignore)
    seen = [[False] * w for _ in range(h)]
    components: List[Dict] = []

    for r in range(h):
        for c in range(w):
            if seen[r][c] or grid[r][c] in ignore_set:
                continue
            color = grid[r][c]
            q = deque([(r, c)])
            seen[r][c] = True
            cells = []
            while q:
                cr, cc = q.popleft()
                cells.append((cr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc] and grid[nr][nc] == color:
                        seen[nr][nc] = True
                        q.append((nr, nc))

            rows = [r for r, _ in cells]
            cols = [c for _, c in cells]
            rmin, rmax = min(rows), max(rows)
            cmin, cmax = min(cols), max(cols)
            height = rmax - rmin + 1
            width = cmax - cmin + 1
            bbox_area = height * width
            fill_ratio = len(cells) / bbox_area
            components.append(
                {
                    "color": color,
                    "cells": cells,
                    "bbox": (rmin, rmax, cmin, cmax),
                    "area": len(cells),
                    "height": height,
                    "width": width,
                    "bbox_area": bbox_area,
                    "fill_ratio": fill_ratio,
                    "center": ((rmin + rmax) / 2.0, (cmin + cmax) / 2.0),
                }
            )

    return components


def _classify_components(components: Sequence[Dict]) -> Tuple[List[Dict], List[Dict]]:
    max_bbox_area = max(comp["bbox_area"] for comp in components)
    backgrounds = [comp for comp in components if comp["bbox_area"] == max_bbox_area]
    shapes = [comp for comp in components if comp not in backgrounds]
    return backgrounds, shapes


def _assign_shapes(
    backgrounds: Sequence[Dict],
    shapes: Sequence[Dict],
    *,
    row_weight: float = 0.3,
    col_weight: float = 6.0,
) -> Dict[int, Dict]:
    best_perm = None
    best_cost = float("inf")
    for perm in permutations(range(len(shapes))):
        cost = 0.0
        for bg_idx, shape_idx in enumerate(perm):
            bg = backgrounds[bg_idx]
            sh = shapes[shape_idx]
            cost += row_weight * abs(bg["center"][0] - sh["center"][0])
            cost += col_weight * abs(bg["center"][1] - sh["center"][1])
        if cost < best_cost:
            best_cost = cost
            best_perm = perm

    if best_perm is None:
        raise ValueError("Failed to match backgrounds to shapes")

    return {idx: shapes[shape_idx] for idx, shape_idx in enumerate(best_perm)}


def _group_backgrounds(backgrounds: Sequence[Dict]) -> Tuple[List[Dict], int, int]:
    if not backgrounds:
        return [], 0, 0

    height = backgrounds[0]["height"]
    width = backgrounds[0]["width"]
    min_r = min(comp["bbox"][0] for comp in backgrounds)
    min_c = min(comp["bbox"][2] for comp in backgrounds)

    grouped = []
    for comp in backgrounds:
        rmin, _, cmin, _ = comp["bbox"]
        row_idx = round((rmin - min_r) / height)
        col_idx = round((cmin - min_c) / width)
        grouped.append({**comp, "grid_pos": (row_idx, col_idx)})

    rows = max(item["grid_pos"][0] for item in grouped) + 1
    cols = max(item["grid_pos"][1] for item in grouped) + 1

    grouped.sort(key=lambda item: (item["grid_pos"][0], item["grid_pos"][1]))
    return grouped, rows, cols


def _extract_shape_pattern(grid: Grid, comp: Dict) -> Grid:
    rmin, rmax, cmin, cmax = comp["bbox"]
    return [row[cmin : cmax + 1] for row in grid[rmin : rmax + 1]]


def _render_solution(
    grid: Grid,
    backgrounds: Sequence[Dict],
    shape_assignment: Dict[int, Dict],
    rows: int,
    cols: int,
) -> Grid:
    if not backgrounds:
        return _clone(grid)

    tile_h = backgrounds[0]["height"]
    tile_w = backgrounds[0]["width"]
    out_h = rows * tile_h
    out_w = cols * tile_w
    output = [[0 for _ in range(out_w)] for _ in range(out_h)]

    for idx, bg in enumerate(backgrounds):
        row_idx, col_idx = bg["grid_pos"]
        base_color = bg["color"]
        top = row_idx * tile_h
        left = col_idx * tile_w

        # Fill tile with background color
        for rr in range(tile_h):
            for cc in range(tile_w):
                output[top + rr][left + cc] = base_color

        shape = shape_assignment[idx]
        pattern = _extract_shape_pattern(grid, shape)
        sh = len(pattern)
        sw = len(pattern[0])
        margin_r = (tile_h - sh) // 2
        margin_c = (tile_w - sw) // 2

        for sr in range(sh):
            for sc in range(sw):
                if pattern[sr][sc] == shape["color"]:
                    output[top + margin_r + sr][left + margin_c + sc] = shape["color"]

    return output


def solve_8698868d(grid: Grid) -> Grid:
    """Task-specific transformation (work-in-progress)."""
    base_color = _most_common_color(grid)
    components = _extract_components(grid, ignore=[base_color])
    backgrounds, shapes = _classify_components(components)

    # Guard: ensure consistent tile sizes
    if not backgrounds or len(backgrounds) != len(shapes):
        return _clone(grid)

    grouped_backgrounds, rows, cols = _group_backgrounds(backgrounds)
    assignment = _assign_shapes(grouped_backgrounds, shapes)
    return _render_solution(grid, grouped_backgrounds, assignment, rows, cols)


p = solve_8698868d
