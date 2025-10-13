"""Solver for ARC-AGI-2 task 4c7dc4dd (split: evaluation)."""

from collections import Counter, deque
from typing import List, Tuple

Grid = List[List[int]]


def _find_zero_components(grid: Grid, min_size: int = 6) -> List[Tuple[List[Tuple[int, int]], Tuple[int, int, int, int]]]:
    """Return sizeable 4-connected zero components with their bounding boxes."""

    height = len(grid)
    width = len(grid[0])
    visited = [[False] * width for _ in range(height)]
    components: List[Tuple[List[Tuple[int, int]], Tuple[int, int, int, int]]] = []

    for r in range(height):
        for c in range(width):
            if grid[r][c] != 0 or visited[r][c]:
                continue

            queue = deque([(r, c)])
            visited[r][c] = True
            cells: List[Tuple[int, int]] = []

            while queue:
                cr, cc = queue.popleft()
                cells.append((cr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[nr][nc] == 0:
                        visited[nr][nc] = True
                        queue.append((nr, nc))

            if len(cells) < min_size:
                continue

            rows = [cell[0] for cell in cells]
            cols = [cell[1] for cell in cells]
            bbox = (min(rows), max(rows), min(cols), max(cols))
            components.append((cells, bbox))

    return components


def _select_output_size(components: List[Tuple[List[Tuple[int, int]], Tuple[int, int, int, int]]]) -> int:
    """Use component heights to pick a square output resolution."""

    heights = [bbox[1] - bbox[0] + 1 for _, bbox in components]
    robust = [h for h in heights if h >= 3]
    candidate = max(robust or heights or [3])
    return max(3, candidate)


def _component_centers(
    components: List[Tuple[List[Tuple[int, int]], Tuple[int, int, int, int]]],
    in_height: int,
    in_width: int,
    out_size: int,
) -> List[Tuple[float, float]]:
    """Return component centers scaled into the output coordinate system."""

    centres: List[Tuple[float, float]] = []
    for cells, _ in components:
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        centre_r = (sum(rows) / len(rows)) / in_height * out_size
        centre_c = (sum(cols) / len(cols)) / in_width * out_size
        centres.append((centre_r, centre_c))
    return centres


def _rare_non_background_color(grid: Grid) -> Tuple[int, int] | None:
    """Return the rarest non-zero color (count, value) for corner highlighting."""

    counts = Counter(value for row in grid for value in row if value != 0)
    if not counts:
        return None
    color, freq = min(counts.items(), key=lambda item: (item[1], item[0]))
    return color, freq


def solve_4c7dc4dd(grid: Grid) -> Grid:
    """Project salient zero rectangles to a coarse glyph with a highlighted corner."""

    input_height = len(grid)
    input_width = len(grid[0])

    components = _find_zero_components(grid)
    if not components:
        return [[0]]

    out_size = _select_output_size(components)
    output = [[0] * out_size for _ in range(out_size)]

    centres = _component_centers(components, input_height, input_width, out_size)
    row_centres = sorted(r for r, _ in centres)
    anchor_row = int(round((row_centres[0] + row_centres[1]) / 2)) if len(row_centres) >= 2 else int(round(row_centres[0]))
    anchor_row = max(0, min(out_size - 1, anchor_row))
    for col in range(out_size):
        output[anchor_row][col] = 2

    col_centres = [c for _, c in centres]
    midpoint = out_size / 2
    left_centres = [c for c in col_centres if c < midpoint]
    right_centres = [c for c in col_centres if c >= midpoint]
    if len(right_centres) > len(left_centres):
        vertical_side = "right"
        anchor_col = int(round(max(col_centres)))
    else:
        vertical_side = "left"
        anchor_col = int(min(col_centres))
    anchor_col = max(0, min(out_size - 1, anchor_col))

    if vertical_side == "right":
        start_row = 0
        end_row = out_size - 1
    else:
        max_centre_row = int(round(max(r for r, _ in centres)))
        start_row = anchor_row
        end_row = max(start_row, min(out_size - 1, max_centre_row))
    for row in range(start_row, end_row + 1):
        output[row][anchor_col] = 2

    if vertical_side == "right" and left_centres:
        left_span = int(min(col_centres))
        left_span = max(0, min(out_size - 1, left_span))
        for col in range(0, left_span + 1):
            output[0][col] = 2
        bottom_row = int(round(max(r for r, _ in centres)))
        bottom_row = max(0, min(out_size - 1, bottom_row))
        for col in range(0, max(0, left_span)):
            output[bottom_row][col] = 2

    rare = _rare_non_background_color(grid)
    if rare and rare[0] not in {0, 2} and rare[1] <= 10:
        output[anchor_row][anchor_col] = rare[0]

    return output


p = solve_4c7dc4dd

