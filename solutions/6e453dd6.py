"""Solver for ARC-AGI-2 task 6e453dd6 (split: evaluation)."""

from collections import Counter, deque


def _most_common_nonzero(grid):
    """Return the most frequent non-zero color (fallback to 0 if none)."""
    counts = Counter(cell for row in grid for cell in row)
    non_zero = [color for color in counts if color != 0]
    if non_zero:
        return max(non_zero, key=counts.__getitem__)
    return 0


def _highlight_color(grid, default=2):
    """Pick a highlight color, preferring the default if unused."""
    present = {cell for row in grid for cell in row}
    if default not in present:
        return default
    for candidate in range(10):
        if candidate not in present:
            return candidate
    return default


def solve_6e453dd6(grid):
    """Slide zero-components against the 5-column and mark certain rows."""
    height = len(grid)
    width = len(grid[0])

    # Locate the column occupied by color 5; bail out if absent.
    five_columns = [c for c in range(width) if any(row[c] == 5 for row in grid)]
    if not five_columns:
        return [row[:] for row in grid]
    col_five = five_columns[0]

    background = _most_common_nonzero(grid)
    highlight = _highlight_color(grid)

    result = [row[:] for row in grid]

    # Reset the left region to the background color before repositioning zeros.
    for r in range(height):
        for c in range(col_five):
            result[r][c] = background

    visited = [[False] * width for _ in range(height)]
    for r in range(height):
        for c in range(col_five):
            if grid[r][c] == 0 and not visited[r][c]:
                component = []
                queue = deque([(r, c)])
                visited[r][c] = True
                while queue:
                    rr, cc = queue.popleft()
                    component.append((rr, cc))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = rr + dr, cc + dc
                        if 0 <= nr < height and 0 <= nc < col_five and not visited[nr][nc] and grid[nr][nc] == 0:
                            visited[nr][nc] = True
                            queue.append((nr, nc))

                rightmost = max(col for _, col in component)
                shift = max(0, (col_five - 1) - rightmost)
                for rr, cc in component:
                    result[rr][cc + shift] = 0

    # Preserve the original content to the right of the 5-column.
    for r in range(height):
        for c in range(col_five + 1, width):
            result[r][c] = grid[r][c]

    # Promote rows that have a trailing 0 next to the 5 with a gap of background color.
    if col_five >= 2 and col_five + 1 < width:
        for r in range(height):
            if result[r][col_five - 1] == 0 and result[r][col_five - 2] == background:
                for c in range(col_five + 1, width):
                    result[r][c] = highlight

    return result


p = solve_6e453dd6
