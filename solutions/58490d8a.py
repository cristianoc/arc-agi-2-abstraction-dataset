"""Solver for ARC-AGI-2 task 58490d8a (split: evaluation)."""

from collections import deque


def _zero_rectangle(grid):
    zero_cells = [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == 0]
    if not zero_cells:
        return None
    rows, cols = zip(*zero_cells)
    return min(rows), max(rows), min(cols), max(cols)


def _count_components_8(grid, color, rect):
    min_r, max_r, min_c, max_c = rect
    height = len(grid)
    width = len(grid[0])
    visited = [[False] * width for _ in range(height)]
    count = 0

    for r in range(height):
        for c in range(width):
            if min_r <= r <= max_r and min_c <= c <= max_c:
                continue
            if visited[r][c] or grid[r][c] != color:
                continue

            count += 1
            queue = deque([(r, c)])
            visited[r][c] = True

            while queue:
                cr, cc = queue.popleft()
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = cr + dr, cc + dc
                        if not (0 <= nr < height and 0 <= nc < width):
                            continue
                        if min_r <= nr <= max_r and min_c <= nc <= max_c:
                            continue
                        if visited[nr][nc] or grid[nr][nc] != color:
                            continue
                        visited[nr][nc] = True
                        queue.append((nr, nc))

    return count


def solve_58490d8a(grid):
    rect = _zero_rectangle(grid)
    if rect is None:
        return [row[:] for row in grid]

    min_r, max_r, min_c, max_c = rect
    board_height = max_r - min_r + 1
    board_width = max_c - min_c + 1
    result = [[0] * board_width for _ in range(board_height)]

    cache = {}

    for out_row, src_row in enumerate(range(min_r, max_r + 1)):
        color = None
        for src_col in range(min_c, max_c + 1):
            val = grid[src_row][src_col]
            if val != 0:
                color = val
                break

        if color is None:
            continue

        if color not in cache:
            cache[color] = _count_components_8(grid, color, rect)

        repeats = cache[color]
        if repeats == 0:
            continue

        col = 1 if board_width > 1 else 0
        placed = 0
        while placed < repeats and col < board_width:
            result[out_row][col] = color
            placed += 1
            col += 2

        if placed < repeats:
            for fallback_col in range(board_width):
                if result[out_row][fallback_col] != 0:
                    continue
                result[out_row][fallback_col] = color
                placed += 1
                if placed == repeats:
                    break

    return result


p = solve_58490d8a
