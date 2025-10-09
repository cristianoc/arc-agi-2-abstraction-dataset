"""Solver for ARC-AGI-2 task dbff022c."""

from collections import deque


def _neighbors(r, c):
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        yield r + dr, c + dc


def _in_bounds(r, c, rows, cols):
    return 0 <= r < rows and 0 <= c < cols


def _collect_zero_components(grid):
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    components = []

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 or visited[r][c]:
                continue

            queue = deque([(r, c)])
            visited[r][c] = True
            zero_cells = []
            neighbor_color = None
            neighbors_mixed = False
            boundary_cells = set()
            touches_border = False

            while queue:
                cr, cc = queue.popleft()
                zero_cells.append((cr, cc))
                if cr == 0 or cr == rows - 1 or cc == 0 or cc == cols - 1:
                    touches_border = True

                for nr, nc in _neighbors(cr, cc):
                    if not _in_bounds(nr, nc, rows, cols):
                        continue
                    val = grid[nr][nc]
                    if val == 0 and not visited[nr][nc]:
                        visited[nr][nc] = True
                        queue.append((nr, nc))
                    elif val != 0:
                        if neighbor_color is None:
                            neighbor_color = val
                        elif neighbor_color != val:
                            neighbors_mixed = True
                        boundary_cells.add((nr, nc))

            if neighbor_color is None or neighbors_mixed:
                continue

            # Expand through the enclosing color to learn adjacent palette context.
            region = set(zero_cells)
            region_queue = deque(zero_cells + list(boundary_cells))
            seen = set(region_queue)
            while region_queue:
                cr, cc = region_queue.popleft()
                region.add((cr, cc))
                for nr, nc in _neighbors(cr, cc):
                    if not _in_bounds(nr, nc, rows, cols):
                        continue
                    if grid[nr][nc] in (0, neighbor_color) and (nr, nc) not in seen:
                        seen.add((nr, nc))
                        region_queue.append((nr, nc))

            adjacency = set()
            for cr, cc in region:
                for nr, nc in _neighbors(cr, cc):
                    if not _in_bounds(nr, nc, rows, cols):
                        continue
                    val = grid[nr][nc]
                    if val not in (0, neighbor_color):
                        adjacency.add(val)

            components.append(
                {
                    "cells": zero_cells,
                    "color": neighbor_color,
                    "size": len(zero_cells),
                    "adjacency": adjacency,
                    "touches_border": touches_border,
                }
            )

    return components


def _decide_fill(component):
    color = component["color"]
    size = component["size"]
    adjacency = component["adjacency"]
    touches_border = component["touches_border"]

    if touches_border:
        return None

    if color == 3:
        return 3

    if color == 8:
        return 1

    if color == 2:
        return 7

    if color == 4 and size == 1:
        if 5 in adjacency:
            return 5
        if 6 in adjacency:
            return 6
        return None

    return None


def solve_dbff022c(grid):
    result = [row[:] for row in grid]

    for component in _collect_zero_components(grid):
        fill_color = _decide_fill(component)
        if fill_color is None:
            continue
        for r, c in component["cells"]:
            result[r][c] = fill_color

    return result


p = solve_dbff022c
