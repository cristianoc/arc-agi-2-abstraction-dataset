"""Solver for ARC-AGI-2 task 78332cb0."""

# Segment the grid into separator-delimited tiles and rotate their order.

def solve_78332cb0(grid):
    """Reorder the 5x5 digit tiles separated by the color 6."""
    separator = _find_separator_color(grid)
    blocks = _extract_blocks(grid, separator)
    ordered_blocks, orientation = _reorder_blocks(blocks)
    return _assemble_output(ordered_blocks, orientation, separator)


def _find_separator_color(grid):
    colors = {cell for row in grid for cell in row}
    height, width = len(grid), len(grid[0])

    def has_full_line(color):
        row_full = any(all(cell == color for cell in row) for row in grid)
        col_full = any(all(grid[r][c] == color for r in range(height)) for c in range(width))
        return row_full or col_full

    if 6 in colors and has_full_line(6):
        return 6

    for color in colors:
        if has_full_line(color):
            return color

    return 6


def _extract_blocks(grid, separator):
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


def _segments_along_axis(grid, separator, axis):
    if axis == 0:
        length = len(grid)
        is_separator = lambda idx: all(cell == separator for cell in grid[idx])
    else:
        length = len(grid[0])
        is_separator = lambda idx: all(row[idx] == separator for row in grid)

    segments = []
    start = None
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


def _reorder_blocks(blocks):
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


def _rotate_blocks_clockwise(blocks):
    if not blocks:
        return []
    block_rows = len(blocks)
    block_cols = len(blocks[0])
    rotated = [[None for _ in range(block_rows)] for _ in range(block_cols)]
    for r, row in enumerate(blocks):
        for c, block in enumerate(row):
            nr = c
            nc = block_rows - 1 - r
            rotated[nr][nc] = block
    return rotated


def _assemble_output(blocks, orientation, separator):
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
    result = []
    for index, block in enumerate(blocks):
        result.extend(row[:] for row in block)
        if index != len(blocks) - 1:
            result.append([separator] * block_width)
    return result


p = solve_78332cb0
