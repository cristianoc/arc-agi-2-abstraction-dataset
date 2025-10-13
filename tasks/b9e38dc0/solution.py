"""Solver for ARC-AGI-2 task b9e38dc0."""

from __future__ import annotations


def copy_grid(grid):
    return [row[:] for row in grid]


def count_colors(grid):
    counts = {}
    for row in grid:
        for value in row:
            counts[value] = counts.get(value, 0) + 1
    return counts


def dominant_color(grid):
    counts = count_colors(grid)
    return max(counts, key=lambda color: counts[color])


def barrier_color(grid, background):
    counts = count_colors(grid)
    candidates = {c: n for c, n in counts.items() if c != background}
    return max(candidates, key=lambda color: (candidates[color], color))


def fill_color(grid, background, barrier):
    counts = count_colors(grid)
    h = len(grid)
    w = len(grid[0])
    touching = []
    for color, total in counts.items():
        if color in (background, barrier):
            continue
        touches = False
        for r in range(h):
            if touches:
                break
            for c in range(w):
                if grid[r][c] != color:
                    continue
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr = r + dr
                    nc = c + dc
                    if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == barrier:
                        touches = True
                        break
                if touches:
                    break
        if touches:
            touching.append((total, color))
    if not touching:
        return None
    touching.sort()
    return touching[0][1]


def group_contiguous(values):
    if not values:
        return []
    values = sorted(values)
    groups = []
    start = prev = values[0]
    for value in values[1:]:
        if value == prev + 1:
            prev = value
            continue
        groups.append((start, prev))
        start = prev = value
    groups.append((start, prev))
    return groups


def seed_segments_vertical(grid, background, fill_positions):
    grouped = {}
    width = len(grid[0])
    for r, c in fill_positions:
        grouped.setdefault(r, []).append(c)
    seeds = {}
    for r, cols in grouped.items():
        segments = []
        for left, right in group_contiguous(cols):
            L = left
            while L > 0 and grid[r][L - 1] == background:
                L -= 1
            R = right
            while R + 1 < width and grid[r][R + 1] == background:
                R += 1
            segments.append((L, R))
        seeds[r] = segments
    return seeds


def clip_row_segments(grid, row, interval, background):
    width = len(grid[0])
    L = max(interval[0], 0)
    R = min(interval[1], width - 1)
    segments = []
    run = None
    for c in range(L, R + 1):
        if grid[row][c] == background:
            if run is None:
                run = [c, c]
            else:
                run[1] = c
        else:
            if run is not None:
                segments.append(tuple(run))
                run = None
    if run is not None:
        segments.append(tuple(run))
    return segments


def merge_segments(segments):
    if not segments:
        return []
    segments = sorted(segments)
    merged = [list(segments[0])]
    for left, right in segments[1:]:
        last = merged[-1]
        if left <= last[1]:
            last[1] = max(last[1], right)
        else:
            merged.append([left, right])
    return [tuple(seg) for seg in merged]


def first_non_background_up(grid, background):
    h = len(grid)
    w = len(grid[0])
    result = [[None] * w for _ in range(h)]
    last = [None] * w
    for r in range(h):
        row = grid[r]
        for c in range(w):
            result[r][c] = last[c]
            if row[c] != background:
                last[c] = row[c]
    return result


def first_non_background_down(grid, background):
    h = len(grid)
    w = len(grid[0])
    result = [[None] * w for _ in range(h)]
    last = [None] * w
    for r in range(h - 1, -1, -1):
        row = grid[r]
        for c in range(w):
            result[r][c] = last[c]
            if row[c] != background:
                last[c] = row[c]
    return result


