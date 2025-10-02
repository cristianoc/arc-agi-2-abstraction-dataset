"""Solver for ARC task edb79dae."""

from collections import Counter
from typing import Dict, List, Tuple

Grid = List[List[int]]


def _bounding_box(grid: Grid, color: int) -> Tuple[int, int, int, int]:
    coords = [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == color]
    if not coords:
        raise ValueError("Reference color for bounding box not found")
    rows = [r for r, _ in coords]
    cols = [c for _, c in coords]
    return min(rows), max(rows), min(cols), max(cols)


def _detect_block_size(grid: Grid, roi: Tuple[int, int, int, int], ignored: Tuple[int, ...]) -> int:
    min_r, max_r, min_c, max_c = roi
    counts = Counter()
    for r in range(min_r + 1, max_r):
        row = grid[r][min_c + 1 : max_c]
        current = None
        length = 0
        for value in row:
            if value == current:
                length += 1
            else:
                if current is not None and current not in ignored and length > 0:
                    counts[length] += 1
                current = value
                length = 1
        if current is not None and current not in ignored and length > 0:
            counts[length] += 1
    if not counts:
        raise ValueError("Unable to infer block size")
    return counts.most_common(1)[0][0]


def _collect_digit_info(grid: Grid, roi: Tuple[int, int, int, int], block: int) -> Tuple[int, Dict[int, Dict[str, Grid]]]:
    min_r, max_r, min_c, max_c = roi
    rows_total = len(grid)
    cols_total = len(grid[0])

    header_rows = grid[:min_r]
    top_background = Counter(val for row in header_rows for val in row).most_common(1)[0][0]

    digit_colors = {
        grid[r][c]
        for r in range(min_r + 1, max_r)
        for c in range(min_c + 1, max_c)
        if grid[r][c] not in (5, top_background)
    }

    block_limit = min(rows_total, min_r + block)
    blocks = []
    for r in range(0, block_limit - block + 1):
        for c in range(0, cols_total - block + 1):
            patch = [grid[r + dr][c : c + block] for dr in range(block)]
            colors = {val for row in patch for val in row}
            blocks.append((patch, colors))

    info: Dict[int, Dict[str, Grid]] = {}
    for color in digit_colors:
        # Locate a block describing the shape (mask) for this color.
        mask_block = None
        best = -1
        for patch, colors in blocks:
            if colors == {color, top_background}:
                count = sum(cell == color for row in patch for cell in row)
                if count > best:
                    best = count
                    mask_block = patch
        if mask_block is None:
            for patch, colors in blocks:
                if color in colors and top_background in colors and len(colors) <= 3:
                    count = sum(cell == color for row in patch for cell in row)
                    if count > best:
                        best = count
                        mask_block = patch

        # Aggregate potential target colors for the primary colour of the digit.
        non_digit_counts: Counter[int] = Counter()
        digit_counts: Counter[int] = Counter()
        for patch, colors in blocks:
            if color in colors:
                for row in patch:
                    for value in row:
                        if value in (color, top_background, 5):
                            continue
                        if value in digit_colors:
                            digit_counts[value] += 1
                        else:
                            non_digit_counts[value] += 1

        if non_digit_counts:
            primary = non_digit_counts.most_common(1)[0][0]
        elif digit_counts:
            primary = digit_counts.most_common(1)[0][0]
        else:
            primary = color

        info[color] = {
            "mask": mask_block,
            "primary": primary,
            "secondary": top_background,
        }

    return top_background, info


def _render_roi(grid: Grid, roi: Tuple[int, int, int, int], block: int, info: Dict[int, Dict[str, Grid]]) -> Grid:
    min_r, max_r, min_c, max_c = roi
    result = [row[:] for row in grid]

    masks = {
        digit: [[cell == digit for cell in row] for row in data["mask"]]
        for digit, data in info.items()
        if data["mask"] is not None
    }

    r = min_r + 1
    while r < max_r:
        inner = grid[r][min_c + 1 : max_c]
        if len(set(inner)) == 1:
            r += 1
            continue

        group_height = 1
        while r + group_height < max_r and grid[r + group_height][min_c + 1 : max_c] == inner:
            group_height += 1

        c = min_c + 1
        while c < max_c:
            digit = grid[r][c]
            if digit in masks:
                candidate = True
                for dc in range(block):
                    if c + dc >= max_c:
                        candidate = False
                        break
                    for dr in range(group_height):
                        if grid[r + dr][c + dc] != digit:
                            candidate = False
                            break
                    if not candidate:
                        break
                if candidate:
                    mask = masks[digit]
                    primary = info[digit]["primary"]
                    secondary = info[digit]["secondary"]
                    for dr in range(group_height):
                        for dc in range(block):
                            rr = r + dr
                            cc = c + dc
                            if cc >= max_c:
                                continue
                            result[rr][cc] = primary if mask[dr % block][dc] else secondary
                    c += block
                    continue
            c += 1
        r += group_height

    return [row[min_c : max_c + 1] for row in result[min_r : max_r + 1]]


def solve_edb79dae(grid: Grid) -> Grid:
    roi = _bounding_box(grid, 5)
    top_rows = grid[: roi[0]]
    top_bg = Counter(val for row in top_rows for val in row).most_common(1)[0][0]
    block_size = _detect_block_size(grid, roi, (top_bg, 5))
    _, digit_info = _collect_digit_info(grid, roi, block_size)
    return _render_roi(grid, roi, block_size, digit_info)


p = solve_edb79dae
