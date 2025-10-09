"""Solver for ARC task 9aaea919 (evaluation split)."""

from collections import Counter


def _get_background(grid):
    flat = [cell for row in grid for cell in row]
    return Counter(flat).most_common(1)[0][0]


def _find_cross_columns(grid):
    height, width = len(grid), len(grid[0])
    visited = [[False] * width for _ in range(height)]
    columns = {}

    for r in range(height):
        for c in range(width):
            if visited[r][c]:
                continue
            color = grid[r][c]
            stack = [(r, c)]
            visited[r][c] = True
            cells = []

            while stack:
                x, y = stack.pop()
                cells.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < height and 0 <= ny < width and not visited[nx][ny] and grid[nx][ny] == color:
                        visited[nx][ny] = True
                        stack.append((nx, ny))

            if len(cells) != 11:
                continue

            rows = [x for x, _ in cells]
            cols = [y for _, y in cells]
            min_r, max_r = min(rows), max(rows)
            min_c, max_c = min(cols), max(cols)

            if max_r - min_r != 2 or max_c - min_c != 4:
                continue

            start_col = min_c
            pattern = [[grid[min_r + i][min_c + j] for j in range(5)] for i in range(3)]
            info = columns.setdefault(
                start_col,
                {
                    "rows": [],
                    "color": color,
                    "pattern": pattern,
                    "min_c": min_c,
                    "max_c": max_c,
                },
            )
            info["rows"].append(min_r)

    for info in columns.values():
        info["rows"].sort()

    return columns


def _instruction_segments(grid, background):
    row = grid[-1]
    segments = []
    start = 0
    current = row[0]

    for idx, val in enumerate(row):
        if val != current:
            segments.append((current, start, idx - 1))
            start = idx
            current = val
    segments.append((current, start, len(row) - 1))

    return [seg for seg in segments if seg[0] != background]


def _map_segments_to_columns(segments, columns):
    if not columns:
        return {}

    mapping = {}
    for color, start, end in segments:
        center = (start + end) // 2
        matched = None
        for col_start, info in columns.items():
            if info["min_c"] <= center <= info["max_c"]:
                matched = col_start
                break
        if matched is None:
            matched = min(
                columns.keys(),
                key=lambda c: abs(((columns[c]["min_c"] + columns[c]["max_c"]) // 2) - center),
            )
        mapping.setdefault(matched, []).append(color)

    return mapping


def _draw_pattern(grid, top, left, pattern):
    for dr, row in enumerate(pattern):
        target = grid[top + dr]
        for dc, val in enumerate(row):
            target[left + dc] = val


def _recolor_column(grid, info, background, new_color):
    original_color = info["color"]
    pattern = info["pattern"]
    recolored = [
        [new_color if cell == original_color else background if cell == background else cell for cell in row]
        for row in pattern
    ]

    for top in info["rows"]:
        _draw_pattern(grid, top, info["min_c"], recolored)

    info["pattern"] = recolored
    info["color"] = new_color


def _extend_column(grid, info, count):
    if count <= 0:
        return

    step = 4  # 3 rows of the plus and one row gap
    top = min(info["rows"])
    pattern = info["pattern"]

    added = 0
    while added < count:
        new_top = top - step * (added + 1)
        if new_top < 0:
            break
        _draw_pattern(grid, new_top, info["min_c"], pattern)
        added += 1


def solve_9aaea919(grid):
    """Transform scoreboard-style plus grids per bottom-row instructions."""
    result = [row[:] for row in grid]

    background = _get_background(result)
    columns = _find_cross_columns(result)
    segments = _instruction_segments(result, background)
    mapping = _map_segments_to_columns(segments, columns)

    color2_columns = [col for col, colors in mapping.items() if 2 in colors]
    total_crosses = sum(len(columns[col]["rows"]) for col in color2_columns)

    for col in color2_columns:
        _recolor_column(result, columns[col], background, 5)

    for col, colors in mapping.items():
        if 3 in colors:
            _extend_column(result, columns[col], total_crosses)

    for _, start, end in segments:
        for c in range(start, end + 1):
            result[-1][c] = background

    return result


p = solve_9aaea919
