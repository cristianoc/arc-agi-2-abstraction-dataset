"""Solver for ARC-AGI-2 task 4c7dc4dd (split: evaluation)."""

from collections import Counter, deque
from typing import List, Tuple, Optional, Dict, Any

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


def _rare_non_background_color(grid: Grid) -> Optional[Tuple[int, int]]:
    """Return the rarest non-zero color (count, value) for corner highlighting."""

    counts = Counter(value for row in grid for value in row if value != 0)
    if not counts:
        return None
    color, freq = min(counts.items(), key=lambda item: (item[1], item[0]))
    return color, freq


def detectZeroRectangles(grid: Grid) -> Dict[str, Any]:
    """Detect sizeable zero components; return metadata bundle for downstream steps."""
    components = _find_zero_components(grid)
    return {
        "components": components,
        "in_height": len(grid),
        "in_width": len(grid[0]) if grid else 0,
        "rare": _rare_non_background_color(grid),
    }


def buildScaffold(rectangles: Dict[str, Any]) -> Dict[str, Any]:
    """Build coarse scaffold: output size, centers, and anchor decisions."""
    components = rectangles["components"]
    if not components:
        return {"empty": True}

    in_h = rectangles["in_height"]
    in_w = rectangles["in_width"]
    out_size = _select_output_size(components)
    centres = _component_centers(components, in_h, in_w, out_size)

    row_centres = sorted(r for r, _ in centres)
    anchor_row_f = (row_centres[0] + row_centres[1]) / 2 if len(row_centres) >= 2 else row_centres[0]
    anchor_row = max(0, min(out_size - 1, int(round(anchor_row_f))))

    col_centres = [c for _, c in centres]
    midpoint = out_size / 2
    left = [c for c in col_centres if c < midpoint]
    right = [c for c in col_centres if c >= midpoint]
    if len(right) > len(left):
        side = "right"
        anchor_col = int(round(max(col_centres)))
    else:
        side = "left"
        anchor_col = int(min(col_centres))
    anchor_col = max(0, min(out_size - 1, anchor_col))

    if side == "right":
        start_row, end_row = 0, out_size - 1
    else:
        max_row = int(round(max(r for r, _ in centres)))
        start_row = anchor_row
        end_row = max(start_row, min(out_size - 1, max_row))

    extra = None
    if side == "right" and left:
        left_span = int(min(col_centres))
        left_span = max(0, min(out_size - 1, left_span))
        bottom_row = int(round(max(r for r, _ in centres)))
        bottom_row = max(0, min(out_size - 1, bottom_row))
        extra = {"left_span": left_span, "bottom_row": bottom_row}

    return {
        "empty": False,
        "out_size": out_size,
        "anchor_row": anchor_row,
        "anchor_col": anchor_col,
        "start_row": start_row,
        "end_row": end_row,
        "side": side,
        "extra": extra,
        "rare": rectangles["rare"],
    }


def augmentScaffold(scaffold: Dict[str, Any]) -> Dict[str, Any]:
    """No-op augmenter; scaffold already encodes all needed strokes."""
    return scaffold


def renderGlyph(scaffold: Dict[str, Any]) -> Grid:
    if scaffold.get("empty"):
        return [[0]]

    n = scaffold["out_size"]
    out = [[0] * n for _ in range(n)]

    anchor_row = scaffold["anchor_row"]
    for c in range(n):
        out[anchor_row][c] = 2

    anchor_col = scaffold["anchor_col"]
    for r in range(scaffold["start_row"], scaffold["end_row"] + 1):
        out[r][anchor_col] = 2

    if scaffold["side"] == "right" and scaffold["extra"] is not None:
        left_span = scaffold["extra"]["left_span"]
        bottom_row = scaffold["extra"]["bottom_row"]
        for c in range(0, left_span + 1):
            out[0][c] = 2
        for c in range(0, max(0, left_span)):
            out[bottom_row][c] = 2

    rare = scaffold.get("rare")
    if rare and rare[0] not in {0, 2} and rare[1] <= 10:
        out[anchor_row][anchor_col] = rare[0]

    return out


def solve_4c7dc4dd(grid: Grid) -> Grid:
    rectangles = detectZeroRectangles(grid)
    scaffold = buildScaffold(rectangles)
    augmented = augmentScaffold(scaffold)
    return renderGlyph(augmented)


p = solve_4c7dc4dd
