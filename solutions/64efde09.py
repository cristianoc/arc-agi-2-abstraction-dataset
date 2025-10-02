"""Auto-generated identity stub for ARC-AGI-2 task 64efde09 (split: evaluation)."""

from collections import deque


def solve_64efde09(grid):
    """Project three accent colors as shadows around the primary motifs."""

    background = 8
    height = len(grid)
    width = len(grid[0])
    out = [row[:] for row in grid]

    def find_components():
        seen = [[False] * width for _ in range(height)]
        comps = []
        for r in range(height):
            for c in range(width):
                if grid[r][c] == background or seen[r][c]:
                    continue
                q = deque([(r, c)])
                seen[r][c] = True
                cells = []
                while q:
                    x, y = q.popleft()
                    cells.append((x, y))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < height and 0 <= ny < width:
                            if not seen[nx][ny] and grid[nx][ny] != background:
                                seen[nx][ny] = True
                                q.append((nx, ny))
                comps.append(cells)
        return comps

    def bbox(cells):
        rs = [r for r, _ in cells]
        cs = [c for _, c in cells]
        return min(rs), min(cs), max(rs), max(cs)

    def vertical_offsets(h):
        if h >= 9:
            return [1, 3, 5]
        if h >= 7:
            return [1, h - 3, h - 2]
        if h >= 5:
            return [1, h - 2, h - 1]
        # degenerate fallback; not expected but keeps code robust
        return [min(1, h - 1)] * 3

    components = find_components()
    accent_colors = sorted(
        grid[r][c]
        for comp in components
        if len(comp) == 1
        for (r, c) in comp
    )

    base_components = [comp for comp in components if len(comp) > 1]
    boxes = [bbox(comp) for comp in base_components]

    vertical_indices = [
        idx
        for idx, (top, left, bottom, right) in enumerate(boxes)
        if (bottom - top) > (right - left)
    ]
    vertical_indices.sort(key=lambda idx: (boxes[idx][1] + boxes[idx][3]) / 2)

    for order, idx in enumerate(vertical_indices):
        top, left, bottom, right = boxes[idx]
        h = bottom - top + 1
        direction_left = order % 2 == 0
        offsets = [off for off in vertical_offsets(h) if 0 <= off < h]
        palette = accent_colors if h >= 9 else list(reversed(accent_colors))
        for tone, offset in zip(palette, offsets):
            row = top + offset
            if direction_left:
                col = left - 1
                while col >= 0 and out[row][col] == background:
                    out[row][col] = tone
                    col -= 1
            else:
                col = right + 1
                while col < width and out[row][col] == background:
                    out[row][col] = tone
                    col += 1

    for idx, (top, left, bottom, right) in enumerate(boxes):
        h = bottom - top + 1
        w = right - left + 1
        if h > w:
            continue  # already handled as vertical shadow

        if top <= 2:
            row_below_top = top - 1
            row_two_above = top - 2
            target_cols = [right - 5, right - 3, right - 1]
            if row_below_top >= 0:
                for col, tone in zip(target_cols, sorted(accent_colors, reverse=True)):
                    if 0 <= col < width and out[row_below_top][col] == background:
                        out[row_below_top][col] = tone
            if row_two_above >= 0:
                for col, tone in zip((right - 5, right - 1), (accent_colors[-1], accent_colors[0])):
                    if 0 <= col < width and out[row_two_above][col] == background:
                        out[row_two_above][col] = tone
        else:
            shadow_cols = sorted({left + 1, left + 2, right - 1})
            for col, tone in zip(shadow_cols, accent_colors):
                if not (left <= col <= right):
                    continue
                row = bottom + 1
                while row < height and out[row][col] == background:
                    out[row][col] = tone
                    row += 1

    return out


p = solve_64efde09
