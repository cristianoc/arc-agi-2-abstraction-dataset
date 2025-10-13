"""Solver for ARC-AGI-2 task 3e6067c3."""

from collections import Counter, defaultdict


def solve_3e6067c3(grid):
    """Connect colored nodes following the color order encoded on the hint row."""
    height = len(grid)
    width = len(grid[0]) if grid else 0

    if not grid or not grid[0]:
        return []

    background = Counter(cell for row in grid for cell in row).most_common(1)[0][0]

    visited = [[False] * width for _ in range(height)]
    components = []

    for r in range(height):
        for c in range(width):
            if visited[r][c]:
                continue

            color = grid[r][c]
            visited[r][c] = True

            if color in (background, 1):
                continue

            stack = [(r, c)]
            cells = []

            while stack:
                rr, cc = stack.pop()
                cells.append((rr, cc))

                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[nr][nc] == color:
                        visited[nr][nc] = True
                        stack.append((nr, nc))

            rows = [rr for rr, _ in cells]
            cols = [cc for _, cc in cells]
            components.append(
                {
                    "color": color,
                    "min_row": min(rows),
                    "max_row": max(rows),
                    "min_col": min(cols),
                    "max_col": max(cols),
                }
            )

    hint_row = max(
        (r for r, row in enumerate(grid) if any(cell not in (background, 1) for cell in row)),
        default=None,
    )

    if hint_row is None:
        return [row[:] for row in grid]

    hints = [comp for comp in components if comp["min_row"] == comp["max_row"] == hint_row]
    hints.sort(key=lambda comp: comp["min_col"])

    sequence = [comp["color"] for comp in hints]

    nodes = [comp for comp in components if comp not in hints]

    nodes_by_color = defaultdict(list)
    for node in nodes:
        nodes_by_color[node["color"]].append(node)

    for bucket in nodes_by_color.values():
        bucket.sort(key=lambda comp: (comp["min_row"], comp["min_col"]))

    path_nodes = []
    for color in sequence:
        bucket = nodes_by_color.get(color)
        if not bucket:
            return [row[:] for row in grid]
        path_nodes.append(bucket.pop(0))

    result = [row[:] for row in grid]

    if len(path_nodes) <= 1:
        return result

    def paint_vertical(src, dst, color):
        col_start = max(src["min_col"], dst["min_col"])
        col_end = min(src["max_col"], dst["max_col"])

        if col_start > col_end:
            return

        if src["max_row"] < dst["min_row"]:
            r_start = src["max_row"] + 1
            r_end = dst["min_row"] - 1
        elif dst["max_row"] < src["min_row"]:
            r_start = dst["max_row"] + 1
            r_end = src["min_row"] - 1
        else:
            return

        for r in range(r_start, r_end + 1):
            for c in range(col_start, col_end + 1):
                if 0 <= r < height and 0 <= c < width and grid[r][c] == background:
                    result[r][c] = color

    def paint_horizontal(src, dst, color):
        row_start = max(src["min_row"], dst["min_row"])
        row_end = min(src["max_row"], dst["max_row"])

        if row_start > row_end:
            return

        if src["max_col"] < dst["min_col"]:
            c_start = src["max_col"] + 1
            c_end = dst["min_col"] - 1
        elif dst["max_col"] < src["min_col"]:
            c_start = dst["max_col"] + 1
            c_end = src["min_col"] - 1
        else:
            return

        for r in range(row_start, row_end + 1):
            for c in range(c_start, c_end + 1):
                if 0 <= r < height and 0 <= c < width and grid[r][c] == background:
                    result[r][c] = color

    for src, dst in zip(path_nodes, path_nodes[1:]):
        color = src["color"]
        paint_vertical(src, dst, color)
        paint_horizontal(src, dst, color)

    return result


p = solve_3e6067c3
# TODO: initial placeholder patch per instructions
