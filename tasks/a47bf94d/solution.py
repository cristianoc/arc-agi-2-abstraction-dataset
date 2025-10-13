from collections import defaultdict, deque


def _detect_squares(grid):
    """Return mapping color->list of 3x3 square centers (row, col)."""
    h, w = len(grid), len(grid[0])
    visited = [[False] * w for _ in range(h)]
    squares = defaultdict(list)

    for r in range(h):
        for c in range(w):
            color = grid[r][c]
            if color == 0 or visited[r][c]:
                continue

            queue = deque([(r, c)])
            visited[r][c] = True
            cells = []

            while queue:
                rr, cc = queue.popleft()
                cells.append((rr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not visited[nr][nc] and grid[nr][nc] == color:
                        visited[nr][nc] = True
                        queue.append((nr, nc))

            if len(cells) != 9:
                continue

            rows = [rr for rr, _ in cells]
            cols = [cc for _, cc in cells]
            if max(rows) - min(rows) != 2 or max(cols) - min(cols) != 2:
                continue

            r0, c0 = min(rows), min(cols)
            filled = True
            for rr in range(r0, r0 + 3):
                for cc in range(c0, c0 + 3):
                    if grid[rr][cc] != color:
                        filled = False
                        break
                if not filled:
                    break

            if filled:
                squares[color].append((r0 + 1, c0 + 1))

    return squares


def _detect_patterns(grid):
    """Detect existing plus-hollow (cardinal arms) and x-center (diagonal arms) patterns."""
    h, w = len(grid), len(grid[0])
    plus = {}
    diag = {}

    for r in range(1, h - 1):
        for c in range(1, w - 1):
            center = grid[r][c]
            north, south = grid[r - 1][c], grid[r + 1][c]
            west, east = grid[r][c - 1], grid[r][c + 1]
            nw, ne = grid[r - 1][c - 1], grid[r - 1][c + 1]
            sw, se = grid[r + 1][c - 1], grid[r + 1][c + 1]

            if center == 0 and north == south == west == east != 0 and nw == ne == sw == se == 0:
                plus.setdefault(north, (r, c))

            if (
                center != 0
                and nw == ne == sw == se == center
                and north == south == west == east == 0
            ):
                diag.setdefault(center, (r, c))

    return plus, diag


def _orientation(squares, plus):
    if squares:
        rows = {pos[0] for centers in squares.values() for pos in centers}
        cols = {pos[1] for centers in squares.values() for pos in centers}
        if len(rows) == 1:
            return "row", next(iter(rows))
        if len(cols) == 1:
            return "col", next(iter(cols))

    if plus:
        rows = {pos[0] for pos in plus.values()}
        cols = {pos[1] for pos in plus.values()}
        if len(rows) == 1:
            return "row", next(iter(rows))
        if len(cols) == 1:
            return "col", next(iter(cols))

    return "row", 1


def _gather_refs(colors, squares, plus, diag, orient):
    refs = {}
    for color in colors:
        if color in squares:
            pos = squares[color][0]
        elif color in plus:
            pos = plus[color]
        elif color in diag:
            pos = diag[color]
        else:
            pos = (1, 1)
        refs[color] = pos[1] if orient == "row" else pos[0]
    return refs


def _derive_axis_positions(refs, count, bounds):
    low, high = bounds
    positions = sorted(set(refs))
    if not positions:
        positions = [(low + high) // 2]

    def clamp(val):
        return max(low, min(high, val))

    while len(positions) < count:
        best_gap = -1
        best_pos = None
        extended = [low] + positions + [high]
        for i in range(len(extended) - 1):
            a, b = extended[i], extended[i + 1]
            gap = b - a
            if gap <= 1:
                continue
            mid = (a + b) // 2
            if mid in positions:
                mid = a + 1
            if gap > best_gap:
                best_gap = gap
                best_pos = clamp(mid)
        if best_pos is None:
            best_pos = clamp(positions[-1] + 1)
        positions.append(best_pos)
        positions = sorted(set(positions))

    positions = [clamp(p) for p in positions]
    positions = sorted(positions)
    if len(positions) > count:
        positions = positions[:count]
    return positions


def _apply_plus(grid, r, c, color):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            grid[r + dr][c + dc] = 0
    grid[r - 1][c] = grid[r + 1][c] = color
    grid[r][c - 1] = grid[r][c + 1] = color


def _apply_x(grid, r, c, color):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            grid[r + dr][c + dc] = 0
    grid[r][c] = color
    grid[r - 1][c - 1] = grid[r - 1][c + 1] = color
    grid[r + 1][c - 1] = grid[r + 1][c + 1] = color


def _last_nonzero_row(grid):
    for r in range(len(grid) - 1, -1, -1):
        if any(cell != 0 for cell in grid[r]):
            return r
    return -1


def solve_a47bf94d(grid):
    h, w = len(grid), len(grid[0])
    squares = _detect_squares(grid)
    plus_in, diag_in = _detect_patterns(grid)
    colors = set(squares) | set(plus_in) | set(diag_in)

    orient, axis_val = _orientation(squares, plus_in)
    refs = _gather_refs(colors, squares, plus_in, diag_in, orient)
    axis_bounds = (1, (w if orient == "row" else h) - 2)
    axis_positions = _derive_axis_positions(list(refs.values()), len(colors), axis_bounds)

    colors_sorted = sorted(colors, key=lambda c: (refs[c], c))
    plus_targets = {}
    for slot, color in enumerate(colors_sorted):
        coord = axis_positions[slot]
        if orient == "row":
            plus_targets[color] = (axis_val, coord)
        else:
            plus_targets[color] = (coord, axis_val)

    preferred_row = [4, 2, 1, 3, 6, 5, 7, 8, 9]
    preferred_col = [2, 4, 1, 3, 6, 5, 7, 8, 9]
    preferred = preferred_row if orient == "row" else preferred_col

    available_slots = set(range(len(axis_positions)))
    x_targets = {}
    if diag_in:
        for color, pos in diag_in.items():
            coord = pos[1] if orient == "row" else pos[0]
            idx = min(range(len(axis_positions)), key=lambda i: abs(axis_positions[i] - coord))
            available_slots.discard(idx)
            x_targets[color] = pos

    ordered = [c for c in preferred if c in colors and c not in x_targets]
    ordered.extend(sorted(color for color in colors if color not in preferred and color not in x_targets))

    remaining_slots = sorted(available_slots)
    remaining_coords = [axis_positions[idx] for idx in remaining_slots]

    if orient == "row":
        if diag_in:
            default_row = sorted({pos[0] for pos in diag_in.values()})[0]
        else:
            candidate = max(axis_val + 2, _last_nonzero_row(grid) + 2)
            default_row = min(candidate, h - 2)
        for color, col in zip(ordered, remaining_coords):
            x_targets[color] = (default_row, col)
    else:
        if diag_in:
            default_col = sorted({pos[1] for pos in diag_in.values()})[0]
        else:
            default_col = min(axis_val + 2, w - 2)
        for color, row in zip(ordered, remaining_coords):
            x_targets[color] = (row, default_col)

    out = [row[:] for row in grid]
    for color, (r, c) in plus_targets.items():
        _apply_plus(out, r, c, color)
    for color, (r, c) in x_targets.items():
        _apply_x(out, r, c, color)

    return out


p = solve_a47bf94d
