"""Solver for ARC-AGI-2 task 4a21e3da (evaluation split)."""


def _component_cells(grid, color):
    return [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == color]


def _align_to_corner(cells, corner, height, width):
    if not cells:
        return set()
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)
    h_span = max_r - min_r + 1
    w_span = max_c - min_c + 1
    if corner == "top-left":
        dy, dx = -min_r, -min_c
    elif corner == "top-right":
        dy, dx = -min_r, (width - w_span) - min_c
    elif corner == "bottom-left":
        dy, dx = (height - h_span) - min_r, -min_c
    elif corner == "bottom-right":
        dy, dx = (height - h_span) - min_r, (width - w_span) - min_c
    else:  # pragma: no cover - defensive guard
        raise ValueError(corner)
    aligned = set()
    for r, c in cells:
        nr, nc = r + dy, c + dx
        if 0 <= nr < height and 0 <= nc < width:
            aligned.add((nr, nc))
    return aligned


def solve_4a21e3da(grid):
    height, width = len(grid), len(grid[0])
    sevens = _component_cells(grid, 7)
    twos = _component_cells(grid, 2)
    if not sevens:
        return [row[:] for row in grid]

    min_r = min(r for r, _ in sevens)
    max_r = max(r for r, _ in sevens)
    min_c = min(c for _, c in sevens)
    max_c = max(c for _, c in sevens)

    has_top = any(sr < min_r for sr, _ in twos)
    has_bottom = any(sr > max_r for sr, _ in twos)
    has_left = any(sc < min_c for _, sc in twos)
    has_right = any(sc > max_c for _, sc in twos)

    twos_to_paint = set()
    sevens_to_paint = set()

    for sr, sc in twos:
        twos_to_paint.add((sr, sc))
        if sr < min_r:  # top sentinel
            column_rows = [r for r, c in sevens if c == sc]
            stop_row = max(column_rows) if column_rows else max_r
            for r in range(sr, stop_row + 1):
                if grid[r][sc] != 7:
                    twos_to_paint.add((r, sc))
            left_cells = [(r, c) for r, c in sevens if c < sc]
            if has_right:
                distance = min_r - sr
                left_cells = [cell for cell in left_cells if cell[0] < min_r + distance]
            sevens_to_paint |= _align_to_corner(left_cells, "top-left", height, width)
            if not has_right:
                right_cells = [(r, c) for r, c in sevens if c > sc]
                sevens_to_paint |= _align_to_corner(right_cells, "top-right", height, width)
            sevens_to_paint |= {(r, c) for r, c in sevens if c == sc}
        elif sr > max_r:  # bottom sentinel
            column_rows = [r for r, c in sevens if c == sc]
            stop_row = min(column_rows) if column_rows else min_r
            for r in range(sr, stop_row - 1, -1):
                if grid[r][sc] != 7:
                    twos_to_paint.add((r, sc))
            left_cells = [(r, c) for r, c in sevens if c < sc]
            right_cells = [(r, c) for r, c in sevens if c > sc]
            sevens_to_paint |= _align_to_corner(left_cells, "bottom-left", height, width)
            sevens_to_paint |= _align_to_corner(right_cells, "bottom-right", height, width)
            sevens_to_paint |= {(r, c) for r, c in sevens if c == sc}
        elif sc < min_c:  # left sentinel
            row_cols = [c for r, c in sevens if r == sr]
            stop_col = max(row_cols) if row_cols else max_c
            for c in range(sc, stop_col + 1):
                if grid[sr][c] != 7:
                    twos_to_paint.add((sr, c))
            top_cells = [(r, c) for r, c in sevens if r < sr]
            bottom_cells = [(r, c) for r, c in sevens if r > sr]
            if not has_top:
                sevens_to_paint |= _align_to_corner(top_cells, "top-left", height, width)
            if not has_bottom:
                sevens_to_paint |= _align_to_corner(bottom_cells, "bottom-left", height, width)
            sevens_to_paint |= {(r, c) for r, c in sevens if r == sr}
        elif sc > max_c:  # right sentinel
            row_cols = [c for r, c in sevens if r == sr]
            stop_col = min(row_cols) if row_cols else min_c
            for c in range(sc, stop_col, -1):
                if grid[sr][c] != 7:
                    twos_to_paint.add((sr, c))
            distance = sc - max_c
            threshold = max_c - distance
            top_cells = [(r, c) for r, c in sevens if r < sr and c >= threshold]
            bottom_cells = [(r, c) for r, c in sevens if r > sr and c >= threshold]
            sevens_to_paint |= _align_to_corner(top_cells, "top-right", height, width)
            sevens_to_paint |= _align_to_corner(bottom_cells, "bottom-right", height, width)
            sevens_to_paint |= {(r, c) for r, c in sevens if r == sr}

    output = [[1 for _ in range(width)] for _ in range(height)]
    for r, c in twos_to_paint:
        output[r][c] = 2
    for r, c in sevens_to_paint:
        output[r][c] = 7
    return output


p = solve_4a21e3da
