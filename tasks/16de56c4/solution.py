"""Solver for ARC-AGI-2 task 16de56c4."""

from math import gcd


def _copy_grid(grid):
    return [row[:] for row in grid]


def _apply_row_rule(grid):
    result = _copy_grid(grid)
    width = len(grid[0])
    for r, row in enumerate(grid):
        nonzero_cols = [c for c, v in enumerate(row) if v]
        if not nonzero_cols:
            continue
        colors = {row[c] for c in nonzero_cols}
        if len(colors) > 2:
            continue

        last_col = nonzero_cols[-1]
        color = row[last_col]
        same_color_cols = [c for c in nonzero_cols if row[c] == color]
        if len(same_color_cols) >= 2:
            diffs = [same_color_cols[i + 1] - same_color_cols[i] for i in range(len(same_color_cols) - 1)]
            step = diffs[0]
            for d in diffs[1:]:
                step = gcd(step, d)
            if step == 0:
                continue
            start = min(same_color_cols)
            for c in range(start, -1, -step):
                result[r][c] = color
            for c in range(start + step, width, step):
                result[r][c] = color
        else:
            other_cols = [c for c in nonzero_cols if c != last_col]
            if not other_cols:
                continue
            freq = {}
            for c in other_cols:
                freq[row[c]] = freq.get(row[c], 0) + 1
            if all(count < 2 for count in freq.values()):
                continue
            step = 0
            for c in other_cols:
                delta = abs(last_col - c)
                step = delta if step == 0 else gcd(step, delta)
            if step == 0:
                continue
            for c in range(last_col, -1, -step):
                result[r][c] = color
    return result


def _apply_column_rule(grid, original):
    height = len(grid)
    width = len(grid[0])
    result = _copy_grid(grid)
    for c in range(width):
        orig_col = [original[r][c] for r in range(height)]
        positions_by_color = {}
        for r, val in enumerate(orig_col):
            if val:
                positions_by_color.setdefault(val, []).append(r)

        for color, rows in positions_by_color.items():
            if len(rows) < 2:
                continue
            rows.sort()
            diffs = [rows[i + 1] - rows[i] for i in range(len(rows) - 1)]
            step = diffs[0]
            for d in diffs[1:]:
                step = gcd(step, d)
            if step == 0:
                continue
            for r in rows:
                result[r][c] = color
            r = rows[0] - step
            while r >= 0:
                val = orig_col[r]
                if val and val != color:
                    break
                result[r][c] = color
                r -= step

        for color, rows in positions_by_color.items():
            if len(rows) != 1:
                continue
            base_row = rows[0]
            repeated_sets = [pos for col, pos in positions_by_color.items() if col != color and len(pos) >= 2]
            if not repeated_sets:
                continue
            target_rows = []
            for pos in repeated_sets:
                target_rows.extend([r for r in pos if r > base_row])
            if not target_rows:
                continue
            step_base = 0
            for r in target_rows:
                delta = r - base_row
                step_base = delta if step_base == 0 else gcd(step_base, delta)
            if step_base == 0:
                continue
            flat = sorted(set(target_rows))
            if len(flat) >= 2:
                step_repeat = flat[1] - flat[0]
                for i in range(1, len(flat) - 1):
                    step_repeat = gcd(step_repeat, flat[i + 1] - flat[i])
                if step_repeat and step_repeat != step_base:
                    continue
            for r in target_rows:
                if (r - base_row) % step_base == 0:
                    result[r][c] = color
    return result


def solve_16de56c4(grid):
    after_rows = _apply_row_rule(grid)
    after_cols = _apply_column_rule(after_rows, grid)
    return after_cols


def p(grid):
    return solve_16de56c4(grid)
