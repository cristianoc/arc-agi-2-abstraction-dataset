"""Solver for ARC task 16b78196."""

from collections import defaultdict, deque
from typing import Dict, Iterable, List, Optional, Tuple, cast

Grid = List[List[int]]
Point = Tuple[int, int]


def _in_bounds(r: int, c: int, height: int, width: int) -> bool:
    return 0 <= r < height and 0 <= c < width


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _get_components(grid: Grid) -> List[Dict[str, object]]:
    """Return 4-connected monochromatic components with metadata."""

    grid_height, grid_width = len(grid), len(grid[0])
    seen = [[False] * grid_width for _ in range(grid_height)]
    components: List[Dict[str, object]] = []

    for r in range(grid_height):
        for c in range(grid_width):
            color = grid[r][c]
            if color == 0 or seen[r][c]:
                continue

            queue: deque[Point] = deque([(r, c)])
            seen[r][c] = True
            cells: List[Point] = []

            while queue:
                cr, cc = queue.popleft()
                cells.append((cr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if _in_bounds(nr, nc, grid_height, grid_width) and not seen[nr][nc] and grid[nr][nc] == color:
                        seen[nr][nc] = True
                        queue.append((nr, nc))

            rows = [rr for rr, _ in cells]
            cols = [cc for _, cc in cells]

            top, left, bottom, right = min(rows), min(cols), max(rows), max(cols)
            comp_height = bottom - top + 1
            comp_width = right - left + 1

            normalized = sorted((rr - top, cc - left) for rr, cc in cells)

            components.append(
                {
                    "color": color,
                    "cells": cells,
                    "size": len(cells),
                    "top": top,
                    "left": left,
                    "bottom": bottom,
                    "right": right,
                    "height": comp_height,
                    "width": comp_width,
                    "shape": tuple(normalized),
                }
            )

    return components


def _paint_component(target: Grid, top: int, left: int, comp: Dict[str, object]) -> None:
    shape = cast(Iterable[Tuple[int, int]], comp["shape"])  # type: ignore[index]
    color = cast(int, comp["color"])  # type: ignore[index]
    for dr, dc in shape:
        rr = top + dr
        cc = left + dc
        target[rr][cc] = color


def _order_narrow(components: List[Dict[str, object]]) -> List[Dict[str, object]]:
    sorted_comps = sorted(
        components,
        key=lambda comp: (
            cast(int, comp["color"]),
            cast(int, comp["top"]),
            cast(int, comp["left"]),
        ),
    )
    grouped: Dict[int, List[Dict[str, object]]] = defaultdict(list)
    for comp in sorted_comps:
        grouped[cast(int, comp["color"])].append(comp)

    ordered: List[Dict[str, object]] = []
    tail: List[Dict[str, object]] = []
    for comp in sorted_comps:
        color = cast(int, comp["color"]) 
        bucket = grouped[color]
        if bucket and bucket[0] is comp:
            ordered.append(comp)
            grouped[color] = bucket[1:]
            tail.extend(grouped[color])
            grouped[color] = []
    ordered.extend(tail)
    return ordered


def _stack_components(
    output: Grid,
    comps: List[Dict[str, object]],
    *,
    above: bool,
    col: int,
    width: int,
    height: int,
    top_anchor: Optional[int],
    bottom_anchor: Optional[int],
    anchor_bottom: Optional[int],
    compress_bottom: bool,
) -> None:
    if not comps:
        return

    max_width = max(cast(int, comp["width"]) for comp in comps)
    col_clamped = max(0, min(width - max_width, col))

    heights = [cast(int, comp["height"]) for comp in comps]

    if above:
        assert bottom_anchor is not None
        total_height = sum(heights) - (len(comps) - 1)
        bottom_anchor_i = cast(int, bottom_anchor)
        top0 = bottom_anchor_i - total_height + 1
    else:
        assert top_anchor is not None
        top_anchor_i = cast(int, top_anchor)
        top0 = top_anchor_i

    if top0 < 0:
        shift = -top0
        top0 = 0
        # If stacking below, maintain relative anchor by shifting reference
        if not above and top_anchor is not None:
            top_anchor = cast(int, top_anchor) + shift

    tops: List[int] = []
    curr_top = top0
    for h in heights:
        tops.append(curr_top)
        curr_top += h - 1

    bottom_last = tops[-1] + heights[-1] - 1
    if bottom_last >= height:
        shift = bottom_last - (height - 1)
        tops = [max(0, t - shift) for t in tops]

    if compress_bottom and not above and anchor_bottom is not None:
        max_height = max(heights)
        anchor_bottom_i = cast(int, anchor_bottom)
        desired_bottom = anchor_bottom_i + len(comps) + max_height - 1
        bottom_last = tops[-1] + heights[-1] - 1
        excess = bottom_last - desired_bottom
        if excess > 0:
            for idx in range(len(tops) - 1, 0, -1):
                max_shift = tops[idx] - (tops[idx - 1] + 1)
                if max_shift <= 0:
                    continue
                shift = min(max_shift, excess)
                if shift > 0:
                    tops[idx] -= shift
                    excess -= shift
                    if excess == 0:
                        break
            if excess > 0:
                tops[0] = max(0, tops[0] - excess)

    for comp, top in zip(comps, tops):
        _paint_component(output, top, col_clamped, comp)


# --- Minimal DSL-style wrappers to match abstractions.md ---
def getComponents(grid: Grid) -> List[Dict[str, object]]:
    return _get_components(grid)


def splitByWidth(components: List[Dict[str, object]]) -> Tuple[Dict[str, object], List[Dict[str, object]], List[Dict[str, object]]]:
    dominant = max(components, key=lambda comp: cast(int, comp["size"]))  # type: ignore[index]
    others = [comp for comp in components if comp is not dominant]
    wide = [comp for comp in others if cast(int, comp["width"]) >= 5]
    narrow = [comp for comp in others if cast(int, comp["width"]) < 5]
    return dominant, wide, narrow


def paintDominantBand(grid: Grid, dominant: Dict[str, object]) -> Grid:
    height, width = len(grid), len(grid[0])
    output: Grid = [[0] * width for _ in range(height)]
    for r, c in cast(Iterable[Tuple[int, int]], dominant["cells"]):  # type: ignore[index]
        output[r][c] = cast(int, dominant["color"])  # type: ignore[index]
    return output


def placeWideComponents(result: Grid, wide: List[Dict[str, object]], dominant: Dict[str, object]) -> Grid:
    if not wide:
        return result
    height, width = len(result), len(result[0])
    wide_sorted = sorted(wide, key=lambda comp: (cast(int, comp["top"]), -cast(int, comp["left"])) )
    bottom_anchor = cast(int, dominant["top"]) + 1  # type: ignore[index]
    _stack_components(
        result,
        wide_sorted,
        above=True,
        col=4,
        width=width,
        height=height,
        top_anchor=None,
        bottom_anchor=bottom_anchor,
        anchor_bottom=None,
        compress_bottom=False,
    )
    return result


def orderNarrow(narrow: List[Dict[str, object]]) -> List[Dict[str, object]]:
    return _order_narrow(narrow)


def placeNarrowComponents(result: Grid, ordered_narrow: List[Dict[str, object]], dominant: Dict[str, object]) -> Grid:
    if not ordered_narrow:
        return result
    height, width = len(result), len(result[0])

    # Detect whether wide components were already placed by scanning for
    # any non-dominant colored cells in the result.
    dom_cells = set(cast(Iterable[Tuple[int, int]], dominant["cells"]))  # type: ignore[index]
    wide_present = any(
        (result[r][c] != 0) and ((r, c) not in dom_cells)
        for r in range(height)
        for c in range(width)
    )

    mean_left = sum(cast(int, comp["left"]) for comp in ordered_narrow) / len(ordered_narrow)
    max_width = max(cast(int, comp["width"]) for comp in ordered_narrow)

    dom_bottom = cast(int, dominant["bottom"])  # type: ignore[index]
    if wide_present:
        column = int(round(mean_left))
        top_anchor = dom_bottom
    else:
        column = int(round(mean_left - 1))
        top_anchor = dom_bottom - 1

    column = max(0, min(width - max_width, column))
    _stack_components(
        result,
        ordered_narrow,
        above=False,
        col=column,
        width=width,
        height=height,
        top_anchor=top_anchor,
        bottom_anchor=None,
        anchor_bottom=dom_bottom,
        compress_bottom=True,
    )
    return result


def solve_16b78196(grid: Grid) -> Grid:
    components = getComponents(grid)
    dominant, wide, narrow = splitByWidth(components)
    
    result = paintDominantBand(grid, dominant)
    result = placeWideComponents(result, wide, dominant)
    ordered_narrow = orderNarrow(narrow)
    return placeNarrowComponents(result, ordered_narrow, dominant)


p = solve_16b78196
