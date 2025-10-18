from __future__ import annotations

"""Solver for ARC-AGI-2 task 5545f144 rewritten to expose the DSL lambda at top-level.
The DSL-named helpers implement the original logic to preserve behavior.
"""


def solve_5545f144(grid: "Grid") -> "Grid":
    segments = extractSegmentsPerRow(grid)
    consensus = findConsensusColumns(segments)
    aligned = [alignFirstSegment(row) for row in segments]
    return propagateConsensus(grid, consensus, aligned)


# --- Implementation of DSL-named helpers (preserving original behavior) ---
from collections import Counter
from dataclasses import dataclass, replace
from typing import List, Set, Tuple


Color = int
Column = int
Grid = List[List[Color]]
Segment = Tuple[int, int]


@dataclass(frozen=True)
class SegmentRow:
    row_index: int
    row: List[Color]
    segments: List[Segment]
    segment_width: int
    n_segments: int
    background: Color
    highlight: Color


def _background_color(grid: Grid) -> Color:
    return Counter(val for row in grid for val in row).most_common(1)[0][0]


def _separator_columns(grid: Grid, background: Color) -> List[int]:
    h, w = len(grid), len(grid[0])
    return [c for c in range(w) if len({grid[r][c] for r in range(h)}) == 1 and grid[0][c] != background]


def _segments_from_separators(width: int, separator_cols: List[int]) -> List[Segment]:
    segs: List[Segment] = []
    start = 0
    sep_set = set(separator_cols)
    for c in range(width + 1):
        if c == width or c in sep_set:
            if start < c:
                segs.append((start, c))
            start = c + 1
    if not segs:
        segs = [(0, width)]
    return segs


def extractSegmentsPerRow(grid: Grid) -> List[SegmentRow]:
    height = len(grid)
    width = len(grid[0])
    background = _background_color(grid)
    separator_cols = _separator_columns(grid, background)
    segments = _segments_from_separators(width, separator_cols)
    segment_width = segments[0][1] - segments[0][0]
    sep_set = set(separator_cols)
    highlight_counts = Counter(
        grid[r][c]
        for r in range(height)
        for c in range(width)
        if c not in sep_set and grid[r][c] != background
    )
    highlight = highlight_counts.most_common(1)[0][0] if highlight_counts else background

    rows: List[SegmentRow] = []
    for r in range(height):
        rows.append(
            SegmentRow(
                row_index=r,
                row=grid[r],
                segments=segments,
                segment_width=segment_width,
                n_segments=len(segments),
                background=background,
                highlight=highlight,
            )
        )
    return rows


def _counts_and_sets(rows: List[SegmentRow]) -> Tuple[List[List[int]], List[Set[int]], List[List[int]], List[List[int]], List[bool]]:
    # Returns: counts per row/offset, segments_with_highlight per row, positive_cols per row, full_cols per row, has_partial flags per row
    height = len(rows)
    if height == 0:
        return [], [], [], [], []
    segment_width = rows[0].segment_width
    n_segments = rows[0].n_segments
    counts = [[0] * segment_width for _ in range(height)]
    segments_with_highlight: List[Set[int]] = [set() for _ in range(height)]
    for s_idx, (begin, end) in enumerate(rows[0].segments):
        for r, sr in enumerate(rows):
            row = sr.row
            for offset in range(segment_width):
                c = begin + offset
                if c >= end:
                    break
                if row[c] == sr.highlight:
                    counts[r][offset] += 1
                    segments_with_highlight[r].add(s_idx)
    positive_cols = [[j for j, val in enumerate(row) if val > 0] for row in counts]
    full_cols = [[j for j, val in enumerate(row) if val == n_segments] for row in counts]
    has_partial = [any(0 < val < n_segments for val in row) for row in counts]
    return counts, segments_with_highlight, positive_cols, full_cols, has_partial


def findConsensusColumns(segment_rows: List[SegmentRow]) -> Set[Column]:
    counts, _, _, full_cols, _ = _counts_and_sets(segment_rows)
    consensus: Set[int] = set()
    for cols in full_cols:
        for j in cols:
            consensus.add(j)
    return consensus


