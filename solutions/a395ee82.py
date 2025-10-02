"""Solver for ARC-AGI-2 task a395ee82 (evaluation split)."""

from collections import Counter


def _extract_components(grid, background):
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    components = []
    for r in range(rows):
        for c in range(cols):
            if visited[r][c] or grid[r][c] == background:
                visited[r][c] = True
                continue
            color = grid[r][c]
            stack = [(r, c)]
            comp = []
            visited[r][c] = True
            while stack:
                x, y = stack.pop()
                comp.append((x, y))
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < rows and 0 <= ny < cols and not visited[nx][ny] and grid[nx][ny] == color:
                        visited[nx][ny] = True
                        stack.append((nx, ny))
            components.append((color, comp))
    return components


def solve_a395ee82(grid):
    """Reconstruct the patterned grid by replicating the template component."""
    rows, cols = len(grid), len(grid[0])
    background = grid[0][0]
    components = _extract_components(grid, background)

    multi = [(color, comp) for color, comp in components if len(comp) > 1]
    if not multi:
        return [row[:] for row in grid]

    template_color, template_comp = max(multi, key=lambda item: len(item[1]))
    t_rows = [r for r, _ in template_comp]
    t_cols = [c for _, c in template_comp]
    t_min_r, t_max_r = min(t_rows), max(t_rows)
    t_min_c, t_max_c = min(t_cols), max(t_cols)
    template_height = t_max_r - t_min_r + 1
    template_width = t_max_c - t_min_c + 1

    template = [[background] * template_width for _ in range(template_height)]
    for r, c in template_comp:
        template[r - t_min_r][c - t_min_c] = template_color

    singletons = [(color, comp[0]) for color, comp in components if len(comp) == 1]
    if not singletons:
        return [row[:] for row in grid]

    singleton_rows = sorted({r for _, (r, _) in singletons})
    singleton_cols = sorted({c for _, (_, c) in singletons})
    row_step = min((b - a) for a, b in zip(singleton_rows, singleton_rows[1:])) if len(singleton_rows) > 1 else template_height
    col_step = min((b - a) for a, b in zip(singleton_cols, singleton_cols[1:])) if len(singleton_cols) > 1 else template_width
    min_row = singleton_rows[0]
    min_col = singleton_cols[0]

    origin_row = t_min_r - template_height
    origin_col = t_min_c - template_width

    output = [[background] * cols for _ in range(rows)]
    singleton_colors = [color for color, _ in singletons]
    alt_candidates = [color for color in singleton_colors if color != template_color]
    swap_color = Counter(alt_candidates).most_common(1)[0][0] if alt_candidates else template_color

    for color, (r, c) in singletons:
        block_row = (r - min_row) // row_step if row_step else 0
        block_col = (c - min_col) // col_step if col_step else 0
        start_r = origin_row + block_row * template_height
        start_c = origin_col + block_col * template_width
        fill_color = template_color if color != template_color else swap_color
        for dr in range(template_height):
            for dc in range(template_width):
                val = template[dr][dc]
                if val == template_color:
                    rr, cc = start_r + dr, start_c + dc
                    if 0 <= rr < rows and 0 <= cc < cols:
                        output[rr][cc] = fill_color
                elif val != background:
                    rr, cc = start_r + dr, start_c + dc
                    if 0 <= rr < rows and 0 <= cc < cols:
                        output[rr][cc] = val

    return output


p = solve_a395ee82
