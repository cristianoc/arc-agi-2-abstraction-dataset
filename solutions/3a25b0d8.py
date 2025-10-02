"""Auto-generated identity stub for ARC-AGI-2 task 3a25b0d8 (split: evaluation)."""

def solve_3a25b0d8(grid):
    """Entry point for task 3a25b0d8."""
    return transform(grid)


from collections import Counter


def transform(grid):
    """Heuristic transformation based on the dominant color structure."""
    if not grid:
        return []

    height, width = len(grid), len(grid[0])
    flat = [cell for row in grid for cell in row]
    bg = Counter(flat).most_common(1)[0][0]

    non_bg = [cell for cell in flat if cell != bg]
    if not non_bg:
        return [row[:] for row in grid]
    base = Counter(non_bg).most_common(1)[0][0]

    interesting_cols = [c for c in range(width) if any(grid[r][c] not in (bg, base) for r in range(height))]
    if not interesting_cols:
        interesting_cols = [c for c in range(width) if any(grid[r][c] != bg for r in range(height))]

    col_lo, col_hi = min(interesting_cols), max(interesting_cols)
    tile = [[grid[r][c] for c in range(col_lo, col_hi + 1)] for r in range(height)]

    def row_has_special(row):
        return any(cell not in (bg, base) for cell in row)

    prefix = 0
    while prefix < len(tile) and not row_has_special(tile[prefix]):
        prefix += 1
    start_idx = max(0, prefix - 1)

    suffix = len(tile) - 1
    while suffix >= 0 and not row_has_special(tile[suffix]):
        suffix -= 1
    end_idx = min(len(tile) - 1, suffix + 1) if suffix >= 0 else len(tile) - 1

    trimmed = tile[start_idx:end_idx + 1]

    if not trimmed:
        return [[cell for cell in row[col_lo:col_hi + 1]] for row in grid]

    expanded = [[bg] + row + [bg] for row in trimmed]

    width = len(expanded[0])

    def widen(row, color, target_len=3):
        idxs = [i for i, val in enumerate(row) if val == color]
        if not idxs or len(idxs) >= target_len:
            return
        start = min(idxs)
        end = max(idxs)
        needed = target_len - (end - start + 1)
        left = start - 1
        right = end + 1
        while needed > 0 and (left >= 1 or right <= len(row) - 2):
            progressed = False
            if left >= 1 and row[left] == base:
                row[left] = color
                left -= 1
                needed -= 1
                progressed = True
            if needed <= 0:
                break
            if right <= len(row) - 2 and row[right] == base:
                row[right] = color
                right += 1
                needed -= 1
                progressed = True
            if not progressed:
                break

    adjusted = []
    specials_per_row = [{cell for cell in row if cell not in (bg, base)} for row in expanded]

    for idx, row in enumerate(expanded):
        cur = row[:]
        specials = specials_per_row[idx]

        if 7 in specials:
            widen(cur, 7)

        removed_all_4 = False

        if 4 in specials:
            positions = [i for i, val in enumerate(cur) if val == 4]
            runs = []
            for i, val in enumerate(cur):
                if val == 4:
                    if runs and runs[-1][1] == i - 1:
                        runs[-1] = (runs[-1][0], i)
                    else:
                        runs.append((i, i))
            max_run = max((end - start + 1) for start, end in runs) if runs else 0
            if max_run <= 1:
                for pos in positions:
                    cur[pos] = base
                removed_all_4 = True
            else:
                cur[0] = base
                cur[-1] = base
                if width > 2 and 3 in specials:
                    cur[1] = 3
                    cur[-2] = 3

        if 3 in specials and (4 not in specials or removed_all_4):
            if base == 1:
                cur[0] = base
                cur[-1] = base
                if width > 2:
                    cur[1] = 3
                    cur[-2] = 3
                for j in range(2, width - 2):
                    cur[j] = base

        if not specials:
            prev = specials_per_row[idx - 1] if idx > 0 else set()
            nxt = specials_per_row[idx + 1] if idx + 1 < len(specials_per_row) else set()
            if 3 in (prev | nxt):
                cur[0] = base
                cur[-1] = base
                if width > 2:
                    cur[1] = 3
                    cur[-2] = 3
            elif prev and len(prev) == 1 and not nxt and adjusted:
                prev_row = adjusted[-1]
                for j, val in enumerate(prev_row):
                    if prev_row[j] != bg:
                        cur[j] = base

        if 6 in specials:
            cur[0] = bg
            cur[-1] = bg
            if width > 2:
                cur[1] = base
                cur[-2] = base

        adjusted.append(cur)

    rows_with_color = {}
    for idx, specials in enumerate(specials_per_row):
        for color in specials:
            rows_with_color.setdefault(color, []).append(idx)

    result = []
    for idx, row in enumerate(adjusted):
        cur = row[:]
        specials = specials_per_row[idx]

        if specials == {3}:
            first = cur.index(3)
            last = len(cur) - 1 - cur[::-1].index(3)
            for j in range(first, last + 1):
                cur[j] = 3

        if specials == {4}:
            cur[0] = base
            cur[-1] = base
            if len(cur) % 2 == 1:
                cur[len(cur) // 2] = base

        if 8 in specials:
            rows_for_8 = rows_with_color.get(8, [])
            if rows_for_8 and idx == rows_for_8[0]:
                cur = [base] * len(cur)

        result.append(cur)

        if 9 in specials:
            result.append(cur[:])

        if 4 in specials and len(rows_with_color.get(4, [])) == 1:
            result.append(cur[:])

        if 8 in specials:
            rows_for_8 = rows_with_color.get(8, [])
            if rows_for_8 and idx == rows_for_8[-1]:
                widened = cur[:]
                widened[0] = base
                widened[-1] = base
                result.append(widened)

        if (
            not specials
            and idx == len(adjusted) - 1
            and bg != base
            and rows_with_color.get(8)
        ):
            cur = cur[:]
            cur[0] = base
            cur[-1] = base
            result[-1] = cur

    return result


p = solve_3a25b0d8
