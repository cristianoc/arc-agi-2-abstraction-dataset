"""Solution for ARC-AGI-2 task 7ed72f31 (evaluation split)."""

from collections import Counter, deque


def solve_7ed72f31(grid):
    """Reflect non-axis objects across the symmetry axes marked in color 2."""
    height, width = len(grid), len(grid[0])

    background = Counter(cell for row in grid for cell in row).most_common(1)[0][0]
    axes = []
    seen = [[False] * width for _ in range(height)]

    for y in range(height):
        for x in range(width):
            if grid[y][x] != 2 or seen[y][x]:
                continue
            queue = deque([(y, x)])
            seen[y][x] = True
            comp = []
            while queue:
                cy, cx = queue.popleft()
                comp.append((cy, cx))
                for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < height and 0 <= nx < width and not seen[ny][nx] and grid[ny][nx] == 2:
                        seen[ny][nx] = True
                        queue.append((ny, nx))

            rows = [p[0] for p in comp]
            cols = [p[1] for p in comp]
            min_r, max_r = min(rows), max(rows)
            min_c, max_c = min(cols), max(cols)
            unique_rows = len(set(rows))
            unique_cols = len(set(cols))

            if len(comp) == 1:
                axis_type = "point"
            elif unique_rows == 1 and unique_cols > 1:
                axis_type = "horizontal"
            elif unique_cols == 1 and unique_rows > 1:
                axis_type = "vertical"
            else:
                axis_type = "block"

            axes.append(
                {
                    "type": axis_type,
                    "cells": set(comp),
                    "min_r": min_r,
                    "max_r": max_r,
                    "min_c": min_c,
                    "max_c": max_c,
                    "center_r": (min_r + max_r) / 2,
                    "center_c": (min_c + max_c) / 2,
                }
            )

    def axis_applicable(axis, y, x):
        if (y, x) in axis["cells"]:
            return False
        atype = axis["type"]
        if atype == "vertical":
            return axis["min_r"] <= y <= axis["max_r"]
        if atype == "horizontal":
            return axis["min_c"] <= x <= axis["max_c"]
        if atype == "block":
            return axis["min_r"] <= y <= axis["max_r"] or axis["min_c"] <= x <= axis["max_c"]
        return True

    def reflect(axis, y, x):
        atype = axis["type"]
        cy = axis["center_r"]
        cx = axis["center_c"]
        if atype == "vertical":
            return y, int(round(2 * cx - x))
        if atype == "horizontal":
            return int(round(2 * cy - y)), x
        ny = int(round(2 * cy - y))
        nx = int(round(2 * cx - x))
        return ny, nx

    out = [row[:] for row in grid]
    original = [(y, x, grid[y][x]) for y in range(height) for x in range(width)]
    for y, x, val in original:
        if val == 2 or val == background:
            continue

        best_axis = None
        best_dist = None
        for axis in axes:
            if not axis_applicable(axis, y, x):
                continue
            atype = axis["type"]
            if atype == "vertical":
                distance = abs(x - axis["center_c"])
            elif atype == "horizontal":
                distance = abs(y - axis["center_r"])
            else:
                distance = abs(y - axis["center_r"]) + abs(x - axis["center_c"])

            if best_dist is None or distance < best_dist:
                best_dist = distance
                best_axis = axis

        if best_axis is None:
            continue

        ny, nx = reflect(best_axis, y, x)
        if 0 <= ny < height and 0 <= nx < width and out[ny][nx] == background:
            out[ny][nx] = val

    return out


p = solve_7ed72f31
