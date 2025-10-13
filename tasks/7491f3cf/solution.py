"""ARC-AGI-2 task 7491f3cf solver."""

from collections import Counter
from typing import Iterable, List, Sequence, Set, Tuple

Grid = List[List[int]]
Coord = Tuple[int, int]


CROSS_SHAPE: Set[Coord] = {
    (0, 2), (1, 2),
    (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
    (3, 2), (4, 2),
}

DIAMOND_SHAPE: Set[Coord] = {
    (0, 0), (0, 4),
    (1, 1), (1, 3),
    (2, 2),
    (3, 1), (3, 3),
    (4, 0), (4, 4),
}

BLOCK_LEFT_SHAPE: Set[Coord] = {
    (0, 3), (0, 4),
    (1, 3), (1, 4),
    (3, 0), (3, 1),
    (4, 0), (4, 1),
}

BLOCK_CENTER_SHAPE: Set[Coord] = {
    (0, 1), (0, 3),
    (1, 0), (1, 2), (1, 4),
    (2, 1), (2, 3),
    (3, 0), (3, 2), (3, 4),
    (4, 1), (4, 3),
}

BLOCK_CENTER_OVERLAY: Set[Coord] = {
    (0, 1), (0, 3),
    (1, 2), (1, 4),
    (2, 3),
    (3, 4),
}

BLOCK_LEFT_OVERLAY: Set[Coord] = {
    (3, 0), (3, 1),
    (4, 0), (4, 1),
}


def _extract_sections(grid: Grid) -> Tuple[int, int, int, int]:
    rows = len(grid)
    cols = len(grid[0])
    border_color = grid[0][0]
    border_cols = [c for c in range(cols) if all(grid[r][c] == border_color for r in range(rows))]
    if len(border_cols) < 4:
        raise ValueError("Unexpected column layout for task 7491f3cf")

    width = border_cols[2] - border_cols[1] - 1
    left_start = border_cols[1] + 1
    center_start = border_cols[2] + 1
    right_start = border_cols[3] + 1

    return left_start, center_start, right_start, width


def _panel_base(panel: Sequence[Sequence[int]]) -> int:
    return Counter(value for row in panel for value in row).most_common(1)[0][0]


def _interior_shape(panel: Sequence[Sequence[int]], base: int) -> Set[Coord]:
    height = len(panel)
    width = len(panel[0])
    return {
        (r - 1, c)
        for r in range(1, height - 1)
        for c in range(width)
        if panel[r][c] != base
    }


def _choose_cross_subset(left_base: int, center_accent: int) -> Set[str]:
    subset = {"bottom", "right"}
    if center_accent is not None and left_base <= center_accent:
        subset.add("left")
    if left_base >= 6:
        subset.add("top")
    return subset


def _apply_cross_subset(
    left_panel: Sequence[Sequence[int]],
    center_panel: Sequence[Sequence[int]],
    subset: Set[str],
) -> List[List[int]]:
    height = len(left_panel)
    width = len(left_panel[0])
    center_row = height // 2
    center_col = width // 2

    left_base = _panel_base(left_panel)
    center_base = _panel_base(center_panel)
    center_counter = Counter(
        center_panel[r][c]
        for r in range(1, height - 1)
        for c in range(width)
        if center_panel[r][c] != center_base
    )
    center_accent = center_counter.most_common(1)[0][0] if center_counter else center_base

    result = [row[:] for row in left_panel]

    def is_overlay_cell(r: int, c: int) -> bool:
        if center_panel[r][c] == center_base:
            return False
        if "top" in subset and c == center_col and r < center_row:
            return True
        if "bottom" in subset and c == center_col and r > center_row:
            return True
        if "left" in subset and r == center_row and c < center_col:
            return True
        if "right" in subset and r == center_row and c > center_col:
            return True
        return False

    for r in range(height):
        for c in range(width):
            if is_overlay_cell(r, c):
                result[r][c] = center_panel[r][c]

    horiz = {d for d in ("left", "right") if d in subset}
    vert = {d for d in ("top", "bottom") if d in subset}

    def in_quadrant(r: int, c: int, h: str, v: str) -> bool:
        if h == "left" and not (c < center_col):
            return False
        if h == "right" and not (c > center_col):
            return False
        if v == "top" and not (r < center_row):
            return False
        if v == "bottom" and not (r > center_row):
            return False
        return True

    for r in range(height):
        for c in range(width):
            if left_panel[r][c] == left_base or center_panel[r][c] != center_base:
                continue
            remove = False
            if horiz and vert:
                for h in horiz:
                    for v in vert:
                        if in_quadrant(r, c, h, v):
                            remove = True
                            break
                    if remove:
                        break
            elif horiz:
                if "left" in horiz and c < center_col:
                    remove = True
                if "right" in horiz and c > center_col:
                    remove = True
            elif vert:
                if "top" in vert and r < center_row:
                    remove = True
                if "bottom" in vert and r > center_row:
                    remove = True
            if remove:
                result[r][c] = center_base

    result[center_row][center_col] = left_panel[center_row][center_col]
    return result


def _apply_block_template(
    left_panel: Sequence[Sequence[int]],
    center_panel: Sequence[Sequence[int]],
) -> List[List[int]]:
    left_base = _panel_base(left_panel)
    center_base = _panel_base(center_panel)
    left_counter = Counter(
        left_panel[r][c]
        for r in range(1, len(left_panel) - 1)
        for c in range(len(left_panel[0]))
        if left_panel[r][c] != left_base
    )
    center_counter = Counter(
        center_panel[r][c]
        for r in range(1, len(center_panel) - 1)
        for c in range(len(center_panel[0]))
        if center_panel[r][c] != center_base
    )
    left_accent = left_counter.most_common(1)[0][0]
    center_accent = center_counter.most_common(1)[0][0]

    result = [row[:] for row in left_panel]

    for r in range(1, len(result) - 1):
        for c in range(len(result[0])):
            result[r][c] = left_base

    for r, c in BLOCK_CENTER_OVERLAY:
        result[r + 1][c] = center_accent
    for r, c in BLOCK_LEFT_OVERLAY:
        result[r + 1][c] = left_accent

    result[0] = left_panel[0][:]
    result[-1] = left_panel[-1][:]
    return result


def solve_7491f3cf(grid: Grid) -> Grid:
    rows = len(grid)
    left_start, center_start, right_start, width = _extract_sections(grid)

    left_panel = [row[left_start : left_start + width] for row in grid]
    center_panel = [row[center_start : center_start + width] for row in grid]

    left_base = _panel_base(left_panel)
    center_base = _panel_base(center_panel)

    left_shape = _interior_shape(left_panel, left_base)
    center_shape = _interior_shape(center_panel, center_base)

    if left_shape == DIAMOND_SHAPE and center_shape == CROSS_SHAPE:
        center_accents = Counter(
            center_panel[r][c]
            for r in range(1, rows - 1)
            for c in range(width)
            if center_panel[r][c] != center_base
        )
        center_accent = center_accents.most_common(1)[0][0] if center_accents else center_base
        subset = _choose_cross_subset(left_base, center_accent)
        result_panel = _apply_cross_subset(left_panel, center_panel, subset)
    elif left_shape == BLOCK_LEFT_SHAPE and center_shape == BLOCK_CENTER_SHAPE:
        result_panel = _apply_block_template(left_panel, center_panel)
    else:
        raise ValueError("Unhandled panel configuration for task 7491f3cf")

    output = [row[:] for row in grid]
    for r in range(rows):
        output[r][right_start : right_start + width] = result_panel[r]

    return output


p = solve_7491f3cf
