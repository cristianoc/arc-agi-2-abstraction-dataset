"""Auto-generated identity stub for ARC-AGI-2 task b5ca7ac4 (split: evaluation)."""

def solve_b5ca7ac4(grid):
    """Reposition 5x5 ring objects by outer color (high-left, low-right)."""

    height = len(grid)
    width = len(grid[0]) if height else 0
    ring_size = 5

    def copy_grid(values):
        return [row[:] for row in values]

    def detect_objects():
        objects = []
        seen = set()
        for r in range(height - 2):
            for c in range(width - 2):
                inner = grid[r][c]
                if inner == 0:
                    continue
                if any(grid[r + dr][c + dc] != inner for dr in range(3) for dc in range(3)):
                    continue
                if r > 0 and grid[r - 1][c] == inner:
                    continue
                if c > 0 and grid[r][c - 1] == inner:
                    continue
                if not (0 < r and 0 < c and r + 2 < height - 1 and c + 2 < width - 1):
                    continue
                top, bottom = r - 1, r + 3
                left, right = c - 1, c + 3
                border = set()
                for x in range(left, right + 1):
                    border.add(grid[top][x])
                    border.add(grid[bottom][x])
                for y in range(top, bottom + 1):
                    border.add(grid[y][left])
                    border.add(grid[y][right])
                border.discard(inner)
                if len(border) != 1:
                    continue
                outer = border.pop()
                if outer == 0:
                    continue
                bbox = (top, bottom, left, right)
                if bbox in seen:
                    continue
                seen.add(bbox)
                pattern = [grid[y][left : right + 1] for y in range(top, bottom + 1)]
                objects.append({
                    "outer": outer,
                    "bbox": bbox,
                    "pattern": [row[:] for row in pattern],
                })
        objects.sort(key=lambda obj: (obj["bbox"][0], obj["bbox"][2]))
        return objects

    objects = detect_objects()
    outer_colors = sorted({obj["outer"] for obj in objects})
    if len(objects) == 0 or len(outer_colors) != 2:
        return copy_grid(grid)

    left_color = max(outer_colors)
    right_color = min(outer_colors)

    counts = [0] * 10
    for row in grid:
        for value in row:
            counts[value] += 1
    background = max(range(10), key=lambda color: (counts[color], color))

    def build_lanes(start, step):
        lanes = []
        position = start
        if step > 0:
            while position <= width - ring_size:
                lanes.append(position)
                position += step
        else:
            while position >= 0:
                lanes.append(position)
                position += step
        if not lanes:
            lanes.append(max(0, min(start, width - ring_size)))
        return lanes

    def place_group(group, lanes, order_fn):
        usage = {lane: [] for lane in lanes}
        placements = []
        for obj in group:
            top, bottom, left, _ = obj["bbox"]
            lane_order = order_fn(obj, lanes)
            chosen = None
            for lane in lane_order:
                if lane not in usage:
                    continue
                overlap = any(not (bottom < used_top or top > used_bottom) for used_top, used_bottom in usage[lane])
                if overlap:
                    continue
                chosen = lane
                break
            if chosen is None:
                chosen = lanes[0]
            usage.setdefault(chosen, []).append((top, bottom))
            placements.append((obj, chosen))
        return placements

    def render(placed_left, placed_right):
        output = [[background] * width for _ in range(height)]
        for obj, lane in placed_left + placed_right:
            top, _, _, _ = obj["bbox"]
            pattern = obj["pattern"]
            for dy in range(ring_size):
                row = output[top + dy]
                for dx in range(ring_size):
                    row[lane + dx] = pattern[dy][dx]
        return output

    left_objects = [obj for obj in objects if obj["outer"] == left_color]
    right_objects = [obj for obj in objects if obj["outer"] == right_color]

    left_lanes = build_lanes(0, ring_size)
    right_lanes = build_lanes(width - ring_size, -ring_size)

    def left_order(_obj, lanes):
        return lanes

    if right_objects:
        average_left = sum(obj["bbox"][2] for obj in right_objects) / len(right_objects)
    else:
        average_left = 0

    def right_order(obj, lanes):
        preferred = lanes[0] if obj["bbox"][2] >= average_left and lanes else (lanes[1] if len(lanes) > 1 else lanes[0])
        ordered = [preferred]
        for lane in lanes:
            if lane not in ordered:
                ordered.append(lane)
        return ordered

    placed_left = place_group(left_objects, left_lanes, left_order)
    placed_right = place_group(right_objects, right_lanes, right_order)

    return render(placed_left, placed_right)


p = solve_b5ca7ac4