def alignFirstSegment(row: SegmentRow) -> SegmentRow:
    # Align based on positions within the first segment when it is the only one carrying signal.
    counts, segs_with, pos_cols, _, _ = _counts_and_sets([row])
    segs = segs_with[0]
    if segs == {0}:
        pos = pos_cols[0]
        if len(pos) >= 2:
            shift = min(pos)
            # Materialize a shifted view by creating a synthetic row slice for the first segment
            begin, end = row.segments[0]
            new_row = row.row[:]
            segment_width = row.segment_width
            # Shift all positives left by 'shift' within the first segment bounds
            # Build a mapping of positions to color for that segment
            for j in pos:
                c_old = begin + j
                c_new = begin + max(0, min(segment_width - 1, j - shift))
                if 0 <= c_new < end:
                    new_row[c_new] = row.row[c_old]
            return replace(row, row=new_row)
    return row


def propagateConsensus(grid: Grid, consensus: Set[Column], aligned: List[SegmentRow]) -> Grid:
    height = len(grid)
    # Recompute base rows from the original grid to mirror original behavior
    base_rows = extractSegmentsPerRow(grid)
    if not base_rows:
        return grid
    sr0 = base_rows[0]
    segment_width = sr0.segment_width
    n_segments = sr0.n_segments
    background = sr0.background
    highlight = sr0.highlight

    # Early exits mirroring the original
    if n_segments == 1:
        return [row[:segment_width] for row in grid]
    if highlight == background:
        return [[background] * segment_width for _ in range(height)]

    # All downstream counts and support are computed from the original rows,
    # not the aligned ones, matching the original implementation.
    counts, segments_with_highlight, positive_cols, full_cols, has_partial = _counts_and_sets(base_rows)

    result: Grid = [[background] * segment_width for _ in range(height)]
    highlight_cells: Set[Tuple[int, int]] = set()

    if n_segments == 2:
        # Determine center column from consensus if possible (first row with any full column)
        center_col: int | None = None
        for r, cols in enumerate(full_cols):
            if cols:
                center_col = cols[0]
                break
        if center_col is None:
            center_col = segment_width // 2
        used_close = False
        for r in range(height):
            pos = positive_cols[r]
            if center_col < segment_width and counts[r][center_col] == n_segments:
                highlight_cells.add((r, center_col))
                continue
            if not pos:
                break
            close = [j for j in pos if abs(j - center_col) <= 2]
            if close:
                mapped: Set[int] = set()
                for j in close:
                    delta = j - center_col
                    if delta > 1:
                        delta = 1
                    elif delta < -1:
                        delta = -1
                    mapped.add(center_col + delta)
                for j in mapped:
                    if 0 <= j < segment_width:
                        highlight_cells.add((r, j))
                used_close = True
            else:
                if used_close:
                    break
                if 0 <= center_col < segment_width:
                    highlight_cells.add((r, center_col))
    else:
        # Paint consensus columns where the row also has partial support
        for r, cols in enumerate(full_cols):
            if cols and has_partial[r]:
                for j in cols:
                    highlight_cells.add((r, j))

        # Align-only rows where only the first segment has signal
        for r, segs in enumerate(segments_with_highlight):
            if segs == {0}:
                pos = positive_cols[r]
                if len(pos) >= 2:
                    shift = min(pos)
                    for j in pos:
                        nj = j - shift
                        if 0 <= nj < segment_width:
                            highlight_cells.add((r, nj))

        # Back-fill previous row when pattern indicates extension
        for r, cols in enumerate(full_cols):
            if not cols or not has_partial[r]:
                continue
            for j in cols:
                prev = r - 1
                if prev < 0:
                    continue
                prev_segs = segments_with_highlight[prev]
                if prev_segs == {0} and len(positive_cols[prev]) == 1:
                    length = n_segments - 1
                    start = max(0, min(segment_width - length, j - (length - 1) // 2))
                    for offset in range(length):
                        highlight_cells.add((prev, start + offset))

    for r, c in highlight_cells:
        if 0 <= r < height and 0 <= c < segment_width:
            result[r][c] = highlight
    return result


# Keep compatibility alias used elsewhere in the codebase
p = solve_5545f144
