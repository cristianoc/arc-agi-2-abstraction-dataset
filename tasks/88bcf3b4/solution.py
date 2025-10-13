"""Solver for ARC-AGI-2 task 88bcf3b4 (evaluation split)."""

from collections import Counter


def _is_column(cells):
    if len(cells) < 2:
        return False
    xs = {x for _, x in cells}
    return len(xs) == 1


def _sign(value):
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


class _PathGenerator:
    def __init__(self, grid, contact, start, anchor_x, accent_cells, start_color):
        self.grid = grid
        self.contact = contact
        self.start = start
        self.anchor_x = anchor_x
        self.accent_cells = accent_cells
        self.start_color = start_color
        self.h = len(grid)
        self.w = len(grid[0])
        self.start_component = {
            (y, x)
            for y, row in enumerate(grid)
            for x, val in enumerate(row)
            if val == start_color
        }
        ys = [y for y, _ in self.start_component]
        self.start_height = max(ys) - min(ys) + 1

    def generate(self):
        cy, cx = self.contact
        sy, sx = self.start
        dir_y = _sign(sy - cy)
        diff = sx - cx

        if diff == 0:
            if self.anchor_x > cx:
                dir_x = -1
            elif self.anchor_x < cx:
                dir_x = 1
            else:
                dir_x = 1 if cx < self.w - 1 else -1
        else:
            dir_x = _sign(diff)

        accent_count = len(self.accent_cells)
        max_vertical = cy if dir_y == -1 else (self.h - 1 - cy if dir_y == 1 else 0)

        # Single-cell target handled separately to mimic training behaviour.
        if self.start_height == 1 and dir_y != 0:
            path = [self.contact]
            y, x = cy, cx
            while y != sy and len(path) < accent_count:
                y += dir_y
                path.append((y, x))
            if len(path) < accent_count:
                ny, nx = y + dir_y, x + dir_x
                if 0 <= ny < self.h and 0 <= nx < self.w:
                    path.append((ny, nx))
            return path

        if dir_y == 0:
            # Horizontal sweep when start shares the contact row.
            path = [self.contact]
            y, x = cy, cx
            step_dir = dir_x if dir_x != 0 else (_sign(self.anchor_x - cx) or 1)
            while len(path) < accent_count:
                nx = x + step_dir
                if not (0 <= nx < self.w):
                    break
                x = nx
                path.append((y, x))
            return path

        if diff == 0:
            approach_len = max(self.start_height - 1, 0)
            plateau_len = 0
            plateau_offset = dir_x * (self.start_height - 1)
        else:
            if dir_x * dir_y >= 0:
                approach_len = abs(diff + dir_x)
                plateau_offset = diff + dir_x
            else:
                approach_len = max(abs(diff) - 1, 0)
                plateau_offset = diff - dir_x
            plateau_len = max(self.start_height - 1, 0)

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


def solve_88bcf3b4(grid):
    h, w = len(grid), len(grid[0])
    counts = Counter(val for row in grid for val in row)
    background = counts.most_common(1)[0][0]

    positions = {}
    for y, row in enumerate(grid):
        for x, val in enumerate(row):
            positions.setdefault(val, []).append((y, x))

    anchor = accent = None
    for color, cells in positions.items():
        if color == background or not _is_column(cells):
            continue
        cell_set = set(cells)
        for y, x in cells:
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w:
                    neighbour = grid[ny][nx]
                    if neighbour != color and neighbour != background:
                        if not _is_column(positions[neighbour]):
                            anchor = color
                            accent = neighbour
                            break
            if anchor is not None:
                break
        if anchor is not None:
            break

    if anchor is None or accent is None:
        return [row[:] for row in grid]

    anchor_cells = set(positions[anchor])
    accent_cells = set(positions[accent])
    contact = min(
        (cell for cell in accent_cells if any((cell[0] + dy, cell[1] + dx) in anchor_cells
                                               for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))),
        default=None,
    )

    if contact is None:
        return [row[:] for row in grid]

    other_colors = [c for c in positions if c not in (background, anchor, accent)]
    if not other_colors:
        return [row[:] for row in grid]

    start_cell = min(
        (pos for color in other_colors for pos in positions[color]),
        key=lambda p: (abs(p[0] - contact[0]) + abs(p[1] - contact[1]), p),
    )
    start_color = grid[start_cell[0]][start_cell[1]]
    anchor_x = next(iter(anchor_cells))[1]

    path = _PathGenerator(grid, contact, start_cell, anchor_x, accent_cells, start_color).generate()

    output = [row[:] for row in grid]
    for y, x in accent_cells:
        output[y][x] = background
    for y, x in path:
        output[y][x] = accent
    return output


p = solve_88bcf3b4
