"""Solver for ARC-AGI-2 task 67e490f4 (evaluation split)."""

from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Sequence, Tuple

Grid = List[List[int]]
Coordinate = Tuple[int, int]


def _canonical_shape(cells: Sequence[Coordinate]) -> Tuple[Coordinate, ...]:
    """Return a translation-invariant encoding of a connected component."""
    min_r = min(r for r, _ in cells)
    min_c = min(c for _, c in cells)
    return tuple(sorted((r - min_r, c - min_c) for r, c in cells))


def _component_cells(
    grid: Grid,
    target: int,
    rows: range,
    cols: range,
    skip: Iterable[Coordinate] = (),
) -> List[List[Coordinate]]:
    """Collect 4-connected components of `target` within the given window."""
    height = len(rows)
    width = len(cols)
    index_by_coord = {(r, c): (ri, ci) for ri, r in enumerate(rows) for ci, c in enumerate(cols)}
    skipped = {index_by_coord[coord] for coord in skip if coord in index_by_coord}
    seen = [[False] * width for _ in range(height)]
    for ri, ci in skipped:
        seen[ri][ci] = True
    components: List[List[Coordinate]] = []
    for ri, r in enumerate(rows):
        for ci, c in enumerate(cols):
            if seen[ri][ci] or grid[r][c] != target:
                continue
            stack = [(ri, ci)]
            seen[ri][ci] = True
            cells: List[Coordinate] = []
            while stack:
                cr, cc = stack.pop()
                cells.append((rows[cr], cols[cc]))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not seen[nr][nc]:
                        if grid[rows[nr]][cols[nc]] == target:
                            seen[nr][nc] = True
                            stack.append((nr, nc))
            components.append(cells)
    return components


def _find_pattern_square(grid: Grid) -> Tuple[int, int, int, int, int]:
    """Locate the square window that hosts the canonical two-colour motif."""
    height = len(grid)
    width = len(grid[0])
    for size in range(min(height, width), 4, -1):
        row_range = range(height - size + 1)
        col_range = range(width - size + 1)
        for r0 in row_range:
            for c0 in col_range:
                rows = range(r0, r0 + size)
                cols = range(c0, c0 + size)
                entries = [grid[r][c] for r in rows for c in cols]
                palette = set(entries)
                if len(palette) != 2:
                    continue
                counts = Counter(entries)
                bg_colour, _ = counts.most_common(1)[0]
                pattern_colour = next(col for col in palette if col != bg_colour)
                components = _component_cells(grid, pattern_colour, rows, cols)
                if len(components) < 4:
                    continue
                largest = max(len(comp) for comp in components)
                if largest <= size - 1:
                    return size, r0, c0, bg_colour, pattern_colour
    raise ValueError("Unable to locate motif square")


def solve_67e490f4(grid: Grid) -> Grid:
    """Solve ARC task 67e490f4."""
    size, r0, c0, bg_colour, pattern_colour = _find_pattern_square(grid)
    rows = range(r0, r0 + size)
    cols = range(c0, c0 + size)

    # Catalogue small connected shapes outside the motif square.
    max_shape_size = max(9, size)
    shape_candidates: Dict[Tuple[Coordinate, ...], Counter] = defaultdict(Counter)
    visited = [[False] * len(grid[0]) for _ in grid]
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if r0 <= r < r0 + size and c0 <= c < c0 + size:
                continue
            if visited[r][c]:
                continue
            colour = grid[r][c]
            stack = [(r, c)]
            visited[r][c] = True
            cells: List[Coordinate] = []
            while stack:
                cr, cc = stack.pop()
                cells.append((cr, cc))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and not visited[nr][nc]:
                        if r0 <= nr < r0 + size and c0 <= nc < c0 + size:
                            continue
                        if grid[nr][nc] == colour:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
            if len(cells) <= max_shape_size:
                shape = _canonical_shape(cells)
                shape_candidates[shape][colour] += 1

    # Extract the motif components within the square.
    components = _component_cells(grid, pattern_colour, rows, cols)
    centre_r = (size - 1) / 2
    centre_c = (size - 1) / 2
    outer_level = 0.0
    comp_info = []
    for cells in components:
        local_cells = [(r - r0, c - c0) for r, c in cells]
        shape = _canonical_shape(local_cells)
        avg_r = sum(r for r, _ in local_cells) / len(local_cells)
        avg_c = sum(c for _, c in local_cells) / len(local_cells)
        abs_dr = abs(avg_r - centre_r)
        abs_dc = abs(avg_c - centre_c)
        max_abs = max(abs_dr, abs_dc)
        outer_level = max(outer_level, max_abs)
        comp_info.append(
            {
                "cells": local_cells,
                "shape": shape,
                "abs_dr": abs_dr,
                "abs_dc": abs_dc,
                "max_abs": max_abs,
            }
        )

    # Assign semantic categories (corner / edge / ring / centre).
    for info in comp_info:
        abs_dr = info["abs_dr"]
        abs_dc = info["abs_dc"]
        max_abs = info["max_abs"]
        min_abs = min(abs_dr, abs_dc)
        if max_abs < 0.5:
            category = "center"
        elif min_abs < 0.5:
            category = "edge"
        elif max_abs > outer_level - 0.5:
            category = "corner"
        else:
            category = "ring"
        info["category"] = category

    # Pick a colour for each category by matching component shapes seen elsewhere.
    category_colours: Dict[str, int] = {}
    for category in ("corner", "edge", "ring", "center"):
        relevant = [info for info in comp_info if info["category"] == category]
        if not relevant:
            continue
        aggregate = Counter()
        for info in relevant:
            aggregate += shape_candidates.get(info["shape"], Counter())
        for forbidden in (bg_colour, pattern_colour):
            if forbidden in aggregate:
                del aggregate[forbidden]
        if aggregate:
            chosen = max(aggregate.items(), key=lambda kv: (kv[1], kv[0]))[0]
        else:
            chosen = pattern_colour
        category_colours[category] = chosen

    # Paint the solution grid using the inferred palette.
    output = [[bg_colour] * size for _ in range(size)]
    for info in comp_info:
        colour = category_colours.get(info["category"], pattern_colour)
        for dr, dc in info["cells"]:
            output[dr][dc] = colour
    return output


p = solve_67e490f4
