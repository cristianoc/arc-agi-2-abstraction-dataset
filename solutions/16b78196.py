"""Solver for ARC task 16b78196."""

from collections import defaultdict, deque
from typing import Dict, Iterable, List, Optional, Tuple

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
    for dr, dc in comp["shape"]:  # type: ignore[index]
        rr = top + dr
        cc = left + dc
        target[rr][cc] = int(comp["color"])  # type: ignore[index]


def _order_narrow(components: List[Dict[str, object]]) -> List[Dict[str, object]]:
    sorted_comps = sorted(components, key=lambda comp: (int(comp["color"]), comp["top"], comp["left"]))
    grouped: Dict[int, List[Dict[str, object]]] = defaultdict(list)
    for comp in sorted_comps:
        grouped[int(comp["color"])].append(comp)

    ordered: List[Dict[str, object]] = []
    tail: List[Dict[str, object]] = []
    for comp in sorted_comps:
        color = int(comp["color"])
        bucket = grouped[color]
        if bucket and bucket[0] is comp:
            ordered.append(comp)
            grouped[color] = bucket[1:]
            tail.extend(grouped[color])
            grouped[color] = []
    ordered.extend(tail)
    return ordered


def solve_16b78196(grid: Grid) -> Grid:
    """Compact stacked arrangement of non-dominant shapes around the dominant band."""

    height, width = len(grid), len(grid[0])
    components = _get_components(grid)
    if not components:
        return _copy_grid(grid)

    dominant = max(components, key=lambda comp: comp["size"])  # type: ignore[index]
    others = [comp for comp in components if comp is not dominant]

    wide = [comp for comp in others if comp["width"] >= 5]  # type: ignore[index]
    narrow = [comp for comp in others if comp["width"] < 5]  # type: ignore[index]

    output: Grid = [[0] * width for _ in range(height)]
    for r, c in dominant["cells"]:  # type: ignore[index]
        output[r][c] = int(dominant["color"])  # type: ignore[index]

    def stack_components(
        comps: List[Dict[str, object]],
        *,
        above: bool,
        col: int,
        top_anchor: Optional[int] = None,
        bottom_anchor: Optional[int] = None,
        anchor_bottom: Optional[int] = None,
    ) -> None:
        if not comps:
            return

        widths = [comp["width"] for comp in comps]  # type: ignore[index]
        max_width = max(widths)
        col_clamped = max(0, min(width - max_width, col))

        heights = [comp["height"] for comp in comps]  # type: ignore[index]
        total_height = sum(heights) - (len(comps) - 1)

        if above:
            assert bottom_anchor is not None
            top0 = bottom_anchor - total_height + 1
        else:
            assert top_anchor is not None
            top0 = top_anchor

        if top0 < 0:
            shift = -top0
            top0 = 0
            if not above and top_anchor is not None:
                top_anchor += shift
        tops: List[int] = []
        curr_top = top0
        for h in heights:
            tops.append(curr_top)
            curr_top += h - 1

        bottom_last = tops[-1] + heights[-1] - 1
        if bottom_last >= height:
            shift = bottom_last - (height - 1)
            tops = [max(0, t - shift) for t in tops]

        if not above and anchor_bottom is not None:
            max_height = max(heights)
            desired_bottom = anchor_bottom + len(comps) + max_height - 1
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

    if wide:
        wide_sorted = sorted(wide, key=lambda comp: (int(comp["top"]), -int(comp["left"])) )
        bottom_anchor = dominant["top"] + 1  # type: ignore[index]
        stack_components(wide_sorted, above=True, col=4, bottom_anchor=bottom_anchor)

    if narrow:
        narrow_ordered = _order_narrow(narrow)
        mean_left = sum(comp["left"] for comp in narrow_ordered) / len(narrow_ordered)  # type: ignore[index]
        max_width = max(comp["width"] for comp in narrow_ordered)  # type: ignore[index]

        if wide:
            column = int(round(mean_left))
            top_anchor = dominant["bottom"]  # type: ignore[index]
        else:
            column = int(round(mean_left - 1))
            top_anchor = dominant["bottom"] - 1  # type: ignore[index]

        column = max(0, min(width - max_width, column))
        stack_components(
            narrow_ordered,
            above=False,
            col=column,
            top_anchor=top_anchor,
            anchor_bottom=int(dominant["bottom"]),
        )

    return output


p = solve_16b78196
