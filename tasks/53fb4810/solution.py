"""Solver for ARC-AGI-2 task 53fb4810."""


def _copy_grid(grid):
    return [row[:] for row in grid]


def _find_mixed_24_components(grid):
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    targets = {2, 4}
    components = []

    for r in range(h):
        for c in range(w):
            if grid[r][c] in targets and not seen[r][c]:
                stack = [(r, c)]
                seen[r][c] = True
                cells = []
                colors = set()

                while stack:
                    rr, cc = stack.pop()
                    color = grid[rr][cc]
                    cells.append((rr, cc, color))
                    colors.add(color)

                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = rr + dr, cc + dc
                        if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc]:
                            if grid[nr][nc] in targets:
                                seen[nr][nc] = True
                                stack.append((nr, nc))

                if colors == targets:
                    components.append(cells)

    return components


def solve_53fb4810(grid):
    result = _copy_grid(grid)
    components = _find_mixed_24_components(grid)

    for comp in components:
        rows = [r for r, _, _ in comp]
        cols = [c for _, c, _ in comp]
        row_min, row_max = min(rows), max(rows)
        col_min, col_max = min(cols), max(cols)

        height = row_max - row_min + 1
        pattern_rows = [[] for _ in range(height)]
        for r, c, color in comp:
            pattern_rows[r - row_min].append((c - col_min, color))

        for r in range(row_min - 1, -1, -1):
            pattern_idx = (r - row_min) % height
            for dc, color in pattern_rows[pattern_idx]:
                result[r][col_min + dc] = color

    return result


p = solve_53fb4810
