"""Solver for ARC-AGI-2 task 67e490f4 (evaluation split)."""

from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Sequence, Tuple, TypedDict

Grid = List[List[int]]
Coordinate = Tuple[int, int]


class ComponentInfo(TypedDict):
    cells: List[Coordinate]
    shape: Tuple[Coordinate, ...]
    category: str
    size: int
    pattern_colour: int


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


def locateTwoColourSquare(grid: Grid) -> Tuple[Tuple[int, int, int], int, int]:
    """Return (box, pattern_colour, bg_colour) for the target two-colour square.

    Box is a tuple (r0, c0, size).
    """
    size, r0, c0, bg_colour, pattern_colour = _find_pattern_square(grid)
    return (r0, c0, size), pattern_colour, bg_colour


def catalogueExternalShapes(
    grid: Grid, box: Tuple[int, int, int]
) -> Dict[Tuple[Coordinate, ...], Counter]:
    """Catalogue small connected shapes outside the motif square.

    Returns a mapping from canonical shape to a Counter of observed colours.
    """
    r0, c0, size = box
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
    return shape_candidates


def classifyMotifComponents(
    grid: Grid, box: Tuple[int, int, int], pattern_colour: int
) -> List[ComponentInfo]:
    """Extract and classify motif components within the square.

    Returns a list of component info dicts containing:
    - 'cells': List[Coordinate] in local box coords
    - 'shape': canonical shape signature
    - 'category': one of {'corner','edge','ring','center'}
    - 'size': int box size (for downstream reconstruction)
    - 'pattern_colour': int (for downstream exclusion/fallback)
    """
    r0, c0, size = box
    rows = range(r0, r0 + size)
    cols = range(c0, c0 + size)
    components = _component_cells(grid, pattern_colour, rows, cols)
    centre = (size - 1) / 2
    outer_level = 0.0
    comp_info: List[ComponentInfo] = []
    raw: List[Dict[str, float]] = []
    for cells in components:
        local_cells = [(r - r0, c - c0) for r, c in cells]
        shape = _canonical_shape(local_cells)
        avg_r = sum(r for r, _ in local_cells) / len(local_cells)
        avg_c = sum(c for _, c in local_cells) / len(local_cells)
        abs_dr = abs(avg_r - centre)
        abs_dc = abs(avg_c - centre)
        max_abs = max(abs_dr, abs_dc)
        outer_level = max(outer_level, max_abs)
        raw.append({"abs_dr": abs_dr, "abs_dc": abs_dc, "max_abs": max_abs})
        comp_info.append({"cells": local_cells, "shape": shape, "category": "", "size": size, "pattern_colour": pattern_colour})

    # Assign categories using computed distances.
    categorized: List[ComponentInfo] = []
    for base, dist in zip(comp_info, raw):
        abs_dr = dist["abs_dr"]
        abs_dc = dist["abs_dc"]
        max_abs = dist["max_abs"]
        min_abs = min(abs_dr, abs_dc)
        if max_abs < 0.5:
            category = "center"
        elif min_abs < 0.5:
            category = "edge"
        elif max_abs > outer_level - 0.5:
            category = "corner"
        else:
            category = "ring"
        base_update: ComponentInfo = {
            "cells": base["cells"],
            "shape": base["shape"],
            "category": category,
            "size": size,
            "pattern_colour": pattern_colour,
        }
        categorized.append(base_update)
    return categorized


def recolourMotif(
    motif_components: List[ComponentInfo],
    external_shapes: Dict[Tuple[Coordinate, ...], Counter],
    bg_colour: int,
) -> Grid:
    """Choose colours per category via external shape matches and repaint motif.

    Excludes both the background colour and the motif pattern colour from voting.
    """
    if not motif_components:
        return []

    size = motif_components[0]["size"]
    pattern_colour = motif_components[0]["pattern_colour"]

    # Build palette per category.
    category_colours: Dict[str, int] = {}
    for category in ("corner", "edge", "ring", "center"):
        relevant = [info for info in motif_components if info["category"] == category]
        if not relevant:
            continue
        aggregate: Counter = Counter()
        for info in relevant:
            shape = info["shape"]
            aggregate += external_shapes.get(shape, Counter())
        for forbidden in (bg_colour, pattern_colour):
            if forbidden in aggregate:
                del aggregate[forbidden]
        chosen = (
            max(aggregate.items(), key=lambda kv: (kv[1], kv[0]))[0]
            if aggregate
            else pattern_colour
        )
        category_colours[category] = int(chosen)

    # Paint output.
    output = [[bg_colour] * size for _ in range(size)]
    for info in motif_components:
        colour = category_colours.get(info["category"], pattern_colour)
        for dr, dc in info["cells"]:
            output[dr][dc] = colour
    return output


def solve_67e490f4(grid: Grid) -> Grid:
    box, color_a, color_b = locateTwoColourSquare(grid)
    external_shapes = catalogueExternalShapes(grid, box)
    motif_components = classifyMotifComponents(grid, box, color_a)
    return recolourMotif(motif_components, external_shapes, color_b)


p = solve_67e490f4
