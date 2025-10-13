"""Solver for ARC-AGI-2 task 5545f144 (split: evaluation)."""

from collections import Counter

def solve_5545f144(grid):
    """Compress repeated horizontal segments and retain the salient pattern."""

    height = len(grid)
    width = len(grid[0])

    # Identify the dominant background color.
    background = Counter(val for row in grid for val in row).most_common(1)[0][0]

    # Separator columns are uniform and use a non-background color.
    separator_cols = [
        c
        for c in range(width)
        if len({grid[r][c] for r in range(height)}) == 1 and grid[0][c] != background
    ]

    segments = []
    start = 0
    for c in range(width + 1):
        if c == width or c in separator_cols:
            if start < c:
                segments.append((start, c))
            start = c + 1
    if not segments:
        segments = [(0, width)]

    segment_width = segments[0][1] - segments[0][0]
    if any((end - begin) != segment_width for begin, end in segments):
        return [row[:segment_width] for row in grid]

    if len(segments) == 1:
        return [row[:segment_width] for row in grid]

    separator_set = set(separator_cols)
    highlight_counts = Counter(
        grid[r][c]
        for r in range(height)
        for c in range(width)
        if c not in separator_set and grid[r][c] != background
    )
    if not highlight_counts:
        return [[background] * segment_width for _ in range(height)]
    highlight = highlight_counts.most_common(1)[0][0]

    n_segments = len(segments)
    counts = [[0] * segment_width for _ in range(height)]
    segments_with_highlight = [set() for _ in range(height)]
    for s_idx, (begin, end) in enumerate(segments):
        for r in range(height):
            row = grid[r]
            for offset in range(segment_width):
                c = begin + offset
                if c >= end:
                    break
                if row[c] == highlight:
                    counts[r][offset] += 1
                    segments_with_highlight[r].add(s_idx)

    positive_cols = [[j for j, val in enumerate(row) if val > 0] for row in counts]
    full_cols = [[j for j, val in enumerate(row) if val == n_segments] for row in counts]
    has_partial = [any(0 < val < n_segments for val in row) for row in counts]

    result = [[background] * segment_width for _ in range(height)]
    highlight_cells = set()

    if n_segments == 2:
        center_col = None
        for r, cols in enumerate(full_cols):
            if cols:
                center_col = cols[0]
                break
        if center_col is None:
            center_col = segment_width // 2
        used_close = False
        for r in range(height):
            pos = positive_cols[r]
            if center_col < segment_width and counts[r][center_col] == n_segments:
                highlight_cells.add((r, center_col))
                continue
            if not pos:
                break
            close = [j for j in pos if abs(j - center_col) <= 2]
            if close:
                mapped = set()
                for j in close:
                    delta = j - center_col
                    if delta > 1:
                        delta = 1
                    elif delta < -1:
                        delta = -1
                    mapped.add(center_col + delta)
                for j in mapped:
                    if 0 <= j < segment_width:
                        highlight_cells.add((r, j))
                used_close = True
            else:
                if used_close:
                    break
                if 0 <= center_col < segment_width:
                    highlight_cells.add((r, center_col))
    else:
        for r, cols in enumerate(full_cols):
            if cols and has_partial[r]:
                for j in cols:
                    highlight_cells.add((r, j))

        for r, segs in enumerate(segments_with_highlight):
            if segs == {0}:
                pos = positive_cols[r]
                if len(pos) >= 2:
                    shift = min(pos)
                    for j in pos:
                        nj = j - shift
                        if 0 <= nj < segment_width:
                            highlight_cells.add((r, nj))

        for r, cols in enumerate(full_cols):
            if not cols or not has_partial[r]:
                continue
            for j in cols:
                prev = r - 1
                if prev < 0:
                    continue
                prev_segs = segments_with_highlight[prev]
                if prev_segs == {0} and len(positive_cols[prev]) == 1:
                    length = n_segments - 1
                    start = max(0, min(segment_width - length, j - (length - 1) // 2))
                    for offset in range(length):
                        highlight_cells.add((prev, start + offset))

    for r, c in highlight_cells:
        if 0 <= r < height and 0 <= c < segment_width:
            result[r][c] = highlight

    return result


p = solve_5545f144
