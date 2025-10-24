"""Solver for ARC-AGI-2 task 20a9e565."""

from collections import Counter, defaultdict
from typing import List

Grid = List[List[int]]
from itertools import groupby


def _copy_grid(grid):
    return [row[:] for row in grid]


def _nonzero_columns(grid):
    h = len(grid)
    w = len(grid[0])
    return [c for c in range(w) if any(grid[r][c] != 0 for r in range(h))]


def _column_groups(grid):
    h = len(grid)
    nonzero_cols = _nonzero_columns(grid)
    if not nonzero_cols:
        return [], 0
    tops = [next(grid[r][c] for r in range(h) if grid[r][c] != 0) for c in nonzero_cols]
    groups = []
    start = 0
    for color, indices_iter in groupby(range(len(nonzero_cols)), key=lambda idx: tops[idx]):
        idx_list = list(indices_iter)
        groups.append({
            "color": color,
            "start": start,
            "length": len(idx_list),
        })
        start += len(idx_list)
    return groups, len(nonzero_cols)


# --- Thin wrappers to match the typed-DSL surface ---
def columnGroups(grid):
    """DSL: Group consecutive non-zero columns by top color.

    Returns (groups, count).
    """
    groups, total_cols = _column_groups(grid)
    return groups, total_cols


def classifyPattern(groups):
    """DSL: Classify groups into one of "S", "C", or "B"."""
    kind, _ = _classify(groups)
    return kind


def buildTypeS(groups):
    """DSL: Build type-S layout from groups only."""
    # _build_type_s does not actually use the grid argument.
    return _build_type_s(None, groups)


def buildTypeC(grid, groups):
    """DSL: Build type-C layout using grid + groups."""
    return _build_type_c(grid, groups)


def buildTypeB(groups):
    """DSL: Build type-B layout from groups only."""
    total_cols = sum(g["length"] for g in groups)
    return _build_type_b(grid=None, total_cols=total_cols, groups=groups)  # type: ignore[arg-type]


def _bounding_boxes(grid):
    boxes = defaultdict(lambda: [10 ** 9, -1, 10 ** 9, -1])
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value == 0:
                continue
            box = boxes[value]
            if r < box[0]:
                box[0] = r
            if r > box[1]:
                box[1] = r
            if c < box[2]:
                box[2] = c
            if c > box[3]:
                box[3] = c
    return {
        color: {
            "height": box[1] - box[0] + 1,
            "width": box[3] - box[2] + 1,
        }
        for color, box in boxes.items()
    }


def _classify(groups):
    colors = [g["color"] for g in groups]
    n = len(groups)
    for k in range(1, n // 2 + 1):
        if colors[:k] == colors[k: 2 * k]:
            return "S", k
    lengths = [g["length"] for g in groups]
    freq = Counter(lengths)
    if any(freq[length] == 1 for length in freq):
        return "C", None
    return "B", None


def _build_type_s(grid, groups):
    freq_color = Counter(g["color"] for g in groups)
    first_color = groups[0]["color"]
    result = []
    for g_idx, g in enumerate(groups):
        color = g["color"]
        next_color = groups[g_idx + 1]["color"] if g_idx + 1 < len(groups) else None
        next_effective = next_color
        if next_color is not None and freq_color[next_color] == 1:
            next_effective = first_color
        for pos in range(g["length"]):
            if g_idx == len(groups) - 1:
                if pos == 0:
                    result.append([first_color, first_color])
                else:
                    result.append([0, first_color])
                continue
            if pos == 0:
                result.append([color, color])
            else:
                if g_idx % 2 == 0:
                    result.append([next_effective, color])
                else:
                    result.append([color, next_effective])
    return result


def _build_type_c(grid, groups):
    boxes = _bounding_boxes(grid)
    lengths = [g["length"] for g in groups]
    freq_len = Counter(lengths)
    candidate = None
    best_width = None
    for g in groups:
        length = g["length"]
        if freq_len[length] != 1:
            continue
        width = boxes[g["color"]]["width"]
        if best_width is None or width < best_width:
            best_width = width
            candidate = (g["color"], length)
    if candidate is None:
        candidate = (groups[0]["color"], groups[0]["length"])
    color, length = candidate
    width = max(1, length * 2)
    height = 3
    out = [[0] * width for _ in range(height)]
    for c in range(width):
        out[0][c] = color
        out[-1][c] = color
    for r in range(height):
        out[r][0] = color
    return out


def _build_type_b(grid, total_cols, groups):
    base_color = groups[0]["color"]
    rows = max(1, total_cols - 1)
    out = []
    for idx in range(rows):
        if idx % 2 == 0:
            out.append([base_color, base_color, base_color])
        else:
            out.append([base_color, 0, base_color])
    return out


def solve_20a9e565(grid: Grid) -> Grid:
    groups, total_cols = columnGroups(grid)
    tag = classifyPattern(groups)

    if tag == "S":
        return buildTypeS(groups)
    elif tag == "C":
        return buildTypeC(grid, groups)
    else:  # tag == "B"
        return buildTypeB(groups)


p = solve_20a9e565
