"""Solver for ARC-AGI-2 task f560132c."""

def solve_f560132c(grid):
    """Rebuild the scene by remapping and reorienting its four components."""

    height = len(grid)
    width = len(grid[0])

    def get_components():
        seen = [[False] * width for _ in range(height)]
        components = []
        for r in range(height):
            for c in range(width):
                if grid[r][c] == 0 or seen[r][c]:
                    continue
                stack = [(r, c)]
                seen[r][c] = True
                cells = []
                while stack:
                    cr, cc = stack.pop()
                    cells.append((cr, cc))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < height and 0 <= nc < width:
                            if grid[nr][nc] != 0 and not seen[nr][nc]:
                                seen[nr][nc] = True
                                stack.append((nr, nc))
                rows = [rr for rr, _ in cells]
                cols = [cc for _, cc in cells]
                size = len(cells)
                centroid = (sum(rows) / size, sum(cols) / size)
                components.append({
                    "cells": cells,
                    "size": size,
                    "centroid": centroid,
                })
        return components

    def trimmed_mask(cells):
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        r0, r1 = min(rows), max(rows)
        c0, c1 = min(cols), max(cols)
        mask = [[0] * (c1 - c0 + 1) for _ in range(r1 - r0 + 1)]
        for r, c in cells:
            mask[r - r0][c - c0] = 1

        while mask and all(val == 0 for val in mask[0]):
            mask.pop(0)
        while mask and all(val == 0 for val in mask[-1]):
            mask.pop()
        if mask:
            while all(row[0] == 0 for row in mask):
                for row in mask:
                    row.pop(0)
            while all(row[-1] == 0 for row in mask):
                for row in mask:
                    row.pop()
        return mask

    def rotate_mask(mask, times):
        times %= 4
        rotated = [row[:] for row in mask]
        for _ in range(times):
            rotated = [list(row) for row in zip(*rotated[::-1])]
        return rotated

    components = get_components()

    counts = {}
    for row in grid:
        for val in row:
            if val:
                counts[val] = counts.get(val, 0) + 1
    palette = [colour for colour, cnt in counts.items() if cnt == 1]
    palette_cells = [(r, c) for r in range(height) for c in range(width)
                     if grid[r][c] in palette]

    def contains_all(comp, coords):
        cell_set = set(comp["cells"])
        return all(cell in cell_set for cell in coords)

    comp_a = next(comp for comp in components if contains_all(comp, palette_cells))
    px, py = comp_a["centroid"]
    others = [comp for comp in components if comp is not comp_a]
    for comp in others:
        cy, cx = comp["centroid"]
        comp["dy"] = cy - px
        comp["dx"] = cx - py

    comp_d = min(others, key=lambda comp: (comp["dx"], comp["dy"]))
    remaining = [comp for comp in others if comp is not comp_d]
    negative_dy = [comp for comp in remaining if comp["dy"] < 0]
    if negative_dy:
        comp_c = min(negative_dy, key=lambda comp: comp["dy"])
    else:
        comp_c = max(remaining, key=lambda comp: comp["dy"])
    comp_b = next(comp for comp in remaining if comp is not comp_c)

    mapping = {"a": comp_a, "b": comp_b, "c": comp_c, "d": comp_d}

    rotations = {
        "a": 0,
        "b": 3,
        "c": 2 if comp_c["dy"] < 0 else 1,
        "d": 1 if comp_d["dx"] < 0 else 2,
    }

    min_row = min(r for r, _ in palette_cells)
    min_col = min(c for _, c in palette_cells)
    block = [[None, None], [None, None]]
    for r, c in palette_cells:
        block[r - min_row][c - min_col] = grid[r][c]
    colours = {
        "a": block[0][0],
        "b": block[0][1],
        "c": block[1][0],
        "d": block[1][1],
    }

    masks = {}
    dims = {}
    for key in "abcd":
        mask = trimmed_mask(mapping[key]["cells"])
        rotated = rotate_mask(mask, rotations[key])
        masks[key] = rotated
        dims[key] = (len(rotated), len(rotated[0]))

    out_h = min(dims["a"][0] + dims["c"][0], dims["b"][0] + dims["d"][0])
    out_w = min(dims["a"][1] + dims["b"][1], dims["c"][1] + dims["d"][1])
    canvas = [[0] * out_w for _ in range(out_h)]

    placements = {
        "a": (0, 0),
        "b": (0, out_w - dims["b"][1]),
        "c": (out_h - dims["c"][0], 0),
        "d": (out_h - dims["d"][0], out_w - dims["d"][1]),
    }

    for key in "abcd":
        start_r, start_c = placements[key]
        colour = colours[key]
        mask = masks[key]
        for r, row in enumerate(mask):
            for c, value in enumerate(row):
                if value:
                    canvas[start_r + r][start_c + c] = colour

    return canvas


p = solve_f560132c
