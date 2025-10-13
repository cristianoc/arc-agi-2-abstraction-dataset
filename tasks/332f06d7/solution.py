"""Solver for ARC-AGI-2 task 332f06d7 (evaluation split)."""

DIRECTIONS = ((-1, 0, "up"), (1, 0, "down"), (0, -1, "left"), (0, 1, "right"))


def solve_332f06d7(grid):
    """Relocate the lone zero block based on colour-2 adjacency cues."""

    def collect(color):
        return [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == color]

    def bbox(cells):
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        return min(rows), min(cols), max(rows), max(cols)

    def adjacency(cells, target=3):
        if not cells:
            return set()
        h, w = len(grid), len(grid[0])
        adj = set()
        for r, c in cells:
            for dr, dc, name in DIRECTIONS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w:
                    if grid[nr][nc] == target:
                        adj.add(name)
                else:
                    adj.add(name)
        return adj

    def centre(box):
        r0, c0, r1, c1 = box
        return (r0 + r1) / 2.0, (c0 + c1) / 2.0

    zeros = collect(0)
    if not zeros:
        return [row[:] for row in grid]

    ones = collect(1)
    if not ones:
        return [row[:] for row in grid]

    twos = collect(2)
    zero_box = bbox(zeros)
    one_box = bbox(ones)
    zero_height = zero_box[2] - zero_box[0] + 1
    zero_width = zero_box[3] - zero_box[1] + 1
    zero_cells = {(r, c) for r in range(zero_box[0], zero_box[2] + 1) for c in range(zero_box[1], zero_box[3] + 1)}
    one_center = centre(one_box)

    if not twos:
        target_pos = (zero_box[0], zero_box[1])
    else:
        two_box = bbox(twos)
        two_cells = {(r, c) for r in range(two_box[0], two_box[2] + 1) for c in range(two_box[1], two_box[3] + 1)}
        two_center = centre(two_box)
        color2_adj = adjacency(two_cells)
        missing_dirs = {name for _, _, name in DIRECTIONS} - color2_adj
        color2_dist_one = abs(two_center[0] - one_center[0]) + abs(two_center[1] - one_center[1])

        candidates = []
        h, w = len(grid), len(grid[0])
        for top in range(h - zero_height + 1):
            for left in range(w - zero_width + 1):
                block = [grid[r][c] for r in range(top, top + zero_height) for c in range(left, left + zero_width)]
                if len(set(block)) != 1:
                    continue
                colour = block[0]
                if colour not in (1, 2):
                    continue
                cells = {(r, c) for r in range(top, top + zero_height) for c in range(left, left + zero_width)}
                adj = adjacency(cells)
                center = (top + (zero_height - 1) / 2.0, left + (zero_width - 1) / 2.0)
                entry = {
                    "pos": (top, left),
                    "is_two": colour == 2,
                    "adj": adj,
                    "contains_missing": not missing_dirs or missing_dirs <= adj,
                    "adj_len": len(adj),
                    "dist_one": abs(center[0] - one_center[0]) + abs(center[1] - one_center[1]),
                    "dist_two": abs(center[0] - two_center[0]) + abs(center[1] - two_center[1]),
                }
                candidates.append(entry)

        two_entry = next((c for c in candidates if c["is_two"]), None)
        filtered = [c for c in candidates if not c["is_two"] and c["contains_missing"] and c["adj_len"] == len(color2_adj)]
        filtered.sort(key=lambda c: (c["dist_one"], c["dist_two"], c["pos"]))

        threshold = 5.0
        if filtered and color2_dist_one - filtered[0]["dist_one"] >= threshold:
            target_pos = filtered[0]["pos"]
        elif two_entry is not None:
            target_pos = two_entry["pos"]
        elif filtered:
            target_pos = filtered[0]["pos"]
        else:
            target_pos = (two_box[0], two_box[1])

    out = [row[:] for row in grid]
    for r, c in zero_cells:
        out[r][c] = 1

    tr, tc = target_pos
    for r in range(tr, tr + zero_height):
        for c in range(tc, tc + zero_width):
            out[r][c] = 0

    return out


p = solve_332f06d7
