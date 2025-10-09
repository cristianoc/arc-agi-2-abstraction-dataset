"""Solver for ARC-AGI-2 task 7b80bb43."""

from collections import Counter


def solve_7b80bb43(grid):
    """Regularise axis-aligned linework to match the task's rectified patterns."""

    height = len(grid)
    width = len(grid[0]) if height else 0
    if height == 0 or width == 0:
        return [row[:] for row in grid]

    flat = [cell for row in grid for cell in row]
    counts = Counter(flat)
    if not counts:
        return [row[:] for row in grid]

    background = counts.most_common(1)[0][0]
    foreground_candidates = [color for color in counts if color != background]
    if not foreground_candidates:
        return [row[:] for row in grid]

    foreground = max(foreground_candidates, key=lambda color: counts[color])
    if counts[foreground] == 0:
        return [row[:] for row in grid]

    mask = [[1 if cell == foreground else 0 for cell in row] for row in grid]
    row_counts = [sum(row_mask) for row_mask in mask]
    pivot_row = max(range(height), key=lambda r: row_counts[r])

    col_counts = [sum(mask[r][c] for r in range(height)) for c in range(width)]
    col_threshold = max(2, (height + 3) // 4)
    key_cols = [c for c, cnt in enumerate(col_counts) if cnt >= col_threshold]
    if not key_cols:
        ordered = sorted(range(width), key=lambda c: col_counts[c], reverse=True)
        key_cols = ordered[: min(2, len(ordered))]
    key_cols = sorted(key_cols)

    vertical_min_run = 2
    vertical_keep_gap = 2
    vertical_gap_bridge = 3
    vertical_bridge_min_run = 2
    vertical_support_radius = 2

    col_masks: dict[int, list[bool]] = {}
    for col in key_cols:
        rows_with_color = [r for r in range(height) if mask[r][col]]
        if not rows_with_color:
            continue

        runs: list[tuple[int, int]] = []
        start = prev = rows_with_color[0]
        for row in rows_with_color[1:]:
            if row == prev + 1:
                prev = row
            else:
                runs.append((start, prev))
                start = prev = row
        runs.append((start, prev))

        kept_runs: list[tuple[int, int]] = []
        for idx, (run_start, run_end) in enumerate(runs):
            run_length = run_end - run_start + 1
            if run_length >= vertical_min_run:
                kept_runs.append((run_start, run_end))
                continue

            gap_prev = run_start - runs[idx - 1][1] - 1 if idx > 0 else None
            gap_next = runs[idx + 1][0] - run_end - 1 if idx + 1 < len(runs) else None
            if any(gap is not None and gap <= vertical_keep_gap for gap in (gap_prev, gap_next)):
                kept_runs.append((run_start, run_end))

        if not kept_runs:
            continue

        column_mask = [False] * height
        for run_start, run_end in kept_runs:
            for row in range(run_start, run_end + 1):
                column_mask[row] = True

        for (s1, e1), (s2, e2) in zip(kept_runs, kept_runs[1:]):
            len_first = e1 - s1 + 1
            len_second = e2 - s2 + 1
            gap = s2 - e1 - 1
            if gap <= 0 or gap > vertical_gap_bridge:
                continue
            if len_first < vertical_bridge_min_run or len_second < vertical_bridge_min_run:
                continue

            support_found = False
            for row in range(e1 + 1, s2):
                lo = max(0, col - vertical_support_radius)
                hi = min(width, col + vertical_support_radius + 1)
                if any(mask[row][cc] for cc in range(lo, hi)):
                    support_found = True
                    break
            if support_found:
                for row in range(e1 + 1, s2):
                    column_mask[row] = True

        col_masks[col] = column_mask

    horizontal_min_keep = 2
    small_segment_limit = 3
    horizontal_gap_bridge = 3

    segments_by_row: list[list[tuple[int, int]]] = []
    for row in range(height):
        segments: list[tuple[int, int]] = []
        col = 0
        while col < width:
            if mask[row][col]:
                seg_start = col
                while col + 1 < width and mask[row][col + 1]:
                    col += 1
                seg_end = col
                segments.append((seg_start, seg_end))
            col += 1

        kept_segments: list[tuple[int, int]] = []
        for idx, (seg_start, seg_end) in enumerate(segments):
            seg_len = seg_end - seg_start + 1
            if seg_len >= horizontal_min_keep:
                kept_segments.append((seg_start, seg_end))
                continue

            if seg_len == 1:
                current_col = seg_start
                col_mask = col_masks.get(current_col)
                if current_col in key_cols and col_mask and col_mask[row]:
                    kept_segments.append((seg_start, seg_end))
                    continue

                if row == pivot_row:
                    gap_prev = None
                    if idx > 0:
                        gap_prev = seg_start - segments[idx - 1][1] - 1
                    gap_next = None
                    if idx + 1 < len(segments):
                        gap_next = segments[idx + 1][0] - seg_end - 1
                    if (gap_prev is not None and gap_prev <= horizontal_gap_bridge) or (
                        gap_next is not None and gap_next <= horizontal_gap_bridge
                    ):
                        kept_segments.append((seg_start, seg_end))

        segments_by_row.append(kept_segments)

    result = [[background for _ in range(width)] for _ in range(height)]

    for col, column_mask in col_masks.items():
        for row in range(height):
            if column_mask[row]:
                result[row][col] = foreground

    for row, segments in enumerate(segments_by_row):
        if not segments:
            continue

        segments = sorted(segments, key=lambda item: item[0])
        for seg_start, seg_end in segments:
            for col in range(seg_start, seg_end + 1):
                result[row][col] = foreground

        bridged = False
        for (s1, e1), (s2, e2) in zip(segments, segments[1:]):
            if bridged:
                break
            gap = s2 - e1 - 1
            if gap <= 0 or gap > horizontal_gap_bridge:
                continue

            len_right = e2 - s2 + 1
            if len_right > small_segment_limit:
                continue

            left_has_key = any(seg_col in key_cols for seg_col in range(s1, e1 + 1))
            right_has_key = any(seg_col in key_cols for seg_col in range(s2, e2 + 1))
            if not (left_has_key or right_has_key):
                continue

            for col in range(e1 + 1, s2):
                result[row][col] = foreground
            bridged = True

    return result


p = solve_7b80bb43
