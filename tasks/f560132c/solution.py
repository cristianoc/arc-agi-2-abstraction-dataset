"""Solver for ARC-AGI-2 task f560132c, refactored to align with DSL."""

from __future__ import annotations

from collections import Counter, deque
from typing import Dict, Iterable, List, Tuple, Any


Grid = List[List[int]]
Cell = Tuple[int, int]


class QuadrantPlan:
    def __init__(self, components: Dict[str, Dict[str, Any]], orientations: Dict[str, int], colours: Dict[str, int]):
        self.components = components
        self.orientations = orientations
        self.colours = colours


def extractComponents(grid: Grid) -> List[Dict[str, Any]]:
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    comps: List[Dict[str, Any]] = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 0 or seen[r][c]:
                continue
            stack = deque([(r, c)])
            seen[r][c] = True
            cells: List[Cell] = []
            cell_colors: Dict[Cell, int] = {}
            while stack:
                cr, cc = stack.pop()
                cells.append((cr, cc))
                cell_colors[(cr, cc)] = grid[cr][cc]
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc] and grid[nr][nc] != 0:
                        seen[nr][nc] = True
                        stack.append((nr, nc))
            rows = [rr for rr, _ in cells]
            cols = [cc for _, cc in cells]
            size = len(cells)
            centroid = (sum(rows) / size, sum(cols) / size)
            comps.append({
                "cells": cells,
                "cell_colors": cell_colors,
                "size": size,
                "centroid": centroid,
            })
    return comps


def _palette_from_components(components: List[Dict[str, Any]]) -> Tuple[List[int], List[Cell]]:
    counts = Counter(col for comp in components for col in comp["cell_colors"].values())
    palette = [val for val, cnt in counts.items() if cnt == 1]
    palette_cells: List[Cell] = [cell for comp in components for cell, col in comp["cell_colors"].items() if col in palette]
    return palette, palette_cells


def _contains_all_cells(comp: Dict[str, Any], coords: Iterable[Cell]) -> bool:
    cells = set(comp["cells"])
    return all(cell in cells for cell in coords)


def classifyQuadrants(components: List[Dict[str, Any]]) -> QuadrantPlan:
    palette, palette_cells = _palette_from_components(components)
    comp_a = next(comp for comp in components if _contains_all_cells(comp, palette_cells))

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
        comp_c = min(negative_dy, key=lambda comp: comp["dy"])  # most negative dy
    else:
        comp_c = max(remaining, key=lambda comp: comp["dy"])    # otherwise largest dy
    comp_b = next(comp for comp in remaining if comp is not comp_c)

    components_map = {"a": comp_a, "b": comp_b, "c": comp_c, "d": comp_d}

    rotations = {
        "a": 0,
        "b": 3,
        "c": 2 if comp_c["dy"] < 0 else 1,
        "d": 1 if comp_d["dx"] < 0 else 2,
    }

    min_row = min(r for r, _ in palette_cells)
    min_col = min(c for _, c in palette_cells)
    block: List[List[int]] = [[0, 0], [0, 0]]
    for r, c in palette_cells:
        # colour can be taken from any component holding this cell
        for comp in components:
            if (r, c) in comp["cell_colors"]:
                block[r - min_row][c - min_col] = comp["cell_colors"][(r, c)]
                break
    colours = {"a": block[0][0], "b": block[0][1], "c": block[1][0], "d": block[1][1]}

    return QuadrantPlan(components_map, rotations, colours)


def trimmed_mask(cells: List[Cell]) -> Grid:
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    r0, r1 = min(rows), max(rows)
    c0, c1 = min(cols), max(cols)
    mask = [[0] * (c1 - c0 + 1) for _ in range(r1 - r0 + 1)]
    for r, c in cells:
        mask[r - r0][c - c0] = 1
    return mask


def rotate_mask(mask: Grid, times: int) -> Grid:
    t = times % 4
    rotated = [row[:] for row in mask]
    for _ in range(t):
        rotated = [list(row) for row in zip(*rotated[::-1])]
    return rotated


def rotateComponentMask(plan: QuadrantPlan, label: str) -> Grid:
    comp = plan.components[label]
    mask = trimmed_mask(comp["cells"])  # type: ignore[index]
    return rotate_mask(mask, plan.orientations[label])


def composeCanvas(rotated_masks: Dict[str, Grid], colours: Dict[str, int]) -> Grid:
    dims: Dict[str, Tuple[int, int]] = {k: (len(v), len(v[0])) for k, v in rotated_masks.items()}
    out_h = min(dims["a"][0] + dims["c"][0], dims["b"][0] + dims["d"][0])
    out_w = min(dims["a"][1] + dims["b"][1], dims["c"][1] + dims["d"][1])
    canvas: Grid = [[0] * out_w for _ in range(out_h)]

    placements = {
        "a": (0, 0),
        "b": (0, out_w - dims["b"][1]),
        "c": (out_h - dims["c"][0], 0),
        "d": (out_h - dims["d"][0], out_w - dims["d"][1]),
    }

    for key in "abcd":
        sr, sc = placements[key]
        colour = colours[key]
        mask = rotated_masks[key]
        for r, row in enumerate(mask):
            for c, val in enumerate(row):
                if val:
                    canvas[sr + r][sc + c] = colour
    return canvas


# The main solver is intentionally identical to abstractions.md's Lambda Representation.
def solve_f560132c(grid: Grid) -> Grid:
    components = extractComponents(grid)
    plan = classifyQuadrants(components)
    rotated_masks = dict(
        (label, rotateComponentMask(plan, label))
        for label in plan.components
    )
    return composeCanvas(rotated_masks, plan.colours)


p = solve_f560132c
