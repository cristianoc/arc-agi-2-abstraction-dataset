"""Auto-generated identity stub for ARC-AGI-2 task b0039139 (split: evaluation)."""

from collections import deque


def solve_b0039139(grid):
    """Solve ARC task b0039139."""

    rows, cols = len(grid), len(grid[0])

    def full_lines(axis):
        if axis == "row":
            return [r for r in range(rows) if all(cell == 1 for cell in grid[r])]
        return [c for c in range(cols) if all(grid[r][c] == 1 for r in range(rows))]

    def extract_segments(boundaries, axis):
        segments = []
        prev = -1
        limit = rows if axis == "row" else cols
        for idx in boundaries + [limit]:
            start = prev + 1
            end = idx - 1
            if start <= end:
                if axis == "row":
                    segment = [grid[r][:] for r in range(start, end + 1)]
                else:
                    segment = [row[start : end + 1] for row in grid]
                segments.append(segment)
            prev = idx
        return segments

    def bounding_pattern(segment, target):
        coords = [
            (r, c)
            for r, row in enumerate(segment)
            for c, value in enumerate(row)
            if value == target
        ]
        if not coords:
            return [[1]]
        r0 = min(r for r, _ in coords)
        r1 = max(r for r, _ in coords)
        c0 = min(c for _, c in coords)
        c1 = max(c for _, c in coords)
        return [
            [1 if segment[r][c] == target else 0 for c in range(c0, c1 + 1)]
            for r in range(r0, r1 + 1)
        ]

    def count_components(segment, target):
        height, width = len(segment), len(segment[0])
        seen = [[False] * width for _ in range(height)]
        total = 0
        for r in range(height):
            for c in range(width):
                if segment[r][c] == target and not seen[r][c]:
                    total += 1
                    queue = deque([(r, c)])
                    seen[r][c] = True
                    while queue:
                        x, y = queue.popleft()
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < height and 0 <= ny < width:
                                if not seen[nx][ny] and segment[nx][ny] == target:
                                    seen[nx][ny] = True
                                    queue.append((nx, ny))
        return max(total, 1)

    def dominant_color(segment):
        counts = {}
        for row in segment:
            for value in row:
                if value not in (0, 1):
                    counts[value] = counts.get(value, 0) + 1
        if counts:
            return max(counts, key=counts.get)
        for row in segment:
            for value in row:
                if value != 1:
                    return value
        return 0

    def build_vertical(pattern, repeats, main_color, gap_color):
        height = len(pattern)
        width = repeats * len(pattern[0]) + (repeats - 1)
        result = [[gap_color] * width for _ in range(height)]
        pattern_width = len(pattern[0])
        for idx in range(repeats):
            start_col = idx * (pattern_width + 1)
            for r in range(height):
                for c in range(pattern_width):
                    if pattern[r][c]:
                        result[r][start_col + c] = main_color
                    else:
                        result[r][start_col + c] = gap_color
            if idx < repeats - 1:
                gap_col = start_col + pattern_width
                for r in range(height):
                    result[r][gap_col] = gap_color
        return result

    def build_horizontal(pattern, repeats, main_color, gap_color):
        pattern_height = len(pattern)
        height = repeats * pattern_height + (repeats - 1)
        width = len(pattern[0])
        result = [[gap_color] * width for _ in range(height)]
        for idx in range(repeats):
            start_row = idx * (pattern_height + 1)
            for r in range(pattern_height):
                for c in range(width):
                    if pattern[r][c]:
                        result[start_row + r][c] = main_color
                    else:
                        result[start_row + r][c] = gap_color
            if idx < repeats - 1:
                gap_row = start_row + pattern_height
                for c in range(width):
                    result[gap_row][c] = gap_color
        return result

    ones_rows = full_lines("row")
    ones_cols = full_lines("col")

    if ones_rows:
        segments = extract_segments(ones_rows, "row")
        if len(segments) < 4:
            return [row[:] for row in grid]
        seg0, seg1, seg2, seg3 = segments[:4]
        pattern = bounding_pattern(seg0, 4)
        repeats = count_components(seg1, 3)
        main_color = dominant_color(seg2)
        gap_color = dominant_color(seg3)
        return build_horizontal(pattern, repeats, main_color, gap_color)

    if ones_cols:
        segments = extract_segments(ones_cols, "col")
        if len(segments) < 4:
            return [row[:] for row in grid]
        seg0, seg1, seg2, seg3 = segments[:4]
        pattern = bounding_pattern(seg0, 4)
        repeats = count_components(seg1, 3)
        main_color = dominant_color(seg2)
        gap_color = dominant_color(seg3)
        return build_vertical(pattern, repeats, main_color, gap_color)

    return [row[:] for row in grid]


p = solve_b0039139
