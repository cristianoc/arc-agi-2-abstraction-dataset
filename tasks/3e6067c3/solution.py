"""Solver for ARC-AGI-2 task 3e6067c3."""

from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple

Grid = List[List[int]]
Cell = Tuple[int, int, int]  # (row, col, color)
Node = Dict[str, int]


def _deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _background_color(grid: Grid) -> int:
    return Counter(cell for row in grid for cell in row).most_common(1)[0][0]


def _components(grid: Grid, background: int) -> List[Node]:
    height = len(grid)
    width = len(grid[0]) if grid else 0
    visited = [[False] * width for _ in range(height)]
    comps: List[Node] = []

    for r in range(height):
        for c in range(width):
            if visited[r][c]:
                continue
            color = grid[r][c]
            visited[r][c] = True
            if color in (background, 1):
                continue
            stack = [(r, c)]
            cells: List[Tuple[int, int]] = []
            while stack:
                rr, cc = stack.pop()
                cells.append((rr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[nr][nc] == color:
                        visited[nr][nc] = True
                        stack.append((nr, nc))
            rows = [rr for rr, _ in cells]
            cols = [cc for _, cc in cells]
            comps.append(
                {
                    "color": color,
                    "min_row": min(rows),
                    "max_row": max(rows),
                    "min_col": min(cols),
                    "max_col": max(cols),
                }
            )
    return comps


def parseHintRow(grid: Grid) -> Any:
    """Collect hint context: sequence and nodes_by_color plus canvas info."""
    height = len(grid)
    width = len(grid[0]) if grid else 0
    if not grid or not grid[0]:
        return {
            "sequence": [],
            "nodes_by_color": {},
            "background": 0,
            "height": 0,
            "width": 0,
        }

    background = _background_color(grid)
    comps = _components(grid, background)

    hint_row = max(
        (r for r, row in enumerate(grid) if any(cell not in (background, 1) for cell in row)),
        default=None,
    )

    if hint_row is None:
        return {
            "sequence": [],
            "nodes_by_color": {},
            "background": background,
            "height": height,
            "width": width,
        }

    hint_nodes = [comp for comp in comps if comp["min_row"] == comp["max_row"] == hint_row]
    hint_nodes.sort(key=lambda comp: comp["min_col"])
    sequence = [comp["color"] for comp in hint_nodes]

    nodes = [comp for comp in comps if comp not in hint_nodes]
    nodes_by_color: Dict[int, List[Node]] = defaultdict(list)
    for node in nodes:
        nodes_by_color[node["color"]].append(node)
    for bucket in nodes_by_color.values():
        bucket.sort(key=lambda comp: (comp["min_row"], comp["min_col"]))

    return {
        "sequence": sequence,
        "nodes_by_color": nodes_by_color,
        "background": background,
        "height": height,
        "width": width,
    }


def buildHintPath(hints: Any) -> List[Any]:
    """Select path nodes per hint sequence and emit adjacent segments."""
    sequence: List[int] = hints.get("sequence", [])
    nodes_by_color: Dict[int, List[Node]] = hints.get("nodes_by_color", {})
    background: int = hints.get("background", 0)
    height: int = hints.get("height", 0)
    width: int = hints.get("width", 0)

    # Select nodes by consuming per-color lists in order
    counters: Dict[int, int] = defaultdict(int)
    path_nodes: List[Node] = []
    for color in sequence:
        idx = counters[color]
        bucket = nodes_by_color.get(color, [])
        if idx >= len(bucket):
            return []  # invalid; no path
        path_nodes.append(bucket[idx])
        counters[color] += 1

    if len(path_nodes) <= 1:
        return []

    segments: List[Any] = []
    for src, dst in zip(path_nodes, path_nodes[1:]):
        color = src["color"]
        segments.append({
            "src": src,
            "dst": dst,
            "color": color,
            "background": background,
            "height": height,
            "width": width,
        })
    return segments


def traceSegmentCells(grid: Grid, segment: Any) -> List[Cell]:
    """Trace vertical and horizontal corridor cells for a segment."""
    src: Node = segment["src"]
    dst: Node = segment["dst"]
    color: int = segment["color"]
    background: int = segment["background"]
    height: int = segment["height"]
    width: int = segment["width"]

    cells: List[Cell] = []

    # Vertical corridor (between disjoint row ranges and overlapping columns)
    col_start = max(src["min_col"], dst["min_col"])
    col_end = min(src["max_col"], dst["max_col"])
    if col_start <= col_end:
        if src["max_row"] < dst["min_row"]:
            r_start = src["max_row"] + 1
            r_end = dst["min_row"] - 1
        elif dst["max_row"] < src["min_row"]:
            r_start = dst["max_row"] + 1
            r_end = src["min_row"] - 1
        else:
            r_start = None  # type: ignore[assignment]
            r_end = None    # type: ignore[assignment]
        if r_start is not None and r_end is not None:
            for r in range(r_start, r_end + 1):
                for c in range(col_start, col_end + 1):
                    if 0 <= r < height and 0 <= c < width and grid[r][c] == background:
                        cells.append((r, c, color))

    # Horizontal corridor (between disjoint column ranges and overlapping rows)
    row_start = max(src["min_row"], dst["min_row"])
    row_end = min(src["max_row"], dst["max_row"])
    if row_start <= row_end:
        if src["max_col"] < dst["min_col"]:
            c_start = src["max_col"] + 1
            c_end = dst["min_col"] - 1
        elif dst["max_col"] < src["min_col"]:
            c_start = dst["max_col"] + 1
            c_end = src["min_col"] - 1
        else:
            c_start = None  # type: ignore[assignment]
            c_end = None    # type: ignore[assignment]
        if c_start is not None and c_end is not None:
            for r in range(row_start, row_end + 1):
                for c in range(c_start, c_end + 1):
                    if 0 <= r < height and 0 <= c < width and grid[r][c] == background:
                        cells.append((r, c, color))

    return cells


def paintHintPath(grid: Grid, cells: List[Cell]) -> Grid:
    """Paint traced cells on a copy of the grid."""
    result = _deep_copy(grid)
    for r, c, color in cells:
        if 0 <= r < len(result) and 0 <= c < len(result[0]):
            result[r][c] = color
    return result


def solve_3e6067c3(grid: Grid) -> Grid:
    hints = parseHintRow(grid)
    segments = buildHintPath(hints)
    cells = [cell for segment in segments for cell in traceSegmentCells(grid, segment)]
    return paintHintPath(grid, cells)


p = solve_3e6067c3
