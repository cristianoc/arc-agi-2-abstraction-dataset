"""Solver for ARC-AGI-2 task 291dc1e1 (split: evaluation)."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple


BACKGROUND = 8
HEADER_COLORS = {0, 1, 2}

# DSL type aliases
Grid = List[List[int]]
Range = range
Segment = List[int]


def _transpose(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    return [list(col) for col in zip(*grid)]


def _trim_header_column(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    return [list(row[1:]) for row in grid]


def _extract_segments(row: Sequence[int]) -> List[List[int]]:
    segments: List[List[int]] = []
    current: List[int] = []
    for value in row:
        if value == BACKGROUND:
            if current and not all(v in HEADER_COLORS for v in current):
                segments.append(current[:])
            current.clear()
        else:
            current.append(value)
    if current and not all(v in HEADER_COLORS for v in current):
        segments.append(current)
    return segments


def _contiguous_groups(non_empty_flags: Sequence[bool]) -> List[range]:
    groups: List[range] = []
    start = None
    for idx, has_segments in enumerate(non_empty_flags):
        if has_segments:
            if start is None:
                start = idx
        else:
            if start is not None:
                groups.append(range(start, idx))
                start = None
    if start is not None:
        groups.append(range(start, len(non_empty_flags)))
    return groups


def _inflate(segment: Sequence[int], width: int) -> List[int]:
    remaining = width - len(segment)
    if remaining <= 0:
        return list(segment[:width])
    left = remaining // 2
    right = remaining - left
    return [BACKGROUND] * left + list(segment) + [BACKGROUND] * right

# === DSL helper wrappers (pure API layer) ===

def maybeTranspose(grid: Sequence[Sequence[int]]) -> Tuple[Grid, bool]:
    use_transpose = len(grid[0]) <= len(grid)
    oriented = _transpose(grid) if use_transpose else [list(row) for row in grid]
    return oriented, use_transpose


def trimHeader(grid: Sequence[Sequence[int]]) -> Grid:
    return _trim_header_column(grid)


def extractSegments(row: Sequence[int]) -> List[Segment]:
    return _extract_segments(row)


def groupRows(flags: Sequence[bool]) -> List[Range]:
    return _contiguous_groups(flags)


def weaveSegments(
    groups: Sequence[Range],
    segments_per_row: Sequence[List[Segment]],
    cores: Sequence[Sequence[int]],
    max_width: int,
    reverse_rows: bool,
) -> Grid:
    result: Grid = []
    for group in groups:
        row_indices = list(group)
        if reverse_rows:
            row_indices.reverse()

        reverse_segments = any(cores[idx] and cores[idx][-1] != BACKGROUND for idx in row_indices)

        ordered_lists: List[List[Segment]] = [
            list(reversed(segments_per_row[idx])) if reverse_segments else segments_per_row[idx]
            for idx in row_indices
        ]
        if not ordered_lists:
            continue

        max_segments = max(len(lst) for lst in ordered_lists)
        for position in range(max_segments):
            for segs in ordered_lists:
                if position < len(segs):
                    result.append(_inflate(segs[position], max_width))
    return result


def restoreOrientation(grid: Grid, transposed: bool) -> Grid:  # identity for this task
    return grid


def solve_291dc1e1(grid: Grid) -> Grid:
    oriented, transposed = maybeTranspose(grid)
    cores = trimHeader(oriented)
    segments_per_row = [extractSegments(row) for row in cores]
    max_width = max((len(seg) for segs in segments_per_row for seg in segs), default=0)
    if max_width == 0:
        return [list(row) for row in grid]
    groups = groupRows([bool(segs) for segs in segments_per_row])
    woven = weaveSegments(groups, segments_per_row, cores, max_width, transposed)
    return restoreOrientation(woven, transposed)


p = solve_291dc1e1
