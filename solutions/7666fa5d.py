"""Solver for ARC-AGI-2 task 7666fa5d."""

from collections import Counter, deque
from typing import List

Grid = List[List[int]]


def solve_7666fa5d(grid: Grid) -> Grid:
    """Fill the corridor framed by the diagonal guide dots with color 2."""

    if not grid or not grid[0]:
        return [row[:] for row in grid]

    height, width = len(grid), len(grid[0])
    counts = Counter(val for row in grid for val in row)
    background, _ = counts.most_common(1)[0]
    foreground_colors = {val for row in grid for val in row if val != background}
    if len(foreground_colors) != 1:
        return [row[:] for row in grid]
    target_color = foreground_colors.pop()

    visited = [[False] * width for _ in range(height)]
    components = []

    for r in range(height):
        for c in range(width):
            if grid[r][c] != target_color or visited[r][c]:
                continue

            dq = deque([(r, c)])
            visited[r][c] = True
            coords = []

            while dq:
                x, y = dq.popleft()
                coords.append((x, y))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < height
                            and 0 <= ny < width
                            and not visited[nx][ny]
                            and grid[nx][ny] == target_color
                        ):
                            visited[nx][ny] = True
                            dq.append((nx, ny))

            diag_sum = coords[0][0] + coords[0][1]
            if any(x + y != diag_sum for x, y in coords):
                return [row[:] for row in grid]

            diag_diffs = [y - x for x, y in coords]
            components.append((diag_sum, min(diag_diffs), max(diag_diffs)))

    components.sort()
    if len(components) < 2:
        return [row[:] for row in grid]

    result = [row[:] for row in grid]

    for r in range(height):
        for c in range(width):
            if grid[r][c] != background:
                continue

            diag_sum = r + c
            diag_diff = c - r

            left_sum = None
            for comp_sum, v_min, v_max in components:
                if comp_sum > diag_sum:
                    break
                if v_min <= diag_diff <= v_max:
                    left_sum = comp_sum

            if left_sum is None:
                continue

            right_sum = None
            for comp_sum, v_min, v_max in components:
                if comp_sum < diag_sum:
                    continue
                if v_min <= diag_diff <= v_max:
                    right_sum = comp_sum
                    break

            if right_sum is None or left_sum >= right_sum:
                continue

            result[r][c] = 2

    return result


p = solve_7666fa5d
