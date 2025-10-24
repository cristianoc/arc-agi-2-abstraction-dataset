"""Solver for task cb2d8a2c."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

Grid = List[List[int]]


def copy_grid(grid):
    return [row[:] for row in grid]


def transpose(grid):
    return [list(col) for col in zip(*grid)]


def get_components(grid):
    h = len(grid)
    w = len(grid[0])
    seen = [[False] * w for _ in range(h)]
    comps = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] not in (1, 2) or seen[r][c]:
                continue
            stack = [(r, c)]
            seen[r][c] = True
            rows = set()
            cols = set()
            while stack:
                rr, cc = stack.pop()
                rows.add(rr)
                cols.add(cc)
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc] and grid[nr][nc] in (1, 2):
                        seen[nr][nc] = True
                        stack.append((nr, nc))
            comps.append((rows, cols))
    return comps


def list_obstacles(grid):
    obstacles = []
    for r, row in enumerate(grid):
        cols = [c for c, val in enumerate(row) if val in (1, 2)]
        if cols:
            obstacles.append((r, min(cols), max(cols)))
    return obstacles


def derive_segments(grid, left_col, right_col, mode):
    h = len(grid)
    w = len(grid[0])
    anchor_row, anchor_col = next((r, c) for r in range(h) for c in range(w) if grid[r][c] == 3)
    obstacles = list_obstacles(grid)
    segments = []
    current_col = anchor_col
    prev_row = anchor_row
    for row, lo, hi in obstacles:
        if not (lo <= current_col <= hi):
            prev_row = row
            continue
        diff = row - prev_row
        if diff <= 1:
            change = prev_row + 1 if prev_row + 1 < row else prev_row
        else:
            if mode == "horizontal":
                change = prev_row + diff // 2
                if diff % 2 == 1:
                    change -= 1
            else:  # vertical (handled on transposed grid)
                width = hi - lo + 1
                addition = max(0, diff - width) + (1 if diff % 2 == 0 else 0)
                change = prev_row + diff // 2 + addition
            if change <= prev_row:
                change = prev_row + 1
            if change >= row:
                change = row - 1
        target_col = right_col if not (lo <= right_col <= hi) else left_col
        segments.append((change, current_col, target_col))
        current_col = target_col
        prev_row = row
    return segments, anchor_row, anchor_col


def draw_path(grid, segments, anchor_row, anchor_col, extend_downward):
    h = len(grid)
    w = len(grid[0])
    path = set()
    current_row = anchor_row
    current_col = anchor_col
    path.add((current_row, current_col))
    for row, start_col, target_col in segments:
        if row != current_row:
            step = 1 if row > current_row else -1
            for r in range(current_row + step, row + step, step):
                path.add((r, current_col))
            current_row = row
        if target_col != current_col:
            step = 1 if target_col > current_col else -1
            for c in range(current_col, target_col + step, step):
                path.add((current_row, c))
            current_col = target_col
        else:
            path.add((current_row, current_col))
    if extend_downward:
        for r in range(current_row + 1, h):
            path.add((r, current_col))
    else:
        for r in range(current_row - 1, -1, -1):
            path.add((r, current_col))
    return path


def render_path(grid):
    comps = get_components(grid)
    horizontal = all(len(rows) == 1 for rows, _ in comps) if comps else True

    if horizontal:
        obstacles = list_obstacles(grid)
        if obstacles:
            min_col = min(lo for _, lo, _ in obstacles)
            left = max(1, min_col - 5)
            right = min(len(grid[0]) - 1, left + 7)
            segments, anchor_row, anchor_col = derive_segments(grid, left, right, "horizontal")
            path = draw_path(grid, segments, anchor_row, anchor_col, extend_downward=True)
        else:
            anchor_row, anchor_col = next((r, c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] == 3)
            path = {(r, anchor_col) for r in range(anchor_row, len(grid))}
    else:
        tgrid = transpose(grid)
        anchor_row, anchor_col = next((r, c) for r in range(len(tgrid)) for c in range(len(tgrid[0])) if tgrid[r][c] == 3)
        left = anchor_col
        right = min(len(tgrid[0]) - 1, 8)
        segments, t_anchor_row, t_anchor_col = derive_segments(tgrid, left, right, "vertical")
        t_path = draw_path(tgrid, segments, t_anchor_row, t_anchor_col, extend_downward=True)
        path = {(c, r) for r, c in t_path}

    out = copy_grid(grid)
    for r, row in enumerate(out):
        for c, val in enumerate(row):
            if val == 1:
                out[r][c] = 2
    for r, c in path:
        out[r][c] = 3
    return out

# --- DSL-aligned wrappers (pure, used by the typed lambda) ---

def classifyCorridorOrientation(grid: Grid) -> str:
    comps = get_components(grid)
    horizontal = all(len(rows) == 1 for rows, _ in comps) if comps else True
    return "horizontal" if horizontal else "vertical"


def paint_path(grid: Grid, path: Iterable[Tuple[int, int]]) -> Grid:
    out = copy_grid(grid)
    for r, row in enumerate(out):
        for c, val in enumerate(row):
            if val == 1:
                out[r][c] = 2
    for r, c in path:
        out[r][c] = 3
    return out


def buildHorizontalCorridor(grid: Grid) -> Iterable[Tuple[int, int]]:
    obstacles = list_obstacles(grid)
    if not obstacles:
        anchor_row, anchor_col = next(
            (r, c)
            for r in range(len(grid))
            for c in range(len(grid[0]))
            if grid[r][c] == 3
        )
        return {(r, anchor_col) for r in range(anchor_row, len(grid))}
    min_col = min(lo for _, lo, _ in obstacles)
    left = max(1, min_col - 5)
    right = min(len(grid[0]) - 1, left + 7)
    segments, anchor_row, anchor_col = derive_segments(grid, left, right, "horizontal")
    return draw_path(grid, segments, anchor_row, anchor_col, extend_downward=True)


def buildVerticalCorridor(grid: Grid) -> Iterable[Tuple[int, int]]:
    tgrid = transpose(grid)
    anchor_row, anchor_col = next(
        (r, c)
        for r in range(len(tgrid))
        for c in range(len(tgrid[0]))
        if tgrid[r][c] == 3
    )
    left = anchor_col
    right = min(len(tgrid[0]) - 1, 8)
    segments, t_anchor_row, t_anchor_col = derive_segments(tgrid, left, right, "vertical")
    t_path = draw_path(tgrid, segments, t_anchor_row, t_anchor_col, extend_downward=True)
    return {(c, r) for r, c in t_path}


def renderCorridorPath(grid: Grid, path: Iterable[Tuple[int, int]]) -> Grid:
    return paint_path(grid, path)


def solve_cb2d8a2c(grid: Grid) -> Grid:
    orientation = classifyCorridorOrientation(grid)
    path = buildHorizontalCorridor(grid) if orientation == "horizontal" else buildVerticalCorridor(grid)
    return renderCorridorPath(grid, path)


p = solve_cb2d8a2c
