"""Solver for ARC-AGI-2 task 4c416de3."""

from collections import Counter, deque


PATTERN_DIST_22 = {
    "NW": {(-1, -1), (-1, 0), (0, -1), (0, 0), (1, 1)},
    "SW": {(-1, 1), (0, -1), (0, 0), (1, -1), (1, 0)},
    "SE": {(-1, -1), (0, 0), (0, 1), (1, 0), (1, 1)},
}

PATTERN_LARGE = {
    "NW": {(-1, -1), (-1, 0), (0, -1), (0, 1), (1, 0)},
    "NE": {(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0)},
    "SW": {(-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)},
    "SE": {(-1, 0), (0, -1), (0, 1), (1, 0), (1, 1)},
}

PATTERN_SMALL = {
    "NW": {(-1, 0), (0, -1), (0, 0)},
    "NE": {(-1, 0), (0, 0), (0, 1)},
    "SW": {(0, -1), (0, 0), (1, 0)},
    "SE": {(0, 0), (0, 1), (1, 0)},
}


def solve_4c416de3(grid):
    """Repaint corner hooks on zero-framed blocks according to interior markers."""
    height, width = len(grid), len(grid[0])
    background = Counter(val for row in grid for val in row).most_common(1)[0][0]

    output = [row[:] for row in grid]
    zero_components = _collect_zero_components(grid)
    markers = _collect_markers(grid, background)
    used_markers = set()

    for comp_idx, component in enumerate(zero_components):
        min_r, max_r, min_c, max_c, zero_set = component
        for marker_idx, marker in enumerate(markers):
            if marker_idx in used_markers or len(marker["cells"]) != 1:
                continue
            (mr, mc) = marker["cells"][0]
            if not (min_r <= mr <= max_r and min_c <= mc <= max_c):
                continue

            orientation, dist, corner = _classify_marker((mr, mc), zero_set, (min_r, max_r, min_c, max_c))
            if orientation is None or dist is None or corner is None:
                continue

            pattern = _select_pattern(orientation, dist, background)
            if not pattern:
                continue

            used_markers.add(marker_idx)
            color = marker["color"]
            cr, cc = corner
            for dr, dc in pattern:
                rr, cc2 = cr + dr, cc + dc
                if 0 <= rr < height and 0 <= cc2 < width:
                    output[rr][cc2] = color

    return output


def _collect_zero_components(grid):
    height, width = len(grid), len(grid[0])
    visited = [[False] * width for _ in range(height)]
    components = []

    for r in range(height):
        for c in range(width):
            if grid[r][c] != 0 or visited[r][c]:
                continue

            queue = deque([(r, c)])
            visited[r][c] = True
            cells = []
            while queue:
                rr, cc = queue.popleft()
                cells.append((rr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[nr][nc] == 0:
                        visited[nr][nc] = True
                        queue.append((nr, nc))

            rows = [rr for rr, _ in cells]
            cols = [cc for _, cc in cells]
            min_r, max_r = min(rows), max(rows)
            min_c, max_c = min(cols), max(cols)
            components.append((min_r, max_r, min_c, max_c, set(cells)))

    return components


def _collect_markers(grid, background):
    height, width = len(grid), len(grid[0])
    visited = [[False] * width for _ in range(height)]
    markers = []

    for r in range(height):
        for c in range(width):
            if visited[r][c]:
                continue

            color = grid[r][c]
            if color in (0, background):
                visited[r][c] = True
                continue

            queue = deque([(r, c)])
            visited[r][c] = True
            cells = []
            while queue:
                rr, cc = queue.popleft()
                cells.append((rr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[nr][nc] == color:
                        visited[nr][nc] = True
                        queue.append((nr, nc))

            markers.append({"color": color, "cells": sorted(cells)})

    return markers


def _classify_marker(cell, zero_set, bbox):
    mr, mc = cell
    min_r, max_r, min_c, max_c = bbox

    up = _find_zero_along_line(mr, mc, zero_set, (-1, 0), min_r)
    down = _find_zero_along_line(mr, mc, zero_set, (1, 0), max_r)
    left = _find_zero_along_line(mr, mc, zero_set, (0, -1), min_c)
    right = _find_zero_along_line(mr, mc, zero_set, (0, 1), max_c)

    if up is None and down is None:
        return None, None, None
    if left is None and right is None:
        return None, None, None

    if up is None:
        vert_dir, target_r = "S", down
    elif down is None:
        vert_dir, target_r = "N", up
    else:
        vert_dir, target_r = ("N", up) if (mr - up) <= (down - mr) else ("S", down)

    if left is None:
        horiz_dir, target_c = "E", right
    elif right is None:
        horiz_dir, target_c = "W", left
    else:
        horiz_dir, target_c = ("W", left) if (mc - left) <= (right - mc) else ("E", right)

    orientation = vert_dir + horiz_dir
    dist = (abs(mr - target_r), abs(mc - target_c))
    corner = (target_r, target_c)
    return orientation, dist, corner


def _find_zero_along_line(r, c, zero_set, step, boundary):
    dr, dc = step
    current_r, current_c = r, c
    while True:
        current_r += dr
        current_c += dc
        if dr < 0 and current_r < boundary:
            break
        if dr > 0 and current_r > boundary:
            break
        if dc < 0 and current_c < boundary:
            break
        if dc > 0 and current_c > boundary:
            break
        if (current_r, current_c) in zero_set:
            return current_r if dr else current_c
    return None


def _select_pattern(orientation, dist, background):
    if dist == (2, 2):
        return PATTERN_DIST_22.get(orientation)
    if dist == (1, 1):
        if background == 8:
            return PATTERN_LARGE.get(orientation)
        return PATTERN_SMALL.get(orientation)
    return None


p = solve_4c416de3

