"""Solver for ARC-AGI-2 task 291dc1e1 (split: evaluation)."""

from typing import Iterable, List, Sequence


BACKGROUND = 8
HEADER_COLORS = {0, 1, 2}


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


def solve_291dc1e1(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    oriented = grid
    use_transpose = len(grid[0]) <= len(grid)
    if use_transpose:
        oriented = _transpose(oriented)

    cores = _trim_header_column(oriented)
    segments_per_row = [_extract_segments(row) for row in cores]
    max_width = max((len(seg) for segs in segments_per_row for seg in segs), default=0)
    if max_width == 0:
        return [list(row) for row in grid]

    groups = _contiguous_groups([bool(segs) for segs in segments_per_row])
    result: List[List[int]] = []
    for group in groups:
        ordered_rows = list(group)
        if use_transpose:
            ordered_rows.reverse()

        reverse_segments = any(cores[idx] and cores[idx][-1] != BACKGROUND for idx in ordered_rows)
        ordered_segment_lists: List[List[List[int]]] = []
        for idx in ordered_rows:
            segs = segments_per_row[idx]
            ordered_segment_lists.append(list(reversed(segs)) if reverse_segments else segs)

        max_segments = max(len(segs) for segs in ordered_segment_lists)
        for position in range(max_segments):
            for segs in ordered_segment_lists:
                if position < len(segs):
                    result.append(_inflate(segs[position], max_width))

    return result


p = solve_291dc1e1
