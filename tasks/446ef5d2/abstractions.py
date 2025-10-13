"""Abstraction experiments for ARC task 446ef5d2."""

from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict
from typing import Callable, Iterable


TASK_PATH = Path("analysis/arc2_samples/446ef5d2.json")


# ---------------------------------------------------------------------------
# Shared helpers


def _ceil_div(a: int, b: int) -> int:
    return -(-a // b)


def _clean_grid(grid):
    return [[8 if v == 4 else v for v in row] for row in grid]


def _components_by_color(grid):
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


def _best_grid_shape(n: int) -> tuple[int, int]:
    best: tuple[int, int, int, int] | None = None
    for rows in range(1, n + 1):
        cols = _ceil_div(n, rows)
        if cols < rows:
            continue
        area = rows * cols
        diff = cols - rows
        cand = (area, diff, rows, cols)
        if best is None or cand < best:
            best = cand
    assert best is not None
    return best[2], best[3]


def _order_components(components):
    n = len(components)
    rows, _ = _best_grid_shape(n)
    base = sorted(components, key=lambda comp: comp["minx"])
    if rows == 1:
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
            for dy, row in enumerate(comp["shape"]):
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


def _assemble_row(components, inner_width, base_color):
    block = [[base_color] * inner_width for _ in range(max(comp["height"] for comp in components))]
    cursor = 0
    for comp in components:
        for r, row in enumerate(comp["shape"]):
            for c, val in enumerate(row):
                if val:
                    block[r][cursor + c] = comp["color"]
        cursor += comp["width"]
    return block


# ---------------------------------------------------------------------------
# Abstractions


def identity_abstraction(grid):
    """Only drop the noisy color 4."""
    return _clean_grid(grid)


def horizontal_compactor(grid):
    """Pack each color into a single horizontal strip (fails on case 1)."""
    base_grid = _clean_grid(grid)
    comps = _components_by_color(base_grid)
    if not comps:
        return [row[:] for row in base_grid]

    counts = {color: sum(comp["size"] for comp in lst) for color, lst in comps.items()}
    base_color = max(counts.items(), key=lambda item: (item[1], item[0]))[0]
    others = [color for color in comps if color != base_color]

    if not others:
        return [row[:] for row in base_grid]

    inner_width = max(sum(comp["width"] for comp in comps[color]) for color in others)
    inner_height = sum(max(comp["height"] for comp in comps[color]) for color in others)
    rect_height = inner_height + len(others) + 1
    rect_width = inner_width + 2

    rect = [[base_color] * rect_width for _ in range(rect_height)]
    row_cursor = 1
    for idx, color in enumerate(sorted(others)):
        ordered = sorted(comps[color], key=lambda comp: comp["minx"])
        block = _assemble_row(ordered, inner_width, base_color)
        for r, row_vals in enumerate(block):
            rect[row_cursor + r][1 : 1 + inner_width] = row_vals
        row_cursor += len(block) + 1

    h, w = len(grid), len(grid[0])
    out = [[8] * w for _ in range(h)]
    off_r = min(max(_ceil_div(h - rect_height, 2), 0), max(0, h - rect_height))
    off_c = min(max(_ceil_div(w - rect_width, 2), 0), max(0, w - rect_width))
    for r in range(rect_height):
        for c in range(rect_width):
            out[off_r + r][off_c + c] = rect[r][c]
    return out


def grid_compactor(grid):
    """Final abstraction: grid-based packing with per-row balancing."""
    base_grid = _clean_grid(grid)
    comps = _components_by_color(base_grid)
    if not comps:
        return [row[:] for row in base_grid]

    counts = {color: sum(comp["size"] for comp in lst) for color, lst in comps.items()}
    base_color = max(counts.items(), key=lambda item: (item[1], item[0]))[0]
    others = [color for color in comps if color != base_color]
    if not others:
        return [row[:] for row in base_grid]

    centroids = {}
    for color in others:
        total = 0.0
        total_size = 0
        for comp in comps[color]:
            center = comp["miny"] + 0.5 * (comp["height"] - 1)
            total += center * comp["size"]
            total_size += comp["size"]
        centroids[color] = total / max(total_size, 1)

    color_order = sorted(others, key=lambda color: centroids[color])

    blocks = {}
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

    h, w = len(grid), len(grid[0])
    out = [[8] * w for _ in range(h)]
    off_r = min(max(_ceil_div(h - rect_height, 2) + shift_v, 0), max(0, h - rect_height))
    off_c = min(max(_ceil_div(w - rect_width, 2) + shift_h, 0), max(0, w - rect_width))
    for r in range(rect_height):
        for c in range(rect_width):
            out[off_r + r][off_c + c] = rect[r][c]
    return out


# ---------------------------------------------------------------------------
# Evaluation harness


def _load_task():
    return json.loads(TASK_PATH.read_text())


def _evaluate(abstraction: Callable[[list[list[int]]], list[list[int]]], cases: Iterable[dict]):
    total = 0
    matches = 0
    first_fail = None
    for idx, case in enumerate(cases):
        if "output" not in case:
            continue
        total += 1
        pred = abstraction(case["input"])
        if pred == case["output"]:
            matches += 1
        elif first_fail is None:
            first_fail = idx
    return matches, total, first_fail


def main():
    data = _load_task()
    abstractions = {
        "identity": identity_abstraction,
        "horizontal_compactor": horizontal_compactor,
        "grid_compactor": grid_compactor,
    }

    for name, fn in abstractions.items():
        print(f"Abstraction: {name}")
        for split in ("train", "test", "arc-gen"):
            cases = data.get(split)
            if not cases:
                continue
            if "output" not in cases[0]:
                print(f"  {split}: outputs hidden (cases={len(cases)})")
                continue
            matched, total, first_fail = _evaluate(fn, cases)
            fail_str = "None" if first_fail is None else str(first_fail)
            print(f"  {split}: {matched}/{total} matched; first fail={fail_str}")
        print()


if __name__ == "__main__":
    main()
