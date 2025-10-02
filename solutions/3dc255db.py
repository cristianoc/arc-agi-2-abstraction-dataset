"""Solver for ARC-AGI-2 task 3dc255db (split: evaluation)."""

from collections import deque


def _nonzero_colors(grid):
    return sorted({cell for row in grid for cell in row if cell})


def _bbox(coords):
    rows = [r for r, _ in coords]
    cols = [c for _, c in coords]
    return min(rows), max(rows), min(cols), max(cols)


def _components(grid, color):
    height = len(grid)
    width = len(grid[0])
    seen = set()
    comps = []
    for r in range(height):
        for c in range(width):
            if grid[r][c] != color or (r, c) in seen:
                continue
            queue = deque([(r, c)])
            seen.add((r, c))
            comp = []
            while queue:
                x, y = queue.popleft()
                comp.append((x, y))
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if (
                        0 <= nx < height
                        and 0 <= ny < width
                        and grid[nx][ny] == color
                        and (nx, ny) not in seen
                    ):
                        seen.add((nx, ny))
                        queue.append((nx, ny))
            comps.append(comp)
    return comps


def solve_3dc255db(grid):
    """Solve task 3dc255db by relocating intruder colors to the edge of their host."""
    height = len(grid)
    width = len(grid[0])
    output = [row[:] for row in grid]

    colors = _nonzero_colors(grid)
    color_cells = {
        color: [(r, c) for r in range(height) for c in range(width) if grid[r][c] == color]
        for color in colors
    }
    bboxes = {color: _bbox(coords) for color, coords in color_cells.items()}
    areas = {color: len(coords) for color, coords in color_cells.items()}
    components = {color: _components(grid, color) for color in colors}

    processed_components = set()
    for host in colors:
        hr0, hr1, hc0, hc1 = bboxes[host]
        host_height = hr1 - hr0 + 1
        host_width = hc1 - hc0 + 1

        for color in colors:
            if color == host or areas[host] <= areas[color]:
                continue

            to_move = []
            for comp in components[color]:
                comp_key = (color, tuple(sorted(comp)))
                if comp_key in processed_components:
                    continue

                rows = [r for r, _ in comp]
                cols = [c for _, c in comp]
                cr0, cr1 = min(rows), max(rows)
                cc0, cc1 = min(cols), max(cols)

                if hr0 <= cr0 and cr1 <= hr1 and hc0 <= cc0 and cc1 <= hc1:
                    to_move.extend(comp)
                    processed_components.add(comp_key)

            if not to_move:
                continue

            for r, c in to_move:
                output[r][c] = 0

            avg_row = sum(r for r, _ in to_move) / len(to_move)
            avg_col = sum(c for _, c in to_move) / len(to_move)
            center_row = (hr0 + hr1) / 2
            center_col = (hc0 + hc1) / 2
            delta_row = avg_row - center_row
            delta_col = avg_col - center_col
            abs_row = abs(delta_row)
            abs_col = abs(delta_col)

            if abs_col > abs_row:
                axis = "horizontal"
            elif abs_col < abs_row:
                axis = "vertical"
            else:
                axis = "horizontal" if host_width >= host_height else "vertical"

            if axis == "horizontal":
                direction = "east" if delta_col < 0 else "west"
                unique_cols = sorted({c for _, c in to_move})
                length = len(unique_cols)
                if length == 0:
                    continue

                row_line = hr1 - 1 if host_height > 1 else hr1
                row_line = max(hr0, min(hr1, row_line))

                if direction == "east":
                    start_col = hc1 + 1
                    for idx in range(length):
                        col = start_col + idx
                        if 0 <= col < width:
                            output[row_line][col] = color
                else:
                    start_col = hc0 - length
                    for idx in range(length):
                        col = start_col + idx
                        if 0 <= col < width:
                            output[row_line][col] = color

            else:
                direction = "north" if delta_row > 0 else "south"
                unique_rows = sorted({r for r, _ in to_move})
                length = len(unique_rows)
                if length == 0:
                    continue

                sorted_cols = sorted(c for _, c in to_move)
                col_line = sorted_cols[len(sorted_cols) // 2]
                col_line = max(hc0, min(hc1, col_line))

                if direction == "north":
                    start_row = hr0 - length
                    for idx in range(length):
                        row = start_row + idx
                        if 0 <= row < height:
                            output[row][col_line] = color
                else:
                    start_row = hr1 + 1
                    for idx in range(length):
                        row = start_row + idx
                        if 0 <= row < height:
                            output[row][col_line] = color

    return output


p = solve_3dc255db
