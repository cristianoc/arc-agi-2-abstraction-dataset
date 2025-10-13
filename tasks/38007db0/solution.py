"""Solver for ARC-AGI-2 task 38007db0."""

from __future__ import annotations

from collections import Counter
from typing import List, Sequence, Tuple


Grid = List[List[int]]


def _non_border_row_segments(grid: Grid, border_color: int) -> List[Tuple[int, int]]:
    """Return (start, end) index pairs for contiguous non-border row runs."""

    segments: List[Tuple[int, int]] = []
    start = None
    for idx, row in enumerate(grid):
        is_border_row = all(value == border_color for value in row)
        if is_border_row:
            if start is not None:
                segments.append((start, idx))
                start = None
            continue
        if start is None:
            start = idx
    if start is not None:
        segments.append((start, len(grid)))
    return segments


def _non_border_col_segments(grid: Grid, border_color: int) -> List[Tuple[int, int]]:
    """Return (start, end) index pairs for contiguous non-border column runs."""

    segments: List[Tuple[int, int]] = []
    start = None
    width = len(grid[0])
    for idx in range(width):
        is_border_col = all(row[idx] == border_color for row in grid)
        if is_border_col:
            if start is not None:
                segments.append((start, idx))
                start = None
            continue
        if start is None:
            start = idx
    if start is not None:
        segments.append((start, width))
    return segments


def _choose_unique_block(blocks: Sequence[Tuple[Tuple[int, ...], ...]]) -> int:
    """Return the index of the block that stands out within its row."""

    if not blocks:
        return 0

    counts = Counter(blocks)
    min_count = min(counts.values())
    candidate_indices = [idx for idx, block in enumerate(blocks) if counts[block] == min_count]
    if len(candidate_indices) == 1:
        return candidate_indices[0]

    mid = (len(blocks) - 1) / 2.0
    return min(candidate_indices, key=lambda idx: (abs(idx - mid), idx))


def solve_38007db0(grid: Grid) -> Grid:
    """Select the unique interior block on each block-row and keep only those."""

    if not grid or not grid[0]:
        return [row[:] for row in grid]

    border_color = grid[0][0]
    row_segments = _non_border_row_segments(grid, border_color)
    col_segments = _non_border_col_segments(grid, border_color)

    if not row_segments or not col_segments:
        return [row[:] for row in grid]

    width_counts = Counter(end - start for start, end in col_segments)
    block_width = max(width_counts, key=width_counts.get)
    output_width = block_width + 2

    result: Grid = [[border_color] * output_width for _ in grid]

    for row_start, row_end in row_segments:
        blocks: List[Tuple[Tuple[int, ...], ...]] = []
        for col_start, col_end in col_segments:
            block = tuple(
                tuple(grid[r][c] for c in range(col_start, col_end))
                for r in range(row_start, row_end)
            )
            blocks.append(block)

        chosen_index = _choose_unique_block(blocks)
        chosen_block = blocks[chosen_index]

        for offset, source_row in enumerate(chosen_block):
            target_row = row_start + offset
            row_values = list(source_row)
            if len(row_values) < block_width:
                row_values.extend([border_color] * (block_width - len(row_values)))
            elif len(row_values) > block_width:
                row_values = row_values[:block_width]
            result[target_row][1 : 1 + block_width] = row_values

    return result


p = solve_38007db0
