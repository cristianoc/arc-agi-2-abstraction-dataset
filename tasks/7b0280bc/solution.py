"""Solver for ARC-AGI-2 task 7b0280bc (evaluation split)."""

from __future__ import annotations

from collections import Counter, deque
from typing import Dict, Iterable, List, Set, Tuple, TypedDict


Grid = List[List[int]]


class Component(TypedDict):
    color: int
    size: int
    row_min: int
    row_max: int
    col_min: int
    col_max: int
    cells: List[Tuple[int, int]]


def identifyForegroundColours(grid: Grid) -> Tuple[int, int]:
    counts = Counter(cell for row in grid for cell in row)
    background, _ = counts.most_common(1)[0]
    colours = [c for c, _ in counts.most_common() if c != background][:2]
    if len(colours) < 2:
        # degenerate; mirror behaviour by returning duplicates
        return (colours[0], colours[0]) if colours else (0, 0)
    return colours[0], colours[1]


def extractMonoComponents(grid: Grid, colours: Set[int]) -> List[Component]:
    h = len(grid)
    w = len(grid[0]) if h else 0
    seen = [[False] * w for _ in range(h)]
    comps: List[Component] = []

    for r in range(h):
        for c in range(w):
            if seen[r][c] or grid[r][c] not in colours:
                continue
            color = grid[r][c]
            q = deque([(r, c)])
            seen[r][c] = True
            cells: List[Tuple[int, int]] = []
            while q:
                y, x = q.popleft()
                cells.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and not seen[ny][nx] and grid[ny][nx] == color:
                        seen[ny][nx] = True
                        q.append((ny, nx))
            rows = [y for y, _ in cells]
            cols = [x for _, x in cells]
            comps.append(
                Component(
                    color=color,
                    size=len(cells),
                    row_min=min(rows),
                    row_max=max(rows),
                    col_min=min(cols),
                    col_max=max(cols),
                    cells=cells,
                )
            )
    return comps


def evaluateDecisionTree(component: Component) -> bool:
    color = component["color"]
    row_min = component["row_min"]
    row_max = component["row_max"]
    col_min = component["col_min"]
    size = component["size"]

    if row_min <= 1:
        if color <= 3:
            return col_min <= 4
        return True

    if color <= 3:
        if row_max <= 9:
            return False
        if size <= 3:
            return True
        if color <= 1:
            return size > 6
        return True

    if row_min <= 3:
        if color <= 5:
            return col_min <= 4
        return True

    return False


def repaintComponents(grid: Grid, selected: List[Component]) -> Grid:
    if not grid or not grid[0]:
        return [row[:] for row in grid]
    major, minor = identifyForegroundColours(grid)
    result = [row[:] for row in grid]
    for comp in selected:
        for y, x in comp["cells"]:
            original = grid[y][x]
            if original == major:
                result[y][x] = 5
            elif original == minor:
                result[y][x] = 3
    return result


def solve_7b0280bc(grid: Grid) -> Grid:
    major, minor = identifyForegroundColours(grid)
    components = extractMonoComponents(grid, set((major, minor)))
    selected = [component for component in components if evaluateDecisionTree(component)]
    return repaintComponents(grid, selected)


p = solve_7b0280bc
