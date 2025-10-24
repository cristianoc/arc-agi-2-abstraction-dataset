"""Solver for ARC-AGI-2 task 446ef5d2 (evaluation split)."""

from collections import defaultdict
from typing import List, Dict, Tuple, Any

Grid = List[List[int]]


def _ceil_div(a: int, b: int) -> int:
    return -(-a // b)


def _best_grid_shape(n: int) -> tuple[int, int]:
    """Pick a near-square rows×cols grid to host n components."""
    best: tuple[int, int, int, int] | None = None
    for rows in range(1, n + 1):
        cols = _ceil_div(n, rows)
        if cols < rows:
            continue
        area = rows * cols
        diff = cols - rows
        candidate = (area, diff, rows, cols)
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    return best[2], best[3]


def _components_by_color(grid):
    """Return connected-component metadata keyed by color."""
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    comps: dict[int, list[dict]] = defaultdict(list)

    for r in range(h):
        for c in range(w):
            color = grid[r][c]
            if color in (8, 4) or seen[r][c]:
                continue

            stack = [(r, c)]
            seen[r][c] = True
            cells = []

            while stack:
                y, x = stack.pop()
                cells.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and not seen[ny][nx] and grid[ny][nx] == color:
                        seen[ny][nx] = True
                        stack.append((ny, nx))

            ys = [y for y, _ in cells]
            xs = [x for _, x in cells]
            miny, maxy = min(ys), max(ys)
            minx, maxx = min(xs), max(xs)
            height = maxy - miny + 1
            width = maxx - minx + 1

            shape = [[0] * width for _ in range(height)]
            for y, x in cells:
                shape[y - miny][x - minx] = 1

            comps[color].append(
                {
                    "color": color,
                    "size": len(cells),
                    "minx": minx,
                    "miny": miny,
                    "width": width,
                    "height": height,
                    "shape": shape,
                }
            )

    return comps


def _order_components(components):
    n = len(components)
    rows, cols = _best_grid_shape(n)
    base = sorted(components, key=lambda comp: comp["minx"])

    if rows == 1:
        # Single-row layouts benefit from grouping by size and sorting by vertical position.
        ordered = []
        i = 0
        while i < len(base):
            j = i
            while j < len(base) and base[j]["size"] == base[i]["size"]:
                j += 1
            chunk = sorted(base[i:j], key=lambda comp: comp["miny"])
            ordered.extend(chunk)
            i = j
        return ordered

    return base


def _layout_block(components):
    comps = _order_components(components)
    rows, cols = _best_grid_shape(len(comps))

    cells = [[None] * cols for _ in range(rows)]
    idx = 0
    for r in range(rows):
        for c in range(cols):
            if idx < len(comps):
                cells[r][c] = comps[idx]
                idx += 1

    if rows > 1:
        for r in range(rows):
            row_comps = [comp for comp in cells[r] if comp]
            row_comps.sort(key=lambda comp: (-comp["height"], comp["minx"]))
            for c, comp in enumerate(row_comps):
                cells[r][c] = comp
            for c in range(len(row_comps), cols):
                cells[r][c] = None

    col_widths = [max((cells[r][c]["width"] for r in range(rows) if cells[r][c]), default=0) for c in range(cols)]
    row_heights = [max((cells[r][c]["height"] for c in range(cols) if cells[r][c]), default=0) for r in range(rows)]

    height = sum(row_heights)
    width = sum(col_widths)
    block = [[-1] * width for _ in range(height)]

    for r in range(rows):
        y0 = sum(row_heights[:r])
        for c in range(cols):
            comp = cells[r][c]
            if not comp:
                continue
            x0 = sum(col_widths[:c])
            shape = comp["shape"]
            for dy, row in enumerate(shape):
                for dx, val in enumerate(row):
                    if val:
                        block[y0 + dy][x0 + dx] = comp["color"]

    return {
        "block": block,
        "height": height,
        "width": width,
        "rows": rows,
        "cols": cols,
    }


def filterNoise(grid: Grid, noise_color: int) -> Grid:
    return [[8 if v == noise_color else v for v in row] for row in grid]


def extractPerColorComponents(grid: Grid) -> Dict[str, Any]:
    h, w = len(grid), len(grid[0])
    comps = _components_by_color(grid)
    return {"h": h, "w": w, "comps": comps}


def packComponentsIntoGrid(info: Dict[str, Any]) -> Dict[str, Any]:
    h: int = info["h"]
    w: int = info["w"]
    comps: Dict[int, List[Dict[str, Any]]] = info["comps"]

    if not comps:
        return {"h": h, "w": w, "rect": [row[:] for row in [[8] * 0 for _ in range(0)]], "rect_height": 0, "rect_width": 0, "offset_row": 0, "offset_col": 0}

    counts = {color: sum(comp["size"] for comp in lst) for color, lst in comps.items()}
    if not counts:
        return {"h": h, "w": w, "rect": [row[:] for row in [[8] * 0 for _ in range(0)]], "rect_height": 0, "rect_width": 0, "offset_row": 0, "offset_col": 0}

    base_color = max(counts.items(), key=lambda item: (item[1], item[0]))[0]
    others = [color for color in comps if color != base_color]
    if not others:
        return {"h": h, "w": w, "rect": [row[:] for row in [[8] * 0 for _ in range(0)]], "rect_height": 0, "rect_width": 0, "offset_row": 0, "offset_col": 0}

    centroid_rows: Dict[int, float] = {}
    for color in others:
        total = 0.0
        total_size = 0
        for comp in comps[color]:
            center = comp["miny"] + 0.5 * (comp["height"] - 1)
            total += center * comp["size"]
            total_size += comp["size"]
        centroid_rows[color] = total / max(total_size, 1)

    color_order = sorted(others, key=lambda color: centroid_rows[color])

    blocks: Dict[int, Dict[str, Any]] = {}
    inner_width = 0
    max_cols_minus_rows = 0
    max_rows_minus_cols = 0
    for color in color_order:
        block_info = _layout_block(comps[color])
        blocks[color] = block_info
        inner_width = max(inner_width, block_info["width"])
        max_cols_minus_rows = max(max_cols_minus_rows, block_info["cols"] - block_info["rows"])
        max_rows_minus_cols = max(max_rows_minus_cols, block_info["rows"] - block_info["cols"])

    rect_width = inner_width + 2
    rect_height = sum(blocks[color]["height"] for color in color_order) + (len(color_order) + 1)

    shift_h = max(0, max_cols_minus_rows)
    shift_v = max(0, max_rows_minus_cols)

    offset_row = min(max(_ceil_div(h - rect_height, 2) + shift_v, 0), max(0, h - rect_height))
    offset_col = min(max(_ceil_div(w - rect_width, 2) + shift_h, 0), max(0, w - rect_width))

    rect = [[base_color] * rect_width for _ in range(rect_height)]
    row_cursor = 1
    for idx, color in enumerate(color_order):
        block = blocks[color]["block"]
        height = blocks[color]["height"]
        width = blocks[color]["width"]
        for r in range(height):
            for c in range(width):
                val = block[r][c]
                if val != -1:
                    rect[row_cursor + r][1 + c] = val
        row_cursor += height
        if idx != len(color_order) - 1:
            row_cursor += 1

    return {
        "h": h,
        "w": w,
        "rect": rect,
        "rect_height": rect_height,
        "rect_width": rect_width,
        "offset_row": offset_row,
        "offset_col": offset_col,
    }


def embedPackedGrid(packed: Dict[str, Any], background: int) -> Grid:
    h: int = packed["h"]
    w: int = packed["w"]
    rect: Grid = packed["rect"]
    rect_height: int = packed["rect_height"]
    rect_width: int = packed["rect_width"]
    offset_row: int = packed["offset_row"]
    offset_col: int = packed["offset_col"]

    out = [[background] * w for _ in range(h)]
    for r in range(rect_height):
        for c in range(rect_width):
            out[offset_row + r][offset_col + c] = rect[r][c]
    return out


def solve_446ef5d2(grid: Grid) -> Grid:
    cleaned = filterNoise(grid, 4)
    per_color = extractPerColorComponents(cleaned)
    packed = packComponentsIntoGrid(per_color)
    return embedPackedGrid(packed, 8)


p = solve_446ef5d2
