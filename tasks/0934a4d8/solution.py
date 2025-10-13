"""Solver for ARC-AGI-2 task 0934a4d8."""

def _bounding_box(grid, target):
    """Return the bounding box (inclusive/exclusive) of cells equal to ``target``."""
    row_min = len(grid)
    row_max = -1
    col_min = len(grid[0])
    col_max = -1

    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value == target:
                if r < row_min:
                    row_min = r
                if r > row_max:
                    row_max = r
                if c < col_min:
                    col_min = c
                if c > col_max:
                    col_max = c

    if row_max == -1:
        raise ValueError("target value not found in grid")

    return row_min, row_max + 1, col_min, col_max + 1


def _extract_block(grid, r_start, c_start, height, width):
    return [row[c_start:c_start + width] for row in grid[r_start:r_start + height]]


def _flip_lr(block):
    return [list(reversed(row)) for row in block]


def _flip_ud(block):
    return [row[:] for row in block[::-1]]


def solve_0934a4d8(grid):
    r0, r1, c0, c1 = _bounding_box(grid, 8)
    height = r1 - r0
    width = c1 - c0
    total_rows = len(grid)
    total_cols = len(grid[0])
    offset = 2

    horizontal_start = total_cols - width - c0 + offset
    vertical_start = total_rows - height - r0 + offset

    horizontal_valid = 0 <= horizontal_start <= total_cols - width
    vertical_valid = 0 <= vertical_start <= total_rows - height

    block_h = None
    dist_h = -1
    if horizontal_valid:
        block_h = _extract_block(grid, r0, horizontal_start, height, width)
        dist_h = abs(c0 - horizontal_start)

    block_v = None
    dist_v = -1
    if vertical_valid:
        block_v = _extract_block(grid, vertical_start, c0, height, width)
        dist_v = abs(r0 - vertical_start)

    if dist_h > dist_v:
        return _flip_lr(block_h)
    if dist_v > dist_h:
        return _flip_ud(block_v)

    if block_h is None:
        return _flip_ud(block_v)
    if block_v is None:
        return _flip_lr(block_h)

    count8_h = sum(value == 8 for row in block_h for value in row)
    count8_v = sum(value == 8 for row in block_v for value in row)

    if count8_v < count8_h:
        return _flip_ud(block_v)
    if count8_h < count8_v:
        return _flip_lr(block_h)

    return _flip_lr(block_h)


p = solve_0934a4d8
