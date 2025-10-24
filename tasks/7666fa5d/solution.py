"""Solver for ARC-AGI-2 task 7666fa5d."""

from collections import Counter, deque
from typing import List, Tuple, Set, Optional

Grid = List[List[int]]
Cell = Tuple[int, int]
Component = List[Cell]
Summary = Tuple[int, int, int]  # (u = r+c, v_min = min(c-r), v_max = max(c-r))


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def background_and_single_foreground(grid: Grid) -> Tuple[int, Optional[int]]:
    if not grid or not grid[0]:
        return 0, None
    counts = Counter(val for row in grid for val in row)
    background, _ = counts.most_common(1)[0]
    foreground = {v for v in counts.keys() if v != background}
    if len(foreground) != 1:
        return background, None
    return background, next(iter(foreground))


def extractDiagonalComponents(grid: Grid) -> List[Component]:
    """Flood-fill the single foreground colour and keep only diagonal components.

    Returns an empty list if the grid is empty, there is not exactly one
    foreground colour, or any component is not strictly on a single diagonal.
    """
    background, target = background_and_single_foreground(grid)
    if target is None:
        return []

    h = len(grid)
    w = len(grid[0]) if h else 0
    visited = [[False] * w for _ in range(h)]
    comps: List[Component] = []

    for r in range(h):
        for c in range(w):
            if grid[r][c] != target or visited[r][c]:
                continue
            dq = deque([(r, c)])
            visited[r][c] = True
            coords: List[Cell] = []
            while dq:
                x, y = dq.popleft()
                coords.append((x, y))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < h and 0 <= ny < w and not visited[nx][ny] and grid[nx][ny] == target:
                            visited[nx][ny] = True
                            dq.append((nx, ny))
            if not coords:
                continue
            u0 = coords[0][0] + coords[0][1]
            if any((x + y) != u0 for x, y in coords):
                return []
            comps.append(coords)

    return comps


def summariseComponents(components: List[Component]) -> List[Summary]:
    """Map each component to (u=r+c, v_min, v_max) and sort by u."""
    summaries: List[Summary] = []
    for comp in components:
        if not comp:
            continue
        u = comp[0][0] + comp[0][1]
        v_vals = [c - r for r, c in comp]
        summaries.append((u, min(v_vals), max(v_vals)))
    summaries.sort()
    return summaries


def bracketBackgroundCells(grid: Grid, summaries: List[Summary]) -> Set[Cell]:
    """Collect background cells that are bracketed by components on both sides."""
    background, _ = background_and_single_foreground(grid)
    if len(summaries) < 2:
        return set()

    h = len(grid)
    w = len(grid[0]) if h else 0
    cells: Set[Cell] = set()

    for r in range(h):
        for c in range(w):
            if grid[r][c] != background:
                continue
            u = r + c
            v = c - r

            left_sum: Optional[int] = None
            for su, vmin, vmax in summaries:
                if su > u:
                    break
                if vmin <= v <= vmax:
                    left_sum = su
            if left_sum is None:
                continue

            right_sum: Optional[int] = None
            for su, vmin, vmax in summaries:
                if su < u:
                    continue
                if vmin <= v <= vmax:
                    right_sum = su
                    break
            if right_sum is None or left_sum >= right_sum:
                continue

            cells.add((r, c))

    return cells


def fillCorridor(grid: Grid, corridor: Set[Cell], color: int) -> Grid:
    """Paint the cells in `corridor` with `color`, leaving others unchanged."""
    result = copy_grid(grid)
    for r, c in corridor:
        result[r][c] = color
    return result


def solve_7666fa5d(grid: Grid) -> Grid:
    components = extractDiagonalComponents(grid)
    summaries = summariseComponents(components)
    corridor = bracketBackgroundCells(grid, summaries)
    return fillCorridor(grid, corridor, 2)


p = solve_7666fa5d
