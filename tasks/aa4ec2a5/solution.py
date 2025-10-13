"""Auto-generated identity stub for ARC-AGI-2 task aa4ec2a5 (split: evaluation)."""

from collections import Counter


DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def solve_aa4ec2a5(grid):
    """Solve the aa4ec2a5 task by annotating each 1-component's neighborhood."""
    height = len(grid)
    width = len(grid[0])
    background = Counter(val for row in grid for val in row).most_common(1)[0][0]
    result = [row[:] for row in grid]
    visited = [[False] * width for _ in range(height)]

    for r in range(height):
        for c in range(width):
            if grid[r][c] != 1 or visited[r][c]:
                continue

            stack = [(r, c)]
            visited[r][c] = True
            component = []
            rows_to_cols = {}

            while stack:
                rr, cc = stack.pop()
                component.append((rr, cc))
                rows_to_cols.setdefault(rr, []).append(cc)
                for dr, dc in DIRS:
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and grid[nr][nc] == 1 and not visited[nr][nc]:
                        visited[nr][nc] = True
                        stack.append((nr, nc))

            row_min = min(r0 for r0, _ in component)
            row_max = max(r0 for r0, _ in component)
            col_min = min(c0 for _, c0 in component)
            col_max = max(c0 for _, c0 in component)
            comp_cells = set(component)

            seen_background = set()
            hole_cells = set()
            for rr in range(row_min, row_max + 1):
                for cc in range(col_min, col_max + 1):
                    if grid[rr][cc] != background or (rr, cc) in seen_background:
                        continue
                    bucket = [(rr, cc)]
                    seen_background.add((rr, cc))
                    touches_edge = False
                    pocket = []
                    while bucket:
                        sr, sc = bucket.pop()
                        pocket.append((sr, sc))
                        if sr in (row_min, row_max) or sc in (col_min, col_max):
                            touches_edge = True
                        for dr, dc in DIRS:
                            nr, nc = sr + dr, sc + dc
                            if row_min <= nr <= row_max and col_min <= nc <= col_max:
                                if grid[nr][nc] == background and (nr, nc) not in seen_background:
                                    seen_background.add((nr, nc))
                                    bucket.append((nr, nc))
                    if not touches_edge:
                        hole_cells.update(pocket)

            has_hole = bool(hole_cells)
            for rr, cc in component:
                result[rr][cc] = 8 if has_hole else 1

            for rr in range(row_min, row_max + 1):
                for cc in range(col_min, col_max + 1):
                    if grid[rr][cc] != background:
                        continue
                    if (rr, cc) in hole_cells:
                        result[rr][cc] = 6
                        continue
                    if any((rr + dr, cc + dc) in comp_cells for dr, dc in DIRS):
                        result[rr][cc] = 2

            for rr, cols in rows_to_cols.items():
                cols_sorted = sorted(cols)
                segments = []
                for col in cols_sorted:
                    if not segments or col > segments[-1][1] + 1:
                        segments.append([col, col])
                    else:
                        segments[-1][1] = col

                for start, end in segments:
                    borders = (start - 1, end + 1)
                    for cc in borders:
                        if 0 <= cc < width and grid[rr][cc] == background and (rr, cc) not in hole_cells:
                            result[rr][cc] = 2
                    for adj in (rr - 1, rr + 1):
                        if not (0 <= adj < height):
                            continue
                        for cc in range(start - 1, end + 2):
                            if 0 <= cc < width and grid[adj][cc] == background and (adj, cc) not in hole_cells:
                                result[adj][cc] = 2

    return result


p = solve_aa4ec2a5
