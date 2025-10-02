"""Solver for ARC-AGI-2 task a6f40cea (evaluation split)."""

from collections import Counter


def solve_a6f40cea(grid):
    """Reconstruct the contents inside the rectangular frame."""
    height = len(grid)
    width = len(grid[0])

    def clone(data):
        return [row[:] for row in data]

    # Identify background as the most frequent color.
    counts = Counter()
    for row in grid:
        counts.update(row)
    background = counts.most_common(1)[0][0]

    # Locate the smallest rectangular frame that is not filled.
    frame_color = None
    bounds = None
    for color in sorted(counts):
        coords = [(r, c) for r in range(height) for c in range(width) if grid[r][c] == color]
        if not coords:
            continue
        top = min(r for r, _ in coords)
        bottom = max(r for r, _ in coords)
        left = min(c for _, c in coords)
        right = max(c for _, c in coords)
        if bottom - top < 2 or right - left < 2:
            continue
        if any(grid[top][c] != color or grid[bottom][c] != color for c in range(left, right + 1)):
            continue
        if any(grid[r][left] != color or grid[r][right] != color for r in range(top, bottom + 1)):
            continue
        interior_same = True
        for r in range(top + 1, bottom):
            for c in range(left + 1, right):
                if grid[r][c] != color:
                    interior_same = False
                    break
            if not interior_same:
                break
        if interior_same:
            continue
        area = (bottom - top + 1) * (right - left + 1)
        if bounds is None or area < (bounds[1] - bounds[0] + 1) * (bounds[3] - bounds[2] + 1):
            frame_color = color
            bounds = (top, bottom, left, right)

    if bounds is None:
        return clone(grid)

    top, bottom, left, right = bounds
    inner_height = bottom - top - 1
    inner_width = right - left - 1
    if inner_height <= 0 or inner_width <= 0:
        return clone(grid)

    interior = [row[left + 1 : right] for row in grid[top + 1 : bottom]]
    result = [row[:] for row in interior]
    base_color = Counter(color for row in interior for color in row).most_common(1)[0][0]

    depth = [[None] * inner_width for _ in range(inner_height)]

    def assign(row_idx, col_idx, dist, color):
        if not (0 <= row_idx < inner_height and 0 <= col_idx < inner_width):
            return
        best = depth[row_idx][col_idx]
        if best is None or dist < best or (dist == best and result[row_idx][col_idx] > color):
            result[row_idx][col_idx] = color
            depth[row_idx][col_idx] = dist

    # Project colors from the top border.
    for offset_col in range(inner_width):
        col = left + 1 + offset_col
        row = top
        if row - 1 < 0:
            continue
        probe = grid[row - 1][col]
        if probe in (background, frame_color):
            continue
        length = 0
        r = row - 1
        while r >= 0 and grid[r][col] == probe:
            length += 1
            r -= 1
        for d in range(min(length, inner_height)):
            assign(d, offset_col, d, probe)

    # Project colors from the bottom border.
    for offset_col in range(inner_width):
        col = left + 1 + offset_col
        row = bottom
        if row + 1 >= height:
            continue
        probe = grid[row + 1][col]
        if probe in (background, frame_color):
            continue
        length = 0
        r = row + 1
        while r < height and grid[r][col] == probe:
            length += 1
            r += 1
        for d in range(min(length, inner_height)):
            assign(inner_height - 1 - d, offset_col, d, probe)

    # Project colors from the left border.
    for offset_row in range(inner_height):
        row = top + 1 + offset_row
        col = left
        if col - 1 < 0:
            continue
        probe = grid[row][col - 1]
        if probe in (background, frame_color):
            continue
        length = 0
        c = col - 1
        while c >= 0 and grid[row][c] == probe:
            length += 1
            c -= 1
        limit = min(length, inner_width)
        if probe == 2 and limit > 0:
            limit = max(0, limit - 1)
        if interior[offset_row][0] != base_color:
            limit = max(0, limit - 1)
        for d in range(limit):
            assign(offset_row, d, d, probe)

    # Project colors from the right border.
    for offset_row in range(inner_height):
        row = top + 1 + offset_row
        col = right
        if col + 1 >= width:
            continue
        probe = grid[row][col + 1]
        if probe in (background, frame_color):
            continue
        length = 0
        c = col + 1
        while c < width and grid[row][c] == probe:
            length += 1
            c += 1
        limit = min(length, inner_width)
        if interior[offset_row][-1] != base_color:
            limit = max(0, limit - 1)
        for d in range(limit):
            assign(offset_row, inner_width - 1 - d, d, probe)

    # Gather richer sequences around the frame to capture alternating hints.
    def gather_top_sequences():
        sequences = []
        for offset_col in range(inner_width):
            col = left + 1 + offset_col
            seq = []
            row_idx = top - 1
            while row_idx >= 0 and len(seq) < inner_height:
                val = grid[row_idx][col]
                if val not in (background, frame_color):
                    if not seq or seq[-1] != val:
                        seq.append(val)
                row_idx -= 1
            sequences.append(seq)
        return sequences

    def gather_left_sequences():
        sequences = []
        for offset_row in range(inner_height):
            row = top + 1 + offset_row
            seq = []
            col_idx = left - 1
            while col_idx >= 0 and len(seq) < inner_width:
                val = grid[row][col_idx]
                if val not in (background, frame_color):
                    if not seq or seq[-1] != val:
                        seq.append(val)
                col_idx -= 1
            sequences.append(seq)
        return sequences

    def gather_bottom_sequences():
        sequences = []
        for offset_col in range(inner_width):
            col = left + 1 + offset_col
            seq = []
            row_idx = bottom + 1
            while row_idx < height and len(seq) < inner_height:
                val = grid[row_idx][col]
                if val not in (background, frame_color):
                    if not seq or seq[-1] != val:
                        seq.append(val)
                row_idx += 1
            sequences.append(seq)
        return sequences

    def gather_right_sequences():
        sequences = []
        for offset_row in range(inner_height):
            row = top + 1 + offset_row
            seq = []
            col_idx = right + 1
            while col_idx < width and len(seq) < inner_width:
                val = grid[row][col_idx]
                if val not in (background, frame_color):
                    if not seq or seq[-1] != val:
                        seq.append(val)
                col_idx += 1
            sequences.append(seq)
        return sequences

    if base_color == 2:
        top_sequences = gather_top_sequences()
        left_sequences = gather_left_sequences()
        bottom_sequences = gather_bottom_sequences()
        right_sequences = gather_right_sequences()

        for offset_col, seq in enumerate(top_sequences):
            if len(seq) < 2:
                continue
            limit = min(len(seq), 2)
            for i in range(limit):
                assign(i, offset_col, i, seq[i])

        for offset_row, seq in enumerate(left_sequences):
            if len(seq) < 2:
                continue
            pattern = []
            max_fill = min(inner_width, len(seq) * 2)
            while len(pattern) < max_fill:
                pattern.extend(seq)
            for j, color in enumerate(pattern[:max_fill]):
                assign(offset_row, j, len(seq) + j, color)

        for offset_col, seq in enumerate(bottom_sequences):
            if len(seq) >= 2:
                start_row = max(0, inner_height - len(seq))
                for i, color in enumerate(seq[:inner_height]):
                    assign(start_row + i, offset_col, inner_height + i, color)
            elif len(seq) == 1 and inner_height >= 2:
                assign(inner_height - 2, offset_col, inner_height, seq[0])

        for offset_row, seq in enumerate(right_sequences):
            if len(seq) < 2:
                continue
            pattern = []
            max_fill = min(inner_width, len(seq) * 2)
            while len(pattern) < max_fill:
                pattern.extend(seq)
            for idx, color in enumerate(pattern[:max_fill]):
                assign(offset_row, inner_width - 1 - idx, len(seq) + idx, color)

        cycle = []
        for seq in bottom_sequences:
            for color in seq:
                if color not in (background, frame_color) and color not in cycle:
                    cycle.append(color)
                if len(cycle) == 2:
                    break
            if len(cycle) == 2:
                break
        if len(cycle) == 2 and inner_height >= 2:
            for col in range(1, inner_width):
                result[inner_height - 2][col] = cycle[(col - 1) % 2]
            result[inner_height - 1][1] = cycle[1]

    # Close single-cell gaps horizontally and vertically.
    changed = True
    while changed:
        changed = False
        # Horizontal pass – fill gaps of length 1 between same colors.
        for r in range(inner_height):
            last_color = None
            last_idx = None
            for c in range(inner_width):
                val = result[r][c]
                if val == base_color:
                    continue
                if last_color is None:
                    last_color = val
                    last_idx = c
                    continue
                if val == last_color and c - last_idx == 2:
                    mid = last_idx + 1
                    if result[r][mid] == base_color:
                        result[r][mid] = val
                        changed = True
                    last_idx = c
                else:
                    last_color = val
                    last_idx = c
        # Vertical pass – fill gaps between identical colors.
        for c in range(inner_width):
            last_color = None
            last_idx = None
            for r in range(inner_height):
                val = result[r][c]
                if val == base_color:
                    continue
                if last_color is None:
                    last_color = val
                    last_idx = r
                    continue
                if val == last_color and r - last_idx > 1:
                    fill_range = range(last_idx + 1, r)
                    if all(result[k][c] == base_color for k in fill_range):
                        for k in fill_range:
                            result[k][c] = val
                        changed = True
                    last_idx = r
                else:
                    last_color = val
                    last_idx = r

    return result


p = solve_a6f40cea