def propagate_vertical(grid, orientation, seeds, background, barrier, fill_color, barrier_bounds):
    if not seeds:
        return {}

    helper = first_non_background_up(grid, background)
    row_range = range(min(seeds), len(grid))
    if orientation == "up":
        helper = first_non_background_down(grid, background)
        row_range = range(max(seeds), -1, -1)

    allowed = {None, barrier, fill_color}
    result = {}
    prev_segments = None

    for r in row_range:
        segments = []
        if prev_segments is not None:
            for left, right in prev_segments:
                candidates = (left - 1, right + 1)
                cand_left, cand_right = candidates
                if cand_left < 0 or helper[r][cand_left] not in allowed:
                    cand_left = left
                if cand_right >= len(grid[0]) or helper[r][cand_right] not in allowed:
                    cand_right = right
                for seg in clip_row_segments(grid, r, (cand_left, cand_right), background):
                    overlap = min(seg[1], right) - max(seg[0], left) + 1
                    if overlap > 0:
                        segments.append(seg)
        if r in seeds:
            segments.extend(seeds[r])
        segments = merge_segments(segments)

        if orientation == "up" and barrier_bounds is not None and segments:
            top_row, left_bound, right_bound = barrier_bounds
            if r < top_row:
                trimmed = []
                for left, right in segments:
                    left_limit = left_bound if r > 0 else left_bound - 1
                    right_limit = right_bound if r > 0 else right_bound + 1
                    new_left = max(left, left_limit)
                    new_right = min(right, right_limit)
                    if new_left <= new_right:
                        trimmed.append((new_left, new_right))
                segments = merge_segments(trimmed)

        if segments:
            result[r] = segments
            prev_segments = segments
        else:
            prev_segments = None
    return result


def transpose_grid(grid):
    return [list(row) for row in zip(*grid)]


def transpose_positions(positions):
    return [(c, r) for r, c in positions]


def segments_to_cells_vertical(segments):
    cells = set()
    for r, spans in segments.items():
        for left, right in spans:
            for c in range(left, right + 1):
                cells.add((r, c))
    return cells


def segments_to_cells_horizontal(segments):
    cells = set()
    for c, spans in segments.items():
        for top, bottom in spans:
            for r in range(top, bottom + 1):
                cells.add((r, c))
    return cells


def choose_orientation(grid, barrier, fill_positions):
    barrier_cells = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value == barrier]
    rows = [r for r, _ in fill_positions]
    cols = [c for _, c in fill_positions]
    top = min(r for r, _ in barrier_cells)
    bottom = max(r for r, _ in barrier_cells)
    left = min(c for _, c in barrier_cells)
    right = max(c for _, c in barrier_cells)
    rmin = min(rows)
    rmax = max(rows)
    cmin = min(cols)
    cmax = max(cols)
    distances = {
        "up": rmin - top,
        "down": bottom - rmax,
        "left": cmin - left,
        "right": right - cmax,
    }
    order = {"up": 0, "down": 1, "left": 2, "right": 3}
    nearest = min(distances.items(), key=lambda item: (item[1], order[item[0]]))[0]
    opposite = {"up": "down", "down": "up", "left": "right", "right": "left"}
    return opposite[nearest], (top, left, right)


def solve_b9e38dc0(grid):
    """Solve ARC task b9e38dc0."""
    background = dominant_color(grid)
    barrier = barrier_color(grid, background)
    fill = fill_color(grid, background, barrier)
    if fill is None:
        return copy_grid(grid)

    fill_positions = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value == fill]
    orientation, barrier_bounds = choose_orientation(grid, barrier, fill_positions)

    if orientation in {"down", "up"}:
        seeds = seed_segments_vertical(grid, background, fill_positions)
        bounds = barrier_bounds if orientation == "up" else None
        segments = propagate_vertical(grid, orientation, seeds, background, barrier, fill, bounds)
        cells = segments_to_cells_vertical(segments)
    else:
        grid_t = transpose_grid(grid)
        seeds = seed_segments_vertical(grid_t, background, transpose_positions(fill_positions))
        orient_t = "down" if orientation == "right" else "up"
        segments_t = propagate_vertical(grid_t, orient_t, seeds, background, barrier, fill, None)
        cells = segments_to_cells_horizontal(segments_t)

    cells -= set(fill_positions)
    result = copy_grid(grid)
    for r, c in cells:
        result[r][c] = fill
    return result
p = solve_b9e38dc0
