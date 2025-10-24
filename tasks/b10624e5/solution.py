"""Solver for ARC-AGI-2 task b10624e5 (split: evaluation)."""

from __future__ import annotations

from collections import Counter
from typing import Callable, Iterable, List, Sequence, Tuple, TypedDict, Optional

# Typed aliases for clarity and mypy
Grid = List[List[int]]
Coord = Tuple[int, int]
Component = List[Coord]


class OrnamentPalette(TypedDict, total=False):
    inner_h: int | None
    outer_h: int | None
    inner_v: int | None
    outer_v: int | None


def _clone_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def findCenterCross(grid: Grid) -> Tuple[int, int]:
    """Locate the dominant row and column of ones that form the cross."""
    # Reset per-solve globals to ensure purity across calls
    global _B10624E5_ORIG, _B10624E5_CROSS
    _B10624E5_ORIG = _clone_grid(grid)
    _B10624E5_CROSS = None
    height = len(grid)
    width = len(grid[0]) if grid else 0
    center_row = max(range(height), key=lambda r: sum(1 for v in grid[r] if v == 1))
    center_col = max(range(width), key=lambda c: sum(1 for r in range(height) if grid[r][c] == 1))
    return center_row, center_col


def _get_components_by_value(grid: Grid, value: int) -> List[Component]:
    height = len(grid)
    width = len(grid[0]) if grid else 0
    visited: set[Coord] = set()
    components: List[Component] = []

    for r in range(height):
        for c in range(width):
            if grid[r][c] != value or (r, c) in visited:
                continue
            stack: List[Coord] = [(r, c)]
            visited.add((r, c))
            comp: Component = []
            while stack:
                cr, cc = stack.pop()
                comp.append((cr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and grid[nr][nc] == value and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        stack.append((nr, nc))
            components.append(comp)

    return components


def extractTwoComponents(grid: Grid) -> List[Component]:
    return _get_components_by_value(grid, value=2)


_B10624E5_ORIG: Optional[Grid] = None
_B10624E5_CROSS: Optional[Tuple[int, int]] = None


def _infer_global_palette(canvas: Grid, center_row: int, center_col: int) -> OrnamentPalette:
    base = _B10624E5_ORIG if _B10624E5_ORIG is not None else canvas
    height = len(base)
    width = len(base[0]) if base else 0
    components = extractTwoComponents(base)
    if not components:
        return {"inner_h": None, "outer_h": None, "inner_v": None, "outer_v": None}

    inner_horizontal_candidates: List[int] = []
    outer_horizontal_candidates: List[int] = []
    vertical_outer_candidates: List[int] = []
    vertical_inner_candidates: List[int] = []

    for comp in components:
        rows = [r for r, _ in comp]
        cols = [c for _, c in comp]
        minr, maxr = min(rows), max(rows)
        minc, maxc = min(cols), max(cols)
        avg_row = sum(rows) / len(rows)
        avg_col = sum(cols) / len(cols)
        side = "left" if avg_col < center_col else "right"
        vert_pos = "top" if avg_row < center_row else "bottom"

        inner_col = maxc + 1 if side == "left" else minc - 1
        if 0 <= inner_col < width:
            for r in range(minr, maxr + 1):
                val = base[r][inner_col]
                if val != 4:
                    inner_horizontal_candidates.append(val)

        outer_col = minc - 1 if side == "left" else maxc + 1
        if 0 <= outer_col < width:
            for r in range(minr, maxr + 1):
                val = base[r][outer_col]
                if val != 4:
                    outer_horizontal_candidates.append(val)

        comp_columns = list(range(minc, maxc + 1))
        column_dist = {c: abs(c - center_col) for c in comp_columns}
        sorted_cols = sorted(comp_columns, key=lambda c: column_dist[c])
        inner_count = len(comp_columns) // 2
        inner_cols = set(sorted_cols[:inner_count])
        outer_cols = set(comp_columns) - inner_cols

        outer_row = minr - 1 if vert_pos == "top" else maxr + 1
        if 0 <= outer_row < height:
            for c in outer_cols:
                val = base[outer_row][c]
                if val != 4:
                    vertical_outer_candidates.append(val)
            for c in inner_cols:
                val = base[outer_row][c]
                if val != 4:
                    vertical_inner_candidates.append(val)

    def choose_color(values: Sequence[int]) -> int | None:
        return Counter(values).most_common(1)[0][0] if values else None

    inner_h = choose_color(inner_horizontal_candidates)
    outer_h = choose_color(outer_horizontal_candidates)
    outer_v = choose_color(vertical_outer_candidates)
    inner_v = choose_color(vertical_inner_candidates)
    if inner_v == outer_v:
        inner_v = None
    return {"inner_h": inner_h, "outer_h": outer_h, "inner_v": inner_v, "outer_v": outer_v}


def inferOrnamentColours(canvas: Grid, component: Component, cross: Tuple[int, int]) -> OrnamentPalette:
    global _B10624E5_ORIG, _B10624E5_CROSS
    if _B10624E5_ORIG is None:
        _B10624E5_ORIG = _clone_grid(canvas)
    if _B10624E5_CROSS is None:
        _B10624E5_CROSS = cross
    center_row, center_col = cross
    return _infer_global_palette(canvas, center_row, center_col)


def paintOrnaments(canvas: Grid, component: Component, palette: OrnamentPalette) -> Grid:
    if not component:
        return canvas
    height = len(canvas)
    width = len(canvas[0]) if canvas else 0

    rows = [r for r, _ in component]
    cols = [c for _, c in component]
    minr, maxr = min(rows), max(rows)
    minc, maxc = min(cols), max(cols)
    comp_height = maxr - minr + 1

    # Determine side and vertical position relative to the global center cross
    base_center = _B10624E5_CROSS
    if base_center is None:
        # Fallback: compute from original/base if available
        base_center = findCenterCross(_B10624E5_ORIG or canvas)
    center_row, center_col = base_center
    avg_row = sum(rows) / len(rows)
    avg_col = sum(cols) / len(cols)
    side = "left" if avg_col < center_col else "right"
    vert_pos = "top" if avg_row < center_row else "bottom"

    # Horizontal expansions (towards and away from the centre column).
    inner_horizontal_color = palette.get("inner_h")
    outer_horizontal_color = palette.get("outer_h")
    inner_thickness = comp_height if inner_horizontal_color is not None else 0
    outer_thickness = (comp_height // 2) if outer_horizontal_color is not None else 0

    result = _clone_grid(canvas)

    if inner_thickness:
        ihc = inner_horizontal_color  # type: ignore[assignment]
        # mypy: guarded by inner_thickness implies non-None
        assert ihc is not None
        if side == "left":
            for offset in range(1, inner_thickness + 1):
                col = maxc + offset
                if col >= width:
                    break
                for row in range(minr, maxr + 1):
                    if result[row][col] == 4:
                        result[row][col] = ihc
        else:  # right side component, fill to the left
            for offset in range(1, inner_thickness + 1):
                col = minc - offset
                if col < 0:
                    break
                for row in range(minr, maxr + 1):
                    if result[row][col] == 4:
                        result[row][col] = ihc

    if outer_thickness:
        ohc = outer_horizontal_color
        assert ohc is not None
        if side == "left":
            for offset in range(1, outer_thickness + 1):
                col = minc - offset
                if col < 0:
                    break
                for row in range(minr, maxr + 1):
                    if result[row][col] == 4:
                        result[row][col] = ohc
        else:
            for offset in range(1, outer_thickness + 1):
                col = maxc + offset
                if col >= width:
                    break
                for row in range(minr, maxr + 1):
                    if result[row][col] == 4:
                        result[row][col] = ohc

    # Vertical expansions (away from the centre row).
    vertical_inner_color = palette.get("inner_v")
    vertical_outer_color = palette.get("outer_v")
    vertical_inner_thickness = comp_height if vertical_inner_color is not None else 0
    if vertical_inner_color is None:
        vertical_outer_thickness = comp_height if vertical_outer_color is not None else 0
    else:
        vertical_outer_thickness = (comp_height + 1) // 2 if vertical_outer_color is not None else 0

    if vertical_outer_thickness or vertical_inner_thickness:
        comp_columns = list(range(minc, maxc + 1))
        column_dist = {c: abs(c - center_col) for c in comp_columns}
        sorted_cols = sorted(comp_columns, key=lambda c: column_dist[c])
        if vertical_inner_color is not None:
            inner_count = len(comp_columns) // 2
            inner_cols = set(sorted_cols[:inner_count])
        else:
            inner_cols = set()
        outer_cols = set(comp_columns) - inner_cols

        base_row = minr if vert_pos == "top" else maxr
        direction = -1 if vert_pos == "top" else 1

        def paint_column(col: int, color: int | None, thickness: int) -> None:
            if color is None or thickness <= 0:
                return
            row = base_row
            for _ in range(thickness):
                row += direction
                if not (0 <= row < height):
                    break
                if result[row][col] == 4:
                    result[row][col] = color

        for col in outer_cols:
            paint_column(col, vertical_outer_color, vertical_outer_thickness)
        for col in inner_cols:
            paint_column(col, vertical_inner_color, vertical_inner_thickness)

    return result


def fold_repaint(canvas: Grid, items: Iterable[Component], update: Callable[[Grid, Component], Grid]) -> Grid:
    result = canvas
    for item in items:
        result = update(result, item)
    return result


def solve_b10624e5(grid: Grid) -> Grid:
    cross = findCenterCross(grid)
    components = extractTwoComponents(grid)

    def repaint(canvas: Grid, component: Component) -> Grid:
        palette = inferOrnamentColours(canvas, component, cross)
        return paintOrnaments(canvas, component, palette)

    return fold_repaint(grid, components, repaint)


p = solve_b10624e5
