"""Solver for ARC-AGI-2 task b10624e5 (split: evaluation)."""

from collections import Counter


def _clone_grid(grid):
    return [row[:] for row in grid]


def _find_center_cross(grid):
    """Locate the dominant row and column of ones that form the cross."""
    height = len(grid)
    width = len(grid[0]) if grid else 0
    center_row = max(range(height), key=lambda r: sum(1 for v in grid[r] if v == 1))
    center_col = max(range(width), key=lambda c: sum(1 for r in range(height) if grid[r][c] == 1))
    return center_row, center_col


def _get_components(grid, value):
    """Return a list of connected components (4-neighbour) for a given value."""
    height = len(grid)
    width = len(grid[0]) if grid else 0
    visited = set()
    components = []

    for r in range(height):
        for c in range(width):
            if grid[r][c] != value or (r, c) in visited:
                continue
            stack = [(r, c)]
            visited.add((r, c))
            comp = []
            while stack:
                cr, cc = stack.pop()
                comp.append((cr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and grid[nr][nc] == value and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        stack.append((nr, nc))
            components.append(comp)

    return components


def solve_b10624e5(grid):
    """Replicate the ornamentation around each block of twos based on the observed template."""
    if not grid:
        return []

    height = len(grid)
    width = len(grid[0])
    center_row, center_col = _find_center_cross(grid)
    components = _get_components(grid, value=2)
    if not components:
        return _clone_grid(grid)

    result = _clone_grid(grid)

    inner_horizontal_candidates = []
    outer_horizontal_candidates = []
    vertical_outer_candidates = []
    vertical_inner_candidates = []
    comp_infos = []

    for comp in components:
        rows = [r for r, _ in comp]
        cols = [c for _, c in comp]
        minr, maxr = min(rows), max(rows)
        minc, maxc = min(cols), max(cols)
        comp_height = maxr - minr + 1
        comp_width = maxc - minc + 1
        avg_row = sum(rows) / len(rows)
        avg_col = sum(cols) / len(cols)
        side = "left" if avg_col < center_col else "right"
        vert_pos = "top" if avg_row < center_row else "bottom"

        info = {
            "minr": minr,
            "maxr": maxr,
            "minc": minc,
            "maxc": maxc,
            "height": comp_height,
            "width": comp_width,
            "side": side,
            "vert": vert_pos,
        }
        comp_infos.append(info)

        # Gather horizontal template colours (one cell away from the component).
        inner_col = maxc + 1 if side == "left" else minc - 1
        if 0 <= inner_col < width:
            for r in range(minr, maxr + 1):
                val = grid[r][inner_col]
                if val != 4:
                    inner_horizontal_candidates.append(val)

        outer_col = minc - 1 if side == "left" else maxc + 1
        if 0 <= outer_col < width:
            for r in range(minr, maxr + 1):
                val = grid[r][outer_col]
                if val != 4:
                    outer_horizontal_candidates.append(val)

        # Prepare column grouping relative to the centre for vertical templates.
        comp_columns = list(range(minc, maxc + 1))
        column_dist = {c: abs(c - center_col) for c in comp_columns}
        sorted_cols = sorted(comp_columns, key=lambda c: column_dist[c])
        inner_count = len(comp_columns) // 2
        inner_cols = set(sorted_cols[:inner_count])
        outer_cols = set(comp_columns) - inner_cols

        outer_row = minr - 1 if vert_pos == "top" else maxr + 1
        if 0 <= outer_row < height:
            for c in outer_cols:
                val = grid[outer_row][c]
                if val != 4:
                    vertical_outer_candidates.append(val)
            for c in inner_cols:
                val = grid[outer_row][c]
                if val != 4:
                    vertical_inner_candidates.append(val)

        info["columns"] = comp_columns
        info["column_dist"] = column_dist

    def choose_color(values):
        return Counter(values).most_common(1)[0][0] if values else None

    inner_horizontal_color = choose_color(inner_horizontal_candidates)
    outer_horizontal_color = choose_color(outer_horizontal_candidates)
    vertical_outer_color = choose_color(vertical_outer_candidates)
    vertical_inner_color = choose_color(vertical_inner_candidates)
    if vertical_inner_color == vertical_outer_color:
        vertical_inner_color = None

    for info in comp_infos:
        minr = info["minr"]
        maxr = info["maxr"]
        minc = info["minc"]
        maxc = info["maxc"]
        comp_height = info["height"]
        columns = info["columns"]
        column_dist = info["column_dist"]
        side = info["side"]
        vert_pos = info["vert"]

        # Horizontal expansions (towards and away from the centre column).
        inner_thickness = comp_height if inner_horizontal_color is not None else 0
        outer_thickness = (comp_height // 2) if outer_horizontal_color is not None else 0

        if inner_thickness:
            if side == "left":
                for offset in range(1, inner_thickness + 1):
                    col = maxc + offset
                    if col >= width:
                        break
                    for row in range(minr, maxr + 1):
                        if result[row][col] == 4:
                            result[row][col] = inner_horizontal_color
            else:  # right side component, fill to the left
                for offset in range(1, inner_thickness + 1):
                    col = minc - offset
                    if col < 0:
                        break
                    for row in range(minr, maxr + 1):
                        if result[row][col] == 4:
                            result[row][col] = inner_horizontal_color

        if outer_thickness:
            if side == "left":
                for offset in range(1, outer_thickness + 1):
                    col = minc - offset
                    if col < 0:
                        break
                    for row in range(minr, maxr + 1):
                        if result[row][col] == 4:
                            result[row][col] = outer_horizontal_color
            else:
                for offset in range(1, outer_thickness + 1):
                    col = maxc + offset
                    if col >= width:
                        break
                    for row in range(minr, maxr + 1):
                        if result[row][col] == 4:
                            result[row][col] = outer_horizontal_color

        # Vertical expansions (away from the centre row).
        vertical_inner_thickness = comp_height if vertical_inner_color is not None else 0
        if vertical_inner_color is None:
            vertical_outer_thickness = comp_height if vertical_outer_color is not None else 0
        else:
            vertical_outer_thickness = (comp_height + 1) // 2 if vertical_outer_color is not None else 0

        if vertical_outer_thickness or vertical_inner_thickness:
            sorted_cols = sorted(columns, key=lambda c: column_dist[c])
            if vertical_inner_color is not None:
                inner_count = len(columns) // 2
                inner_cols = set(sorted_cols[:inner_count])
            else:
                inner_cols = set()
            outer_cols = set(columns) - inner_cols

            base_row = minr if vert_pos == "top" else maxr
            direction = -1 if vert_pos == "top" else 1

            def paint_column(col, color, thickness):
                if color is None or thickness <= 0:
                    return
                row = base_row
                for step in range(1, thickness + 1):
                    row += direction
                    if not (0 <= row < height):
                        break
                    if result[row][col] == 4:
                        result[row][col] = color

            for col in outer_cols:
                paint_column(col, vertical_outer_color, vertical_outer_thickness)
            for col in inner_cols:
                paint_column(col, vertical_inner_color, vertical_inner_thickness)

    return result


p = solve_b10624e5
