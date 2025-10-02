"""Solver for ARC-AGI-2 task 195c6913 (split: evaluation)."""

from collections import deque
from typing import Dict, Iterable, List, Sequence, Tuple

Grid = List[List[int]]


def _iter_components(grid: Sequence[Sequence[int]]) -> Iterable[Tuple[int, List[Tuple[int, int]]]]:
    """Yield 4-connected components as (color, cells)."""

    height = len(grid)
    width = len(grid[0]) if height else 0
    seen = [[False] * width for _ in range(height)]

    for r in range(height):
        for c in range(width):
            if seen[r][c]:
                continue
            color = grid[r][c]
            queue = deque([(r, c)])
            seen[r][c] = True
            cells = [(r, c)]

            while queue:
                cr, cc = queue.popleft()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not seen[nr][nc] and grid[nr][nc] == color:
                        seen[nr][nc] = True
                        queue.append((nr, nc))
                        cells.append((nr, nc))

            yield color, cells


def solve_195c6913(grid: Grid) -> Grid:
    """Reconstruct the legend-driven pattern and propagate it across the canvas."""

    if not grid or not grid[0]:
        return [row[:] for row in grid]

    height = len(grid)
    width = len(grid[0])
    background = grid[0][0]

    components = list(_iter_components(grid))
    total_by_color: Dict[int, int] = {}
    for color, cells in components:
        total_by_color[color] = total_by_color.get(color, 0) + len(cells)

    palette_infos: List[Tuple[int, int, List[Tuple[int, int]]]] = []
    for color, cells in components:
        if len(cells) != 4:
            continue
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        if max(rows) - min(rows) != 1 or max(cols) - min(cols) != 1:
            continue
        if min(rows) > 2:
            continue
        palette_infos.append((min(cols), color, cells))

    if not palette_infos:
        return [row[:] for row in grid]

    palette_infos.sort(key=lambda item: item[0])
    pattern: List[int] = [color for _, color, _ in palette_infos]
    pattern_cells = [cells for _, _, cells in palette_infos]
    pattern_len = len(pattern)

    candidate_colors = [
        (total_by_color[c], c)
        for c in total_by_color
        if c != background and c not in pattern
    ]
    if not candidate_colors:
        return [row[:] for row in grid]

    fill_color = max(candidate_colors)[1]
    remaining_candidates = [item for item in candidate_colors if item[1] != fill_color]
    cap_color = min(remaining_candidates)[1] if remaining_candidates else None

    cap_component: List[Tuple[int, int]] = []
    if cap_color is not None:
        cap_comps = [cells for color, cells in components if color == cap_color]
        if cap_comps:
            cap_component = min(cap_comps, key=len)

    result = [row[:] for row in grid]
    for cells in pattern_cells:
        for r, c in cells:
            result[r][c] = background
    for r, c in cap_component:
        result[r][c] = background

    # locate anchor rows
    anchor_rows: List[Tuple[int, int, int]] = []  # (row, boundary, start_idx)
    for r, row in enumerate(grid):
        first = row[0]
        if first not in pattern:
            continue
        start_idx = pattern.index(first)
        c = 1
        while c < width and row[c] == fill_color:
            c += 1
        if c <= 1:
            continue
        anchor_rows.append((r, c, start_idx))

    if not anchor_rows:
        return result

    anchor_rows.sort()

    def fill_anchor_row(r: int, boundary: int, start_idx: int) -> None:
        idx = start_idx
        for c in range(boundary):
            result[r][c] = pattern[idx]
            idx = (idx + 1) % pattern_len
        if cap_color is not None and boundary < width:
            result[r][boundary] = cap_color

    for r, boundary, start_idx in anchor_rows:
        fill_anchor_row(r, boundary, start_idx)

    def propagate(r_anchor: int, boundary: int, start_idx: int, direction: int) -> None:
        col_last = boundary - 1
        if col_last < 0 or col_last >= width:
            return
        idx_anchor = (start_idx + col_last) % pattern_len

        # walk along anchor column
        rows_col: List[Tuple[int, int]] = []
        r = r_anchor + direction
        current_idx = (idx_anchor - direction) % pattern_len
        while 0 <= r < height and result[r][col_last] == fill_color:
            result[r][col_last] = pattern[current_idx]
            rows_col.append((r, current_idx))
            r += direction
            current_idx = (current_idx - direction) % pattern_len
        if rows_col and cap_color is not None and 0 <= r < height:
            result[r][col_last] = cap_color

        if not rows_col:
            return

        boundary_row, idx_boundary = rows_col[-1]

        # fill boundary row horizontally to the right
        run_end = col_last
        while run_end < width and grid[boundary_row][run_end] == fill_color:
            run_end += 1
        if run_end == col_last:
            return

        idx = idx_boundary
        for c in range(col_last, run_end):
            result[boundary_row][c] = pattern[idx]
            idx = (idx + 1) % pattern_len
        if cap_color is not None and run_end < width:
            result[boundary_row][run_end] = cap_color

        col_right = run_end - 1
        idx_right = (idx_boundary + (run_end - col_last - 1)) % pattern_len
        rows_edge: List[Tuple[int, int]] = []
        r = boundary_row + direction
        current_idx = (idx_right - direction) % pattern_len
        while 0 <= r < height and grid[r][col_right] == fill_color:
            result[r][col_right] = pattern[current_idx]
            rows_edge.append((r, current_idx))
            r += direction
            current_idx = (current_idx - direction) % pattern_len
        if rows_edge and cap_color is not None and 0 <= r < height:
            result[r][col_right] = cap_color

        if not rows_edge:
            return

        row_idx, idx_value = rows_edge[-1]
        neighbor_row = row_idx + direction
        if not (0 <= neighbor_row < height) or grid[neighbor_row][col_right] == fill_color:
            return

        c = col_right + 1
        next_idx = (idx_value + 1) % pattern_len
        while c < width and grid[row_idx][c] == fill_color:
            result[row_idx][c] = pattern[next_idx]
            next_idx = (next_idx + 1) % pattern_len
            c += 1
        if cap_color is not None and c < width:
            result[row_idx][c] = cap_color

    top_r, top_boundary, top_idx = anchor_rows[0]
    propagate(top_r, top_boundary, top_idx, direction=-1)
    if len(anchor_rows) == 1:
        propagate(top_r, top_boundary, top_idx, direction=1)
    else:
        bottom_r, bottom_boundary, bottom_idx = anchor_rows[-1]
        propagate(bottom_r, bottom_boundary, bottom_idx, direction=-1)

    return result


p = solve_195c6913
