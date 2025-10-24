"""Solver for ARC-AGI-2 task 3dc255db (split: evaluation).

Refactored to the typed-DSL workflow using pure helpers and a
fold-repaint iteration in the main function, preserving original
behaviour.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Dict, Iterable, List, Sequence, Tuple


# --- Basic types ---
Grid = List[List[int]]
Component = Dict[str, Any]  # typed payload: host bbox/dims, colour, cells
Edge = Dict[str, str]  # {"axis": "horizontal|vertical", "direction": "east|west|north|south"}
Offset = Dict[str, float]  # {"drow": float, "dcol": float, "host_h": int, "host_w": int}


# --- Shared helpers (pure) ---
def _deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _nonzero_colors(grid: Grid) -> List[int]:
    return sorted({cell for row in grid for cell in row if cell})


def _bbox(coords: Sequence[Tuple[int, int]]) -> Tuple[int, int, int, int]:
    rows = [r for r, _ in coords]
    cols = [c for _, c in coords]
    return min(rows), max(rows), min(cols), max(cols)


def _components(grid: Grid, color: int) -> List[List[Tuple[int, int]]]:
    h = len(grid)
    w = len(grid[0])
    seen = set()
    comps: List[List[Tuple[int, int]]] = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] != color or (r, c) in seen:
                continue
            q = deque([(r, c)])
            seen.add((r, c))
            comp: List[Tuple[int, int]] = []
            while q:
                x, y = q.popleft()
                comp.append((x, y))
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w and grid[nx][ny] == color and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        q.append((nx, ny))
            comps.append(comp)
    return comps


def _collect_metadata(grid: Grid) -> Tuple[
    List[int],
    Dict[int, List[Tuple[int, int]]],
    Dict[int, Tuple[int, int, int, int]],
    Dict[int, int],
    Dict[int, List[List[Tuple[int, int]]]],
]:
    colors = _nonzero_colors(grid)
    color_cells = {
        color: [(r, c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] == color]
        for color in colors
    }
    bboxes = {color: _bbox(coords) for color, coords in color_cells.items()}
    areas = {color: len(coords) for color, coords in color_cells.items()}
    components = {color: _components(grid, color) for color in colors}
    return colors, color_cells, bboxes, areas, components


# --- DSL primitives ---
def fold_repaint(initial: Grid, items: List[Component], update: Any) -> Grid:
    g = _deep_copy(initial)
    for it in items:
        g = update(g, it)
    return g


def extractIntruders(grid: Grid) -> List[Component]:
    colors, _cells, bboxes, areas, components = _collect_metadata(grid)
    items: List[Component] = []
    processed: set = set()
    for host in colors:
        hr0, hr1, hc0, hc1 = bboxes[host]
        host_h = hr1 - hr0 + 1
        host_w = hc1 - hc0 + 1
        by_colour: Dict[int, List[Tuple[int, int]]] = {}
        for color in colors:
            if color == host or areas[host] <= areas[color]:
                continue
            for comp in components[color]:
                key = (color, tuple(sorted(comp)))
                if key in processed:
                    continue
                rows = [r for r, _ in comp]
                cols = [c for _, c in comp]
                cr0, cr1 = min(rows), max(rows)
                cc0, cc1 = min(cols), max(cols)
                if hr0 <= cr0 and cr1 <= hr1 and hc0 <= cc0 and cc1 <= hc1:
                    by_colour.setdefault(color, []).extend(comp)
                    processed.add(key)
        for color, cells in by_colour.items():
            if cells:
                items.append(
                    {
                        "host_bbox": (hr0, hr1, hc0, hc1),
                        "host_dims": (host_h, host_w),
                        "color": color,
                        "cells": cells,
                    }
                )
    return items


def computeDrift(component: Component) -> Offset:
    hr0, hr1, hc0, hc1 = component["host_bbox"]
    host_h, host_w = component["host_dims"]
    cells: List[Tuple[int, int]] = component["cells"]
    avg_row = sum(r for r, _ in cells) / len(cells)
    avg_col = sum(c for _, c in cells) / len(cells)
    center_row = (hr0 + hr1) / 2
    center_col = (hc0 + hc1) / 2
    return {"drow": avg_row - center_row, "dcol": avg_col - center_col, "host_h": host_h, "host_w": host_w}


def chooseTargetEdge(drift: Offset) -> Edge:
    abs_row = abs(drift["drow"])
    abs_col = abs(drift["dcol"])
    host_h = drift["host_h"]
    host_w = drift["host_w"]
    if abs_col > abs_row:
        axis = "horizontal"
    elif abs_col < abs_row:
        axis = "vertical"
    else:
        axis = "horizontal" if host_w >= host_h else "vertical"
    if axis == "horizontal":
        direction = "east" if drift["dcol"] < 0 else "west"
    else:
        direction = "north" if drift["drow"] > 0 else "south"
    return {"axis": axis, "direction": direction}


def _place_horizontal(canvas: Grid, comp: Component, direction: str) -> Grid:
    hr0, hr1, hc0, hc1 = comp["host_bbox"]
    host_h, _host_w = comp["host_dims"]
    color: int = comp["color"]
    cells: List[Tuple[int, int]] = comp["cells"]
    h = len(canvas)
    w = len(canvas[0])
    out = _deep_copy(canvas)
    for r, c in cells:
        out[r][c] = 0
    unique_cols = sorted({c for _, c in cells})
    length = len(unique_cols)
    if length == 0:
        return out
    row_line = hr1 - 1 if host_h > 1 else hr1
    row_line = max(hr0, min(hr1, row_line))
    if direction == "east":
        start_col = hc1 + 1
        for idx in range(length):
            col = start_col + idx
            if 0 <= col < w:
                out[row_line][col] = color
    else:
        start_col = hc0 - length
        for idx in range(length):
            col = start_col + idx
            if 0 <= col < w:
                out[row_line][col] = color
    return out


def _place_vertical(canvas: Grid, comp: Component, direction: str) -> Grid:
    hr0, hr1, hc0, hc1 = comp["host_bbox"]
    color: int = comp["color"]
    cells: List[Tuple[int, int]] = comp["cells"]
    h = len(canvas)
    _w = len(canvas[0])
    out = _deep_copy(canvas)
    for r, c in cells:
        out[r][c] = 0
    unique_rows = sorted({r for r, _ in cells})
    length = len(unique_rows)
    if length == 0:
        return out
    sorted_cols = sorted(c for _, c in cells)
    col_line = sorted_cols[len(sorted_cols) // 2]
    col_line = max(hc0, min(hc1, col_line))
    if direction == "north":
        start_row = hr0 - length
        for idx in range(length):
            row = start_row + idx
            if 0 <= row < h:
                out[row][col_line] = color
    else:
        start_row = hr1 + 1
        for idx in range(length):
            row = start_row + idx
            if 0 <= row < h:
                out[row][col_line] = color
    return out


def pushComponent(canvas: Grid, component: Component, edge: Edge) -> Grid:
    if edge["axis"] == "horizontal":
        return _place_horizontal(canvas, component, edge["direction"])
    return _place_vertical(canvas, component, edge["direction"])


# --- Main function (must match abstractions.md exactly) ---
def solve_3dc255db(grid: Grid) -> Grid:
    intruders = extractIntruders(grid)
    
    def push(canvas: Grid, component: Component) -> Grid:
        drift = computeDrift(component)
        edge = chooseTargetEdge(drift)
        return pushComponent(canvas, component, edge)
    
    return fold_repaint(grid, intruders, push)


p = solve_3dc255db
