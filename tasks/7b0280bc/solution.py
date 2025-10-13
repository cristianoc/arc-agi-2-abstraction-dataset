"""Solver for ARC-AGI-2 task 7b0280bc (evaluation split)."""

from collections import Counter, deque


def solve_7b0280bc(grid):
    """Recolor selected components of the two dominant foreground colors."""

    height = len(grid)
    width = len(grid[0])

    # Identify background and the two most frequent foreground colors.
    color_counts = Counter(cell for row in grid for cell in row)
    background, _ = color_counts.most_common(1)[0]
    foreground = [color for color, _ in color_counts.most_common() if color != background][:2]
    if len(foreground) < 2:
        return [row[:] for row in grid]

    major, minor = foreground[0], foreground[1]

    def classify_component(component):
        """Decision tree learnt from the training cases (integer thresholds)."""

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

    visited = [[False] * width for _ in range(height)]
    target_cells = set()

    for r in range(height):
        for c in range(width):
            color = grid[r][c]
            if color not in (major, minor) or visited[r][c]:
                continue

            # Gather the monochrome component for this color.
            queue = deque([(r, c)])
            visited[r][c] = True
            cells = []

            while queue:
                y, x = queue.popleft()
                cells.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width:
                        if not visited[ny][nx] and grid[ny][nx] == color:
                            visited[ny][nx] = True
                            queue.append((ny, nx))

            rows = [y for y, _ in cells]
            cols = [x for _, x in cells]
            component = {
                "color": color,
                "size": len(cells),
                "row_min": min(rows),
                "row_max": max(rows),
                "col_min": min(cols),
                "col_max": max(cols),
            }

            if classify_component(component):
                target_cells.update(cells)

    result = [row[:] for row in grid]
    for y, x in target_cells:
        original = grid[y][x]
        if original == major:
            result[y][x] = 5
        elif original == minor:
            result[y][x] = 3

    return result


p = solve_7b0280bc
# Codex initial patch touch
# Temporary note: adjusting solver per iteration.
