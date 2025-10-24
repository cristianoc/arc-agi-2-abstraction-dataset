"""Solver for ARC-AGI-2 task 6e453dd6 (split: evaluation).

Refactored to align the solver's main with the typed DSL lambda.
"""

from collections import Counter, deque
from typing import List, Tuple, Optional


# Type aliases for clarity and static checking
Grid = List[List[int]]
Pos = Tuple[int, int]
Component = List[Pos]


def _most_common_nonzero(grid: Grid) -> int:
    """Return the most frequent non-zero color (fallback to 0 if none)."""
    counts = Counter(cell for row in grid for cell in row)
    non_zero = [color for color in counts if color != 0]
    if non_zero:
        return max(non_zero, key=counts.__getitem__)
    return 0


def _highlight_color(grid: Grid, default: int = 2) -> int:
    """Pick a highlight color, preferring the default if unused, else first unused digit."""
    present = {cell for row in grid for cell in row}
    if default not in present:
        return default
    for candidate in range(10):
        if candidate not in present:
            return candidate
    return default


# === DSL helper shims (pure) ===

def locateFiveColumn(grid: Grid) -> Optional[int]:
    width = len(grid[0])
    for c in range(width):
        if any(row[c] == 5 for row in grid):
            return c
    return None


def extractZeroComponents(grid: Grid, five_col: int) -> List[Component]:
    height = len(grid)
    width = len(grid[0])
    visited = [[False] * width for _ in range(height)]
    components: List[Component] = []

    for r in range(height):
        for c in range(five_col):
            if grid[r][c] == 0 and not visited[r][c]:
                comp: Component = []
                queue = deque([(r, c)])
                visited[r][c] = True
                while queue:
                    rr, cc = queue.popleft()
                    comp.append((rr, cc))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = rr + dr, cc + dc
                        if 0 <= nr < height and 0 <= nc < five_col and not visited[nr][nc] and grid[nr][nc] == 0:
                            visited[nr][nc] = True
                            queue.append((nr, nc))
                components.append(comp)
    return components


def slideComponentsRight(grid: Grid, components: List[Component], five_col: int) -> Grid:
    """Return a grid where each zero-component is slid so its right edge meets five_col-1.

    Also repaints the left-of-five region to the background colour and preserves
    the original right-of-five region, matching the baseline behaviour.
    """
    height = len(grid)
    width = len(grid[0])
    background = _most_common_nonzero(grid)

    result: Grid = [row[:] for row in grid]

    # Reset left-of-five to background
    for r in range(height):
        for c in range(five_col):
            result[r][c] = background

    # Paint shifted zero components
    for comp in components:
        rightmost = max(col for _, col in comp)
        shift = max(0, (five_col - 1) - rightmost)
        for rr, cc in comp:
            result[rr][cc + shift] = 0

    # Preserve the original content to the right of the 5-column
    for r in range(height):
        for c in range(five_col + 1, width):
            result[r][c] = grid[r][c]

    return result


def determineHighlightColors(grid: Grid) -> Tuple[int, int]:
    background = _most_common_nonzero(grid)
    highlight = _highlight_color(grid)
    return background, highlight


def highlightRowTail(grid: Grid, five_col: int, background: int, highlight: int) -> Grid:
    height = len(grid)
    width = len(grid[0])
    result: Grid = [row[:] for row in grid]

    if five_col >= 2 and five_col + 1 < width:
        for r in range(height):
            if result[r][five_col - 1] == 0 and result[r][five_col - 2] == background:
                for c in range(five_col + 1, width):
                    result[r][c] = highlight
    return result


# === Main matches the DSL lambda ===
def solve_6e453dd6(grid: Grid) -> Grid:
    five_col = locateFiveColumn(grid)
    if five_col is None:
        return grid
    components = extractZeroComponents(grid, five_col)
    shifted = slideComponentsRight(grid, components, five_col)
    background, highlight = determineHighlightColors(grid)
    return highlightRowTail(shifted, five_col, background, highlight)


p = solve_6e453dd6
