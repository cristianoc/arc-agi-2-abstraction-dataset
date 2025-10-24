"""Solver for ARC-AGI-2 task 4a21e3da (evaluation split), refactored to DSL workflow."""

from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple, Union


# Basic typed aliases used by the DSL subset
Grid = List[List[int]]
Point = Tuple[int, int]
Sentinel = Point  # classified later relative to the glyph's bounding box
Component = Set[Point]
Corner = str  # "top-left" | "top-right" | "bottom-left" | "bottom-right"


# Pure helpers (no mutation of inputs)
def _component_cells(grid: Grid, color: int) -> List[Point]:
    return [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == color]


def _bbox(cells: Iterable[Point]) -> Tuple[int, int, int, int]:
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    return min(rows), max(rows), min(cols), max(cols)


def _align_to_corner(cells: Iterable[Point], corner: Corner, height: int, width: int) -> Set[Point]:
    cells = list(cells)
    if not cells:
        return set()
    min_r, max_r, min_c, max_c = _bbox(cells)
    h_span = max_r - min_r + 1
    w_span = max_c - min_c + 1
    if corner == "top-left":
        dy, dx = -min_r, -min_c
    elif corner == "top-right":
        dy, dx = -min_r, (width - w_span) - min_c
    elif corner == "bottom-left":
        dy, dx = (height - h_span) - min_r, -min_c
    else:  # "bottom-right"
        dy, dx = (height - h_span) - min_r, (width - w_span) - min_c
    return {
        (r + dy, c + dx)
        for r, c in cells
        if 0 <= r + dy < height and 0 <= c + dx < width
    }


# === DSL main function (must exactly match abstractions.md) ===
def solve_4a21e3da(grid: Grid) -> Grid:
    sentinels = findCornerSentinels(grid)
    glyph = extractSourceGlyph(grid)
    offsets = selectCornerOffsets(sentinels, glyph)
    return projectGlyphToCorners(grid, glyph, offsets)


# === Implementations of the DSL-sketched helpers ===
def findCornerSentinels(grid: Grid) -> List[Sentinel]:
    # Return all sentinel positions (colour 2); classification is done later
    return _component_cells(grid, 2)


def extractSourceGlyph(grid: Grid) -> Component:
    return set(_component_cells(grid, 7))


# Offsets/instructions per sentinel; structure tailored to downstream projection
Instruction = Dict[str, Union[int, bool]]
Offsets = Dict[Sentinel, Instruction]


def selectCornerOffsets(sentinels: List[Sentinel], glyph: Component) -> Offsets:
    if not glyph:
        return {}
    min_r, max_r, min_c, max_c = _bbox(glyph)

    has_top = any(sr < min_r for sr, _ in sentinels)
    has_bottom = any(sr > max_r for sr, _ in sentinels)
    has_left = any(sc < min_c for _, sc in sentinels)
    has_right = any(sc > max_c for _, sc in sentinels)

    offsets: Offsets = {}
    for sr, sc in sentinels:
        if sr < min_r:  # top
            instr: Instruction = {"kind_top": 1, "sr": sr, "sc": sc}
            if has_right:
                instr["limit_left_distance"] = min_r - sr  # constrain upper extent for left subset
            instr["include_right_subset"] = not has_right
            offsets[(sr, sc)] = instr
        elif sr > max_r:  # bottom
            offsets[(sr, sc)] = {"kind_bottom": 1, "sr": sr, "sc": sc}
        elif sc < min_c:  # left
            offsets[(sr, sc)] = {
                "kind_left": 1,
                "sr": sr,
                "sc": sc,
                "include_top_subset": not has_top,
                "include_bottom_subset": not has_bottom,
            }
        elif sc > max_c:  # right
            distance = sc - max_c
            threshold = max_c - distance
            offsets[(sr, sc)] = {
                "kind_right": 1,
                "sr": sr,
                "sc": sc,
                "threshold": threshold,
            }
        else:
            # Sentinel inside glyph bbox: keep only itself as a ray origin
            offsets[(sr, sc)] = {"kind_inside": 1, "sr": sr, "sc": sc}
    return offsets


