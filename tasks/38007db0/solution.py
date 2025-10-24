"""Solver for ARC-AGI-2 task 38007db0."""

from __future__ import annotations

from collections import Counter
from typing import List, Sequence, Tuple, NamedTuple


Grid = List[List[int]]
Block = Tuple[Tuple[int, ...], ...]
BlockRow = List[Block]


class BorderSpec(NamedTuple):
    border_color: int
    row_segments: List[Tuple[int, int]]
    col_segments: List[Tuple[int, int]]
    block_width: int
    output_width: int
    identity: bool


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

def detectBorders(grid: Grid) -> BorderSpec:
    if not grid or not grid[0]:
        return BorderSpec(0, [], [], 0, 0, True)

    border_color = grid[0][0]
    row_segments = _non_border_row_segments(grid, border_color)
    col_segments = _non_border_col_segments(grid, border_color)

    if not row_segments or not col_segments:
        return BorderSpec(border_color, row_segments, col_segments, 0, len(grid[0]), True)

    width_counts = Counter(end - start for start, end in col_segments)
    block_width = max(width_counts.items(), key=lambda kv: kv[1])[0]
    output_width = block_width + 2
    return BorderSpec(border_color, row_segments, col_segments, block_width, output_width, False)


def partitionIntoBlocks(grid: Grid, border_spec: BorderSpec) -> List[BlockRow]:
    if border_spec.identity:
        return []
    rows = border_spec.row_segments
    cols = border_spec.col_segments
    block_rows: List[BlockRow] = []
    for row_start, row_end in rows:
        blocks: BlockRow = []
        for col_start, col_end in cols:
            block: Block = tuple(
                tuple(grid[r][c] for c in range(col_start, col_end))
                for r in range(row_start, row_end)
            )
            blocks.append(block)
        block_rows.append(blocks)
    return block_rows


def selectUniqueBlockPerRow(block_rows: List[BlockRow]) -> List[Block]:
    return [row[_choose_unique_block(row)] for row in block_rows]


def renderUniqueBlocks(grid: Grid, border_spec: BorderSpec, unique_blocks: List[Block]) -> Grid:
    if border_spec.identity:
        return [row[:] for row in grid]

    border_color = border_spec.border_color
    block_width = border_spec.block_width
    output_width = border_spec.output_width
    result: Grid = [[border_color] * output_width for _ in grid]

    for (row_start, row_end), chosen_block in zip(border_spec.row_segments, unique_blocks):
        for offset, source_row in enumerate(chosen_block):
            target_row = row_start + offset
            row_values = list(source_row)
            if len(row_values) < block_width:
                row_values.extend([border_color] * (block_width - len(row_values)))
            elif len(row_values) > block_width:
                row_values = row_values[:block_width]
            result[target_row][1 : 1 + block_width] = row_values

    return result


def solve_38007db0(grid: Grid) -> Grid:
    border_spec = detectBorders(grid)
    block_rows = partitionIntoBlocks(grid, border_spec)
    unique_blocks = selectUniqueBlockPerRow(block_rows)
    return renderUniqueBlocks(grid, border_spec, unique_blocks)


p = solve_38007db0
