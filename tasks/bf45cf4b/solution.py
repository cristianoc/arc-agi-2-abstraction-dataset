"""Solver for ARC-AGI-2 task bf45cf4b."""

from collections import Counter
from typing import List, Tuple


Grid = List[List[int]]


def _extract_components(grid: Grid, background: int) -> List[List[Tuple[int, int]]]:
    """Return 4-connected components of non-background cells."""

    height, width = len(grid), len(grid[0])
    seen = [[False] * width for _ in range(height)]
    components: List[List[Tuple[int, int]]] = []

    for r in range(height):
        for c in range(width):
            if grid[r][c] == background or seen[r][c]:
                continue
            queue = [(r, c)]
            seen[r][c] = True
            cells: List[Tuple[int, int]] = []

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


def _bounding_box(cells: List[Tuple[int, int]]) -> Tuple[int, int, int, int]:
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    return min(rows), max(rows), min(cols), max(cols)


def solve_bf45cf4b(grid: Grid) -> Grid:
    """Tile the pattern component following the mask component's layout."""

    height, width = len(grid), len(grid[0])
    background = Counter(cell for row in grid for cell in row).most_common(1)[0][0]

    components = _extract_components(grid, background)

    pattern_cells: List[Tuple[int, int]] = []
    for cells in components:
        colors = {grid[r][c] for r, c in cells}
        if len(colors) > 1:
            pattern_cells = cells
            break

    if not pattern_cells:
        return [row[:] for row in grid]

    mask_cells = [cell for cells in components if cells is not pattern_cells for cell in cells]
    if not mask_cells:
        return [row[:] for row in grid]

    mask_r0, mask_r1, mask_c0, mask_c1 = _bounding_box(mask_cells)
    mask_height = mask_r1 - mask_r0 + 1
    mask_width = mask_c1 - mask_c0 + 1
    mask_layout = [[False] * mask_width for _ in range(mask_height)]
    for r, c in mask_cells:
        mask_layout[r - mask_r0][c - mask_c0] = True

    pat_r0, pat_r1, pat_c0, pat_c1 = _bounding_box(pattern_cells)
    pattern_tile = [row[pat_c0 : pat_c1 + 1] for row in grid[pat_r0 : pat_r1 + 1]]
    tile_height = len(pattern_tile)
    tile_width = len(pattern_tile[0])
    background_tile = [[background] * tile_width for _ in range(tile_height)]

    output_height = mask_height * tile_height
    output_width = mask_width * tile_width
    output: Grid = [[background] * output_width for _ in range(output_height)]

    for mr in range(mask_height):
        for mc in range(mask_width):
            tile = pattern_tile if mask_layout[mr][mc] else background_tile
            base_r = mr * tile_height
            base_c = mc * tile_width
            for tr in range(tile_height):
                output[base_r + tr][base_c : base_c + tile_width] = tile[tr][:]

    return output


p = solve_bf45cf4b