def projectGlyphToCorners(grid: Grid, glyph: Component, offsets: Offsets) -> Grid:
    height, width = len(grid), len(grid[0])
    if not glyph:
        return [row[:] for row in grid]
    min_r, max_r, min_c, max_c = _bbox(glyph)

    twos_to_paint: Set[Point] = set()
    sevens_to_paint: Set[Point] = set()

    for (sr, sc), instr in offsets.items():
        twos_to_paint.add((sr, sc))

        if "kind_top" in instr:
            column_rows = [r for r, c in glyph if c == sc]
            stop_row = max(column_rows) if column_rows else max_r
            twos_to_paint |= {
                (r, sc)
                for r in range(sr, stop_row + 1)
                if (r, sc) not in glyph
            }
            left_cells = [(r, c) for (r, c) in glyph if c < sc]
            if "limit_left_distance" in instr:
                distance = int(instr["limit_left_distance"])  
                left_cells = [cell for cell in left_cells if cell[0] < min_r + distance]
            sevens_to_paint |= _align_to_corner(left_cells, "top-left", height, width)
            if bool(instr.get("include_right_subset", False)):
                right_cells = [(r, c) for (r, c) in glyph if c > sc]
                sevens_to_paint |= _align_to_corner(right_cells, "top-right", height, width)
            sevens_to_paint |= {(r, c) for (r, c) in glyph if c == sc}

        elif "kind_bottom" in instr:
            column_rows = [r for r, c in glyph if c == sc]
            stop_row = min(column_rows) if column_rows else min_r
            twos_to_paint |= {
                (r, sc)
                for r in range(sr, stop_row - 1, -1)
                if (r, sc) not in glyph
            }
            left_cells = [(r, c) for (r, c) in glyph if c < sc]
            right_cells = [(r, c) for (r, c) in glyph if c > sc]
            sevens_to_paint |= _align_to_corner(left_cells, "bottom-left", height, width)
            sevens_to_paint |= _align_to_corner(right_cells, "bottom-right", height, width)
            sevens_to_paint |= {(r, c) for (r, c) in glyph if c == sc}

        elif "kind_left" in instr:
            row_cols = [c for r, c in glyph if r == sr]
            stop_col = max(row_cols) if row_cols else max_c
            twos_to_paint |= {
                (sr, c)
                for c in range(sc, stop_col + 1)
                if (sr, c) not in glyph
            }
            top_cells = [(r, c) for (r, c) in glyph if r < sr]
            bottom_cells = [(r, c) for (r, c) in glyph if r > sr]
            if bool(instr.get("include_top_subset", False)):
                sevens_to_paint |= _align_to_corner(top_cells, "top-left", height, width)
            if bool(instr.get("include_bottom_subset", False)):
                sevens_to_paint |= _align_to_corner(bottom_cells, "bottom-left", height, width)
            sevens_to_paint |= {(r, c) for (r, c) in glyph if r == sr}

        elif "kind_right" in instr:
            row_cols = [c for r, c in glyph if r == sr]
            stop_col = min(row_cols) if row_cols else min_c
            twos_to_paint |= {
                (sr, c)
                for c in range(sc, stop_col, -1)
                if (sr, c) not in glyph
            }
            threshold = int(instr["threshold"])  
            top_cells = [(r, c) for (r, c) in glyph if r < sr and c >= threshold]
            bottom_cells = [(r, c) for (r, c) in glyph if r > sr and c >= threshold]
            sevens_to_paint |= _align_to_corner(top_cells, "top-right", height, width)
            sevens_to_paint |= _align_to_corner(bottom_cells, "bottom-right", height, width)
            sevens_to_paint |= {(r, c) for (r, c) in glyph if r == sr}

        else:  # inside bbox: only ensure the sentinel itself is present
            pass

    # Paint onto a fresh canvas (background 1), then 2s, then 7s
    out: Grid = [[1 for _ in range(width)] for _ in range(height)]
    for r, c in twos_to_paint:
        out[r][c] = 2
    for r, c in sevens_to_paint:
        out[r][c] = 7
    return out


# Backwards compatibility alias used by tooling
p = solve_4a21e3da
