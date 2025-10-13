"""Solver for ARC-AGI-2 task db0c5428."""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Tuple

Grid = List[List[int]]
Block = List[List[int]]


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _most_common_color(grid: Grid) -> int:
    counts: Counter[int] = Counter(value for row in grid for value in row)
    return counts.most_common(1)[0][0]


def _bounding_box(grid: Grid, background: int) -> Optional[Tuple[int, int, int, int]]:
    coords = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value != background]
    if not coords:
        return None
    rows, cols = zip(*coords)
    return min(rows), max(rows), min(cols), max(cols)


def _extract_blocks(grid: Grid, top: int, left: int) -> Dict[Tuple[int, int], Block]:
    blocks: Dict[Tuple[int, int], Block] = {}
    for br in range(3):
        for bc in range(3):
            rows = grid[top + br * 3 : top + (br + 1) * 3]
            block = [row[left + bc * 3 : left + (bc + 1) * 3] for row in rows]
            blocks[(br, bc)] = [row[:] for row in block]
    return blocks


def _map_macro_index(mr: int, mc: int) -> Optional[Tuple[int, int]]:
    even_map = {0: 2, 2: 1, 4: 0}

    if (mr, mc) == (2, 2):
        return None
    if mr in {0, 4} and mc in {1, 3}:
        return (1, 1)
    if mc in {0, 4} and mr in {1, 3}:
        return (1, 1)
    if mr % 2 == 0 and mc % 2 == 0:
        return (even_map[mr], even_map[mc])
    if mr % 2 == 1 and mc % 2 == 1:
        return (2 * ((mr - 1) // 2), 2 * ((mc - 1) // 2))
    if mr % 2 == 1 and mc % 2 == 0:
        if mc in {0, 4}:
            return (1, 1)
        return (2 * ((mr - 1) // 2), even_map[mc])
    if mr in {0, 4}:
        return (1, 1)
    return (even_map[mr], 2 * ((mc - 1) // 2))


def _build_center_block(
    blocks: Dict[Tuple[int, int], Block],
    background: int,
    corner_color: int,
    edge_color: int,
) -> Block:
    counts: Counter[int] = Counter()
    for block in blocks.values():
        for row in block:
            for value in row:
                if value != background:
                    counts[value] += 1
    dominant_color = edge_color if not counts else counts.most_common(1)[0][0]

    return [
        [corner_color, edge_color, corner_color],
        [edge_color, dominant_color, edge_color],
        [corner_color, edge_color, corner_color],
    ]


def solve_db0c5428(grid: Grid) -> Grid:
    background = _most_common_color(grid)
    bbox = _bounding_box(grid, background)
    if bbox is None:
        return _copy_grid(grid)

    r0, r1, c0, c1 = bbox
    if (r1 - r0 + 1) != 9 or (c1 - c0 + 1) != 9:
        return _copy_grid(grid)

    blocks = _extract_blocks(grid, r0, c0)

    corner_positions = [
        grid[r0 + 2][c0 + 2],
        grid[r0 + 2][c0 + 6],
        grid[r0 + 6][c0 + 2],
        grid[r0 + 6][c0 + 6],
    ]
    corner_color = corner_positions[0]
    if not all(color == corner_color for color in corner_positions):
        corner_color = max(set(corner_positions), key=corner_positions.count)

    edge_positions = [
        grid[r0 + 4][c0 + 2],
        grid[r0 + 4][c0 + 6],
        grid[r0 + 2][c0 + 4],
        grid[r0 + 6][c0 + 4],
    ]
    edge_color = edge_positions[0]
    if not all(color == edge_color for color in edge_positions):
        edge_color = max(set(edge_positions), key=edge_positions.count)

    center_block = _build_center_block(blocks, background, corner_color, edge_color)

    total_rows = len(grid)
    total_cols = len(grid[0]) if grid else 0
    start_r = r0 - 3
    start_c = c0 - 3
    if not (0 <= start_r and 0 <= start_c and start_r + 15 <= total_rows and start_c + 15 <= total_cols):
        return _copy_grid(grid)

    output = _copy_grid(grid)
    for mr in range(5):
        for mc in range(5):
            source = _map_macro_index(mr, mc)
            block = center_block if source is None else blocks[source]
            for r in range(3):
                dest_r = start_r + mr * 3 + r
                row_block = block[r]
                row_out = output[dest_r]
                for c in range(3):
                    dest_c = start_c + mc * 3 + c
                    row_out[dest_c] = row_block[c]

    return output


p = solve_db0c5428
