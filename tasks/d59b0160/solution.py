"""Solver for ARC-AGI-2 task d59b0160."""

from __future__ import annotations

from collections import deque
from typing import Callable, List, Set, Tuple, TypedDict

Grid = List[List[int]]


class Component(TypedDict):
    cells: List[Tuple[int, int]]
    colors: Set[int]
    r0: int
    r1: int
    c0: int
    c1: int
    width: int
    height: int


# --- Minimal DSL helpers ----------------------------------------------------

def fold_repaint(canvas: Grid, items: List[Component], update: Callable[[Grid, Component], Grid]) -> Grid:
    result = [row[:] for row in canvas]
    for item in items:
        result = update(result, item)
    return result


def extractNonSevenComponents(grid: Grid) -> List[Component]:
    """Return 4-connected components of non-7 cells with basic stats."""
    height = len(grid)
    width = len(grid[0])
    seen = [[False] * width for _ in range(height)]
    components: List[Component] = []

    for r in range(height):
        for c in range(width):
            if seen[r][c] or grid[r][c] == 7:
                continue
            stack = deque([(r, c)])
            seen[r][c] = True
            cells: List[Tuple[int, int]] = []
            colors = set()
            r_min = r_max = r
            c_min = c_max = c

            while stack:
                cr, cc = stack.pop()
                cells.append((cr, cc))
                colors.add(grid[cr][cc])
                r_min = min(r_min, cr)
                r_max = max(r_max, cr)
                c_min = min(c_min, cc)
                c_max = max(c_max, cc)
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not seen[nr][nc] and grid[nr][nc] != 7:
                        seen[nr][nc] = True
                        stack.append((nr, nc))

            components.append(
                Component(
                    cells=cells,
                    colors=colors,
                    r0=r_min,
                    r1=r_max,
                    c0=c_min,
                    c1=c_max,
                    width=c_max - c_min + 1,
                    height=r_max - r_min + 1,
                )
            )

    return components


def shouldFill(comp: Component, h: int, w: int) -> bool:
    """Decide whether the component should be painted to 7."""
    height, width = h, w
    comp_width = comp["width"]
    comp_height = comp["height"]
    r0, r1 = comp["r0"], comp["r1"]
    c0, c1 = comp["c0"], comp["c1"]

    touches_top = r0 == 0
    touches_right = c1 == width - 1
    touches_left = c0 == 0
    unique_colors = len(comp["colors"])

    if comp_width <= 2 or touches_top:
        return False
    if touches_right:
        return True
    if touches_left:
        return comp_height <= 5
    if comp_height <= 4:
        return True
    if comp_height == 5 and unique_colors <= 4:
        if c0 <= 2 or c0 >= width - 4:
            return True
    return False


def paintComponent(canvas: Grid, comp: Component, colour: int) -> Grid:
    for r, c in comp["cells"]:
        canvas[r][c] = colour
    return canvas


def solve_d59b0160(grid: Grid) -> Grid:
    components = extractNonSevenComponents(grid)
    if not grid:
        return grid
    h, w = len(grid), len(grid[0])

    def repaint(canvas: Grid, comp: Component) -> Grid:
        return paintComponent(canvas, comp, 7) if shouldFill(comp, h, w) else canvas

    return fold_repaint(grid, components, repaint)


p = solve_d59b0160
