"""Auto-generated identity stub for ARC-AGI-2 task b0039139 (split: evaluation)."""

from __future__ import annotations

from collections import deque
from typing import List, Tuple


Grid = List[List[int]]


def findFullLines(grid: Grid) -> Tuple[List[int], List[int]]:
    rows, cols = len(grid), len(grid[0])
    row_breaks = [r for r in range(rows) if all(cell == 1 for cell in grid[r])]
    col_breaks = [c for c in range(cols) if all(grid[r][c] == 1 for r in range(rows))]
    return row_breaks, col_breaks


def _slice_by_breaks(grid: Grid, breaks: List[int], axis: str) -> List[Grid]:
    if not breaks:
        return []
    rows, cols = len(grid), len(grid[0])
    segments: List[Grid] = []
    prev = -1
    limit = rows if axis == "row" else cols
    for idx in breaks + [limit]:
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


def extractSegments(grid: Grid, separators: Tuple[List[int], List[int]]) -> Tuple[List[Grid], List[Grid]]:
    row_breaks, col_breaks = separators
    row_segments = _slice_by_breaks(grid, row_breaks, "row") if row_breaks else []
    col_segments = _slice_by_breaks(grid, col_breaks, "col") if col_breaks else []
    return row_segments, col_segments


def summarisePattern(segment: Grid, target: int) -> Grid:
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


def _count_components(segment: Grid, target: int) -> int:
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


def _dominant_color(segment: Grid) -> int:
    counts: dict[int, int] = {}
    for row in segment:
        for value in row:
            if value not in (0, 1):
                counts[value] = counts.get(value, 0) + 1
    if counts:
        return max(counts.items(), key=lambda kv: kv[1])[0]
    for row in segment:
        for value in row:
            if value != 1:
                return value
    return 0


def _build_vertical(pattern: Grid, repeats: int, main_color: int, gap_color: int) -> Grid:
    height = len(pattern)
    width = repeats * len(pattern[0]) + (repeats - 1)
    result = [[gap_color] * width for _ in range(height)]
    pattern_width = len(pattern[0])
    for idx in range(repeats):
        start_col = idx * (pattern_width + 1)
        for r in range(height):
            for c in range(pattern_width):
                result[r][start_col + c] = main_color if pattern[r][c] else gap_color
        if idx < repeats - 1:
            gap_col = start_col + pattern_width
            for r in range(height):
                result[r][gap_col] = gap_color
    return result


def _build_horizontal(pattern: Grid, repeats: int, main_color: int, gap_color: int) -> Grid:
    pattern_height = len(pattern)
    height = repeats * pattern_height + (repeats - 1)
    width = len(pattern[0])
    result = [[gap_color] * width for _ in range(height)]
    for idx in range(repeats):
        start_row = idx * (pattern_height + 1)
        for r in range(pattern_height):
            for c in range(width):
                result[start_row + r][c] = main_color if pattern[r][c] else gap_color
        if idx < repeats - 1:
            gap_row = start_row + pattern_height
            for c in range(width):
                result[gap_row][c] = gap_color
    return result


def rebuildByOrientation(pattern: Grid, segment_groups: Tuple[List[Grid], List[Grid]]) -> Grid:
    row_segments, col_segments = segment_groups
    if row_segments:
        segs = row_segments
        repeats = _count_components(segs[1], 3) if len(segs) > 1 else 1
        main_color = _dominant_color(segs[2]) if len(segs) > 2 else 0
        gap_color = _dominant_color(segs[3]) if len(segs) > 3 else 0
        return _build_horizontal(pattern, repeats, main_color, gap_color)
    if col_segments:
        segs = col_segments
        repeats = _count_components(segs[1], 3) if len(segs) > 1 else 1
        main_color = _dominant_color(segs[2]) if len(segs) > 2 else 0
        gap_color = _dominant_color(segs[3]) if len(segs) > 3 else 0
        return _build_vertical(pattern, repeats, main_color, gap_color)
    # Fallback shouldn't be reached due to guard in solver
    return []  # type: ignore[return-value]


# === DSL-style main, must match abstractions.md ===
def solve_b0039139(grid: Grid) -> Grid:
    separators = findFullLines(grid)
    segment_groups = extractSegments(grid, separators)
    row_segments, col_segments = segment_groups
    primary_segments = row_segments or col_segments
    if not primary_segments:
        return grid
    pattern = summarisePattern(primary_segments[0], 4)
    return rebuildByOrientation(pattern, segment_groups)


p = solve_b0039139
