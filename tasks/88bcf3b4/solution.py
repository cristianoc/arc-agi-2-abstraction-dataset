"""Solver for ARC-AGI-2 task 88bcf3b4 (evaluation split)."""

from typing import List, Dict, Iterable, Tuple, Optional, Set
from collections import Counter


Grid = List[List[int]]


def _is_column(cells: Iterable[Tuple[int, int]]) -> bool:
    cells = list(cells)
    if len(cells) < 2:
        return False
    xs = {x for _, x in cells}
    return len(xs) == 1


def _sign(value: int) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def classifyColumns(grid: Grid) -> Tuple[Optional[int], Optional[int]]:
    h, w = len(grid), len(grid[0])
    counts = Counter(val for row in grid for val in row)
    background = counts.most_common(1)[0][0]

    positions: Dict[int, List[Tuple[int, int]]] = {}
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            positions.setdefault(val, []).append((y, x))

    anchor: Optional[int] = None
    accent: Optional[int] = None
    for color, cells in positions.items():
        if color == background or not _is_column(cells):
            continue
        for y, x in cells:
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w:
                    neighbour = grid[ny][nx]
                    if neighbour != color and neighbour != background:
                        if not _is_column(positions.get(neighbour, [])):
                            anchor = color
                            accent = neighbour
                            break
            if anchor is not None:
                break
        if anchor is not None:
            break

    return anchor, accent


def locateContactAndStart(
    grid: Grid, anchor_color: Optional[int], accent_color: Optional[int]
) -> Tuple[Tuple[int, int], Tuple[int, int], int, Optional[Set[Tuple[int, int]]], int]:
    h, w = len(grid), len(grid[0])
    counts = Counter(val for row in grid for val in row)
    background = counts.most_common(1)[0][0]

    if anchor_color is None or accent_color is None:
        return (0, 0), (0, 0), 0, None, 0

    positions: Dict[int, List[Tuple[int, int]]] = {}
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            positions.setdefault(val, []).append((y, x))

    anchor_cells: Set[Tuple[int, int]] = set(positions.get(anchor_color, []))
    accent_cells: Set[Tuple[int, int]] = set(positions.get(accent_color, []))

    contact: Optional[Tuple[int, int]] = min(
        (
            cell
            for cell in accent_cells
            if any((cell[0] + dy, cell[1] + dx) in anchor_cells for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        ),
        default=None,
    )

    if contact is None:
        return (0, 0), (0, 0), 0, None, 0

    other_colors = [c for c in positions if c not in (background, anchor_color, accent_color)]
    if not other_colors:
        return (0, 0), (0, 0), 0, None, 0

    contact_y, contact_x = contact
    start_cell = min(
        (pos for color in other_colors for pos in positions[color]),
        key=lambda p: (abs(p[0] - contact_y) + abs(p[1] - contact_x), p),
    )
    start_color = grid[start_cell[0]][start_cell[1]]
    anchor_x = next(iter(anchor_cells))[1] if anchor_cells else 0
    return contact, start_cell, start_color, accent_cells, anchor_x


def generatePath(
    grid: Grid,
    contact: Tuple[int, int],
    start: Tuple[int, int],
    accent_cells: Optional[Set[Tuple[int, int]]],
    anchor_x: int,
    start_color: int,
) -> List[Tuple[int, int]]:
    h, w = len(grid), len(grid[0])
    accent_count = len(accent_cells) if accent_cells else 0

    # Build an overall height for the start colour across the grid (matches original heuristic).
    start_component = {
        (y, x)
        for y, row in enumerate(grid)
        for x, val in enumerate(row)
        if val == start_color
    }
    if start_component:
        ys = [y for y, _ in start_component]
        start_height = max(ys) - min(ys) + 1
    else:
        start_height = 0

    cy, cx = contact
    sy, sx = start
    dir_y = _sign(sy - cy)
    diff = sx - cx

    if diff == 0:
        if anchor_x > cx:
            dir_x = -1
        elif anchor_x < cx:
            dir_x = 1
        else:
            dir_x = 1 if cx < w - 1 else -1
    else:
        dir_x = _sign(diff)

    max_vertical = cy if dir_y == -1 else (h - 1 - cy if dir_y == 1 else 0)

    # Single-cell target handled separately to mimic training behaviour.
    if start_height == 1 and dir_y != 0:
        path = [contact]
        y, x = cy, cx
        while y != sy and len(path) < accent_count:
            y += dir_y
            path.append((y, x))
        if len(path) < accent_count:
            ny, nx = y + dir_y, x + dir_x
            if 0 <= ny < h and 0 <= nx < w:
                path.append((ny, nx))
        return path

    if dir_y == 0:
        # Horizontal sweep when start shares the contact row.
        path = [contact]
        y, x = cy, cx
        step_dir = dir_x if dir_x != 0 else (_sign(anchor_x - cx) or 1)
        while len(path) < accent_count:
            nx = x + step_dir
            if not (0 <= nx < w):
                break
            x = nx
            path.append((y, x))
        return path

    if diff == 0:
        approach_len = max(start_height - 1, 0)
        plateau_len = 0
        plateau_offset = dir_x * (start_height - 1)
    else:
        if dir_x * dir_y >= 0:
            approach_len = abs(diff + dir_x)
            plateau_offset = diff + dir_x
        else:
            approach_len = max(abs(diff) - 1, 0)
            plateau_offset = diff - dir_x
        plateau_len = max(start_height - 1, 0)

    plateau_x = cx + plateau_offset
    max_steps = min(
        max_vertical,
        2 * approach_len + plateau_len,
        max(accent_count - 1, 0),
    )

    y, x = cy, cx
    path = [(y, x)]
    steps_used = 0

    actual_approach = min(approach_len, max_steps)
    for _ in range(actual_approach):
        if steps_used >= max_steps:
            break
        y += dir_y
        x += dir_x
        path.append((y, x))
        steps_used += 1

    remaining = max_steps - steps_used
    actual_plateau = min(plateau_len, remaining)
    for _ in range(actual_plateau):
        if steps_used >= max_steps:
            break
        y += dir_y
        if x != plateau_x:
            x += _sign(plateau_x - x)
        path.append((y, x))
        steps_used += 1

    remaining = max_steps - steps_used
    dep_dir_x = -dir_x
    for _ in range(remaining):
        y += dir_y
        if dir_x != 0:
            x += dep_dir_x
        path.append((y, x))

    return path


def rewritePath(
    grid: Grid, accent_cells: Optional[Set[Tuple[int, int]]], path_cells: List[Tuple[int, int]]
) -> Grid:
    # Guard: if any prior step failed to find necessary structure, keep grid unchanged.
    if not accent_cells or not path_cells:
        return [row[:] for row in grid]

    counts = Counter(val for row in grid for val in row)
    background = counts.most_common(1)[0][0]

    # Determine accent colour from any accent cell.
    any_y, any_x = next(iter(accent_cells))
    accent_color = grid[any_y][any_x]

    output = [row[:] for row in grid]
    for y, x in accent_cells:
        output[y][x] = background
    for y, x in path_cells:
        output[y][x] = accent_color
    return output


def solve_88bcf3b4(grid: Grid) -> Grid:
    anchor_color, accent_color = classifyColumns(grid)
    contact, start, start_color, accent_cells, anchor_x = locateContactAndStart(grid, anchor_color, accent_color)
    path_cells = generatePath(grid, contact, start, accent_cells, anchor_x, start_color)
    return rewritePath(grid, accent_cells, path_cells)


p = solve_88bcf3b4
