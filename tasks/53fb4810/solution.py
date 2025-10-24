"""Solver for ARC-AGI-2 task 53fb4810."""

from typing import Callable, Iterable, List, Tuple


Grid = List[List[int]]
Cell = Tuple[int, int, int]
Component = List[Cell]


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def findMixedComponents(grid: Grid) -> List[Component]:
    """Return all 4-connected components that contain both colours {2,4}."""
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    targets = {2, 4}
    components: List[Component] = []

    for r in range(h):
        for c in range(w):
            if grid[r][c] in targets and not seen[r][c]:
                stack = [(r, c)]
                seen[r][c] = True
                cells: Component = []
                colors = set()

                while stack:
                    rr, cc = stack.pop()
                    color = grid[rr][cc]
                    cells.append((rr, cc, color))
                    colors.add(color)

                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = rr + dr, cc + dc
                        if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc]:
                            if grid[nr][nc] in targets:
                                seen[nr][nc] = True
                                stack.append((nr, nc))

                if colors == targets:
                    components.append(cells)

    return components


def tilePatternUpward(canvas: Grid, comp: Component) -> Grid:
    """Tile the component's 2/4 pattern upward in its column span."""
    result = _copy_grid(canvas)
    rows = [r for r, _, _ in comp]
    cols = [c for _, c, _ in comp]
    row_min, row_max = min(rows), max(rows)
    col_min, _col_max = min(cols), max(cols)

    height = row_max - row_min + 1
    pattern_rows: List[List[Tuple[int, int]]] = [[] for _ in range(height)]
    for r, c, color in comp:
        pattern_rows[r - row_min].append((c - col_min, color))

    for r in range(row_min - 1, -1, -1):
        pattern_idx = (r - row_min) % height
        for dc, color in pattern_rows[pattern_idx]:
            result[r][col_min + dc] = color

    return result


def fold_repaint(
    canvas: Grid, items: Iterable[Component], update: Callable[[Grid, Component], Grid]
) -> Grid:
    """Functional fold that applies `update` sequentially over items."""
    acc = _copy_grid(canvas)
    for x in items:
        acc = update(acc, x)
    return acc


def solve_53fb4810(grid: Grid) -> Grid:
    components = findMixedComponents(grid)

    def repaint(canvas: Grid, comp: Component) -> Grid:
        return tilePatternUpward(canvas, comp)

    return fold_repaint(grid, components, repaint)


p = solve_53fb4810
