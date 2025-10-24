"""Solver for ARC-AGI-2 task bf45cf4b (DSL-aligned composition)."""

from collections import Counter
from typing import List, Tuple


Grid = List[List[int]]
Component = List[Tuple[int, int]]
GridBool = List[List[bool]]
Color = int


def _extract_components(grid: Grid, background: int) -> List[Component]:
    """Return 4-connected components of non-background cells."""

    height, width = len(grid), len(grid[0])
    seen = [[False] * width for _ in range(height)]
    components: List[Component] = []

    for r in range(height):
        for c in range(width):
            if grid[r][c] == background or seen[r][c]:
                continue
            queue = [(r, c)]
            seen[r][c] = True
            cells: Component = []

            while queue:
                rr, cc = queue.pop()
                cells.append((rr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width:
                        if grid[nr][nc] != background and not seen[nr][nc]:
                            seen[nr][nc] = True
                            queue.append((nr, nc))

            components.append(cells)

    return components


def _bounding_box(cells: Component) -> Tuple[int, int, int, int]:
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    return min(rows), max(rows), min(cols), max(cols)


# === DSL helper primitives (pure) ===

def majorityColor(grid: Grid) -> Color:
    return Counter(cell for row in grid for cell in row).most_common(1)[0][0]


def extractComponents(grid: Grid) -> Tuple[Component, Component]:
    background = majorityColor(grid)
    components = _extract_components(grid, background)

    pattern_cells: Component = []
    for cells in components:
        colors = {grid[r][c] for r, c in cells}
        if len(colors) > 1:
            pattern_cells = cells
            break

    # Fallback to identity if no clear split.
    if not pattern_cells:
        return ([], [])

    mask_cells: Component = [cell for cells in components if cells is not pattern_cells for cell in cells]
    return mask_cells, pattern_cells


def computeMaskLayout(mask_component: Component) -> GridBool:
    if not mask_component:
        return []
    r0, r1, c0, c1 = _bounding_box(mask_component)
    h, w = r1 - r0 + 1, c1 - c0 + 1
    layout = [[False] * w for _ in range(h)]
    for r, c in mask_component:
        layout[r - r0][c - c0] = True
    return layout


def extractPatternTile(grid: Grid, pattern_component: Component) -> Grid:
    if not pattern_component:
        return [row[:] for row in grid]
    r0, r1, c0, c1 = _bounding_box(pattern_component)
    return [row[c0 : c1 + 1] for row in grid[r0 : r1 + 1]]


def tilePatternByMask(mask_layout: GridBool, pattern_tile: Grid, background: Color) -> Grid:
    if not mask_layout:
        return [row[:] for row in pattern_tile]

    tile_h, tile_w = len(pattern_tile), len(pattern_tile[0])
    mask_h, mask_w = len(mask_layout), len(mask_layout[0])

    out_h, out_w = mask_h * tile_h, mask_w * tile_w
    output: Grid = [[background] * out_w for _ in range(out_h)]

    background_tile = [[background] * tile_w for _ in range(tile_h)]
    for mr in range(mask_h):
        for mc in range(mask_w):
            tile = pattern_tile if mask_layout[mr][mc] else background_tile
            base_r, base_c = mr * tile_h, mc * tile_w
            for tr in range(tile_h):
                output[base_r + tr][base_c : base_c + tile_w] = tile[tr][:]
    return output


def solve_bf45cf4b(grid: Grid) -> Grid:
    mask_component, pattern_component = extractComponents(grid)
    mask_layout = computeMaskLayout(mask_component)
    pattern_tile = extractPatternTile(grid, pattern_component)
    background = majorityColor(grid)
    return tilePatternByMask(mask_layout, pattern_tile, background)


p = solve_bf45cf4b
