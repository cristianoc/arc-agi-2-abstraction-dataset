"""Solver for ARC-AGI-2 task 80a900e0 (split: evaluation)."""

from collections import Counter, defaultdict


def solve_80a900e0(grid):
    """Extend diagonal handles into full stripes along the perpendicular axis."""
    rows, cols = len(grid), len(grid[0])
    output = [row[:] for row in grid]

    counts = Counter(val for row in grid for val in row)
    background = {c for c in (0, 1) if c in counts}
    if not background:
        # Fallback: treat the most common color as background if 0/1 absent.
        background = {counts.most_common(1)[0][0]}

    def find_runs(points, step):
        points = sorted(points)
        runs = []
        current = []
        for r, c in points:
            if not current:
                current = [(r, c)]
                continue
            prev_r, prev_c = current[-1]
            if (r - prev_r, c - prev_c) == step:
                current.append((r, c))
            else:
                if len(current) >= 3:
                    runs.append(current)
                current = [(r, c)]
        if len(current) >= 3:
            runs.append(current)
        return runs

    coords_by_color = defaultdict(list)
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value not in background:
                coords_by_color[value].append((r, c))

    for color, coords in coords_by_color.items():
        sum_groups = defaultdict(list)
        diff_groups = defaultdict(list)
        for r, c in coords:
            sum_groups[r + c].append((r, c))
            diff_groups[r - c].append((r, c))

        target_sums = set()
        target_diffs = set()
        has_sum_runs = False
        has_diff_runs = False

        for points in sum_groups.values():
            runs = find_runs(points, (1, -1))
            if runs:
                has_sum_runs = True
                for run in runs:
                    first_r, first_c = run[0]
                    last_r, last_c = run[-1]
                    target_diffs.add(first_r - first_c)
                    target_diffs.add(last_r - last_c)

        for points in diff_groups.values():
            runs = find_runs(points, (1, 1))
            if runs:
                has_diff_runs = True
                for run in runs:
                    first_r, first_c = run[0]
                    last_r, last_c = run[-1]
                    target_sums.add(first_r + first_c)
                    target_sums.add(last_r + last_c)

        if has_sum_runs and has_diff_runs:
            continue

        if has_sum_runs:
            for diff in target_diffs:
                for r in range(rows):
                    c = r - diff
                    if 0 <= c < cols:
                        original = grid[r][c]
                        current = output[r][c]
                        if (original in background) and (current in background or current == color):
                            output[r][c] = color

        if has_diff_runs:
            for total in target_sums:
                for r in range(rows):
                    c = total - r
                    if 0 <= c < cols:
                        original = grid[r][c]
                        current = output[r][c]
                        if (original in background) and (current in background or current == color):
                            output[r][c] = color

    return output


p = solve_80a900e0
