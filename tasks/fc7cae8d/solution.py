"""Solver for ARC-AGI-2 task fc7cae8d (split: evaluation)."""

from collections import deque


def _largest_component(grid):
    """Return the largest color component, preferring ones away from the border."""
    height = len(grid)
    width = len(grid[0])
    visited = [[False] * width for _ in range(height)]

    best_interior = None
    best_any = None

    for r in range(height):
        for c in range(width):
            if visited[r][c]:
                continue
            color = grid[r][c]
            queue = deque([(r, c)])
            visited[r][c] = True
            cells = []
            touches_border = False

            while queue:
                rr, cc = queue.popleft()
                cells.append((rr, cc))
                if rr in (0, height - 1) or cc in (0, width - 1):
                    touches_border = True
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width:
                        if not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            queue.append((nr, nc))

            component = {
                "color": color,
                "cells": cells,
                "touches_border": touches_border,
            }

            if best_any is None or len(cells) > len(best_any["cells"]):
                best_any = component
            if not touches_border:
                if best_interior is None or len(cells) > len(best_interior["cells"]):
                    best_interior = component

    return best_interior or best_any


def _rotate_ccw(grid):
    return [list(row) for row in zip(*grid)][::-1]


def _maybe_flip_horizontal(grid, dominant_color):
    left_column = [row[0] for row in grid]
    right_column = [row[-1] for row in grid]

    left_primary = sum(1 for val in left_column if val == dominant_color)
    right_primary = sum(1 for val in right_column if val == dominant_color)
    left_impurity = len(left_column) - left_primary
    right_impurity = len(right_column) - right_primary

    left_score = (left_primary, -left_impurity)
    right_score = (right_primary, -right_impurity)

    if left_score < right_score:
        return [list(reversed(row)) for row in grid]
    return grid


def solve_fc7cae8d(grid):
    component = _largest_component(grid)
    cells = component["cells"]
    color = component["color"]
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    r0, r1 = min(rows), max(rows)
    c0, c1 = min(cols), max(cols)

    cropped = [row[c0 : c1 + 1] for row in grid[r0 : r1 + 1]]
    rotated = _rotate_ccw(cropped)
    adjusted = _maybe_flip_horizontal(rotated, color)
    return adjusted


p = solve_fc7cae8d
