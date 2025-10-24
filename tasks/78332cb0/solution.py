"""Solver for ARC-AGI-2 task 78332cb0."""

from typing import List, Tuple

# Typed alias used by the DSL lambda
Grid = List[List[int]]


# DSL lambda-equivalent main entrypoint
def solve_78332cb0(grid: Grid) -> Grid:
    separator = detectSeparatorColor(grid)
    blocks = segmentIntoBlocks(grid, separator)
    ordered_blocks, orientation = rotateAndCycleBlocks(blocks)
    return assembleBlocks(list(ordered_blocks), orientation, separator)


# Thin wrappers to align helper names with the DSL lambda, delegating to existing logic
def detectSeparatorColor(grid: Grid) -> int:
    return _find_separator_color(grid)


def segmentIntoBlocks(grid: Grid, separator: int) -> List[List[Grid]]:
    return _extract_blocks(grid, separator)


def rotateAndCycleBlocks(blocks: List[List[Grid]]) -> Tuple[List[Grid], str]:
    return _reorder_blocks(blocks)


def assembleBlocks(blocks: List[Grid], orientation: str, separator: int) -> Grid:
    return _assemble_output(blocks, orientation, separator)


def _find_separator_color(grid: Grid) -> int:
    colors = {cell for row in grid for cell in row}
    height, width = len(grid), len(grid[0])

    def has_full_line(color: int) -> bool:
        row_full = any(all(cell == color for cell in row) for row in grid)
        col_full = any(all(grid[r][c] == color for r in range(height)) for c in range(width))
        return row_full or col_full

    if 6 in colors and has_full_line(6):
        return 6

    for color in colors:
        if has_full_line(color):
            return color

    return 6


def _extract_blocks(grid: Grid, separator: int) -> List[List[Grid]]:
    row_segments = _segments_along_axis(grid, separator, axis=0)
    col_segments = _segments_along_axis(grid, separator, axis=1)

    blocks = []
    for r0, r1 in row_segments:
        row_blocks = []
        for c0, c1 in col_segments:
            block = [row[c0:c1] for row in grid[r0:r1]]
            row_blocks.append(block)
        blocks.append(row_blocks)
    return blocks


from typing import Optional


def _segments_along_axis(grid: Grid, separator: int, axis: int) -> List[Tuple[int, int]]:
    if axis == 0:
        length = len(grid)
        def is_separator(idx: int) -> bool:
            return all(cell == separator for cell in grid[idx])
    else:
        length = len(grid[0])
        def is_separator(idx: int) -> bool:
            return all(row[idx] == separator for row in grid)

    segments: List[Tuple[int, int]] = []
    start: Optional[int] = None
    for idx in range(length):
        if is_separator(idx):
            if start is not None:
                segments.append((start, idx))
                start = None
        else:
            if start is None:
                start = idx
    if start is not None:
        segments.append((start, length))

    if not segments:
        segments.append((0, length))
    return segments


def _reorder_blocks(blocks: List[List[Grid]]) -> Tuple[List[Grid], str]:
    block_rows = len(blocks)
    block_cols = len(blocks[0]) if blocks else 0

    rotated = _rotate_blocks_clockwise(blocks)
    flat_blocks = [block for row in rotated for block in row]

    if block_rows > 1 and block_cols > 1:
        start_index = block_rows - 1
        flat_blocks = flat_blocks[start_index:] + flat_blocks[:start_index]
        orientation = "vertical"
    else:
        orientation = "horizontal" if len(rotated) == 1 else "vertical"

    return flat_blocks, orientation


def _rotate_blocks_clockwise(blocks: List[List[Grid]]) -> List[List[Grid]]:
    if not blocks:
        return []
    block_rows = len(blocks)
    block_cols = len(blocks[0])
    rotated: List[List[Grid]] = [[blocks[0][0] for _ in range(block_rows)] for _ in range(block_cols)]
    for r, row in enumerate(blocks):
        for c, block in enumerate(row):
            nr = c
            nc = block_rows - 1 - r
            rotated[nr][nc] = block
    return rotated


def _assemble_output(blocks: List[Grid], orientation: str, separator: int) -> Grid:
    if not blocks:
        return []

    block_height = len(blocks[0])
    block_width = len(blocks[0][0]) if block_height else 0

    if orientation == "horizontal":
        total_width = len(blocks) * block_width + (len(blocks) - 1)
        result = [[separator] * total_width for _ in range(block_height)]
        cursor = 0
        for index, block in enumerate(blocks):
            for r in range(block_height):
                for c in range(block_width):
                    result[r][cursor + c] = block[r][c]
            cursor += block_width
            if index != len(blocks) - 1:
                for r in range(block_height):
                    result[r][cursor] = separator
                cursor += 1
        return result

    total_height = len(blocks) * block_height + (len(blocks) - 1)
    vresult: Grid = []
    for index, block in enumerate(blocks):
        vresult.extend(row[:] for row in block)
        if index != len(blocks) - 1:
            vresult.append([separator] * block_width)
    return vresult


p = solve_78332cb0
