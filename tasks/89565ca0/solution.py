"""Auto-generated identity stub for ARC-AGI-2 task 89565ca0 (split: evaluation)."""

from collections import Counter, defaultdict, deque


def solve_89565ca0(grid):
    """Puzzle-specific solver filled in over multiple refinement steps."""
    if not grid or not grid[0]:
        return []

    h, w = len(grid), len(grid[0])
    color_cells = defaultdict(list)
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val != 0:
                color_cells[val].append((r, c))
    if not color_cells:
        return []

    def component_count(color):
        seen = [[False] * w for _ in range(h)]
        components = 0
        for sr in range(h):
            for sc in range(w):
                if grid[sr][sc] == color and not seen[sr][sc]:
                    components += 1
                    dq = deque([(sr, sc)])
                    seen[sr][sc] = True
                    while dq:
                        cr, cc = dq.pop()
                        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            nr, nc = cr + dr, cc + dc
                            if (
                                0 <= nr < h
                                and 0 <= nc < w
                                and grid[nr][nc] == color
                                and not seen[nr][nc]
                            ):
                                seen[nr][nc] = True
                                dq.append((nr, nc))
        return components

    def stripe_ranges(length, parts):
        base = length // parts
        extra = length % parts
        start = 0
        for idx in range(parts):
            end = start + base + (1 if idx < extra else 0)
            yield start, end
            start = end

    components = {color: component_count(color) for color in color_cells}
    filler = max(components, key=lambda col: components[col])

    stripe_dominators = []
    for start, end in stripe_ranges(h, 4):
        if start == end:
            stripe_dominators.append(None)
            continue
        counts = Counter()
        for r in range(start, end):
            for c in range(w):
                val = grid[r][c]
                if val != 0:
                    counts[val] += 1
        if not counts:
            stripe_dominators.append(None)
            continue
        winner = None
        winner_count = -1
        for color, count in counts.items():
            if (
                winner is None
                or count > winner_count
                or (count == winner_count and color == filler and winner != filler)
            ):
                winner = color
                winner_count = count
        stripe_dominators.append(winner)

    bottommost_dominator = {color: None for color in color_cells}
    for idx, dom_color in enumerate(stripe_dominators):
        if dom_color is None:
            continue
        previous = bottommost_dominator.get(dom_color)
        if previous is None or idx > previous:
            bottommost_dominator[dom_color] = idx

    areas = {color: len(cells) for color, cells in color_cells.items()}
    non_filler_colors = [color for color in color_cells if color != filler]
    if not non_filler_colors:
        return [[filler] * 4]

    no_dom_colors = sorted(
        (color for color in non_filler_colors if bottommost_dominator[color] is None),
        key=lambda col: (areas[col], col),
    )

    prefix_lengths = {}
    for rank, color in enumerate(no_dom_colors):
        prefix_lengths[color] = 1 if rank == 0 else 2

    for color in non_filler_colors:
        dom_idx = bottommost_dominator.get(color)
        if dom_idx is None:
            continue
        if dom_idx == 0:
            length = 2
        elif dom_idx in (1, 2):
            length = 3
        else:
            length = 4
        prefix_lengths[color] = length

    result_rows = []
    for color in sorted(non_filler_colors, key=lambda col: (prefix_lengths[col], col)):
        length = max(1, min(4, prefix_lengths[color]))
        row = [color] * length + [filler] * (4 - length)
        result_rows.append(row)

    return result_rows


p = solve_89565ca0
