"""Solver for ARC-AGI-2 task a395ee82 (evaluation split)."""

from collections import Counter
from typing import List, Tuple, Dict, Optional, TypedDict


Grid = List[List[int]]


class Template(TypedDict):
    rows: int
    cols: int
    background: int
    mask: Grid
    height: int
    width: int
    origin_row: int
    origin_col: int


class Markers(TypedDict):
    markers: List[Tuple[int, int, int]]


class Lattice(TypedDict):
    markers: List[Tuple[int, int, int]]
    row_step: Optional[int]
    col_step: Optional[int]
    min_row: int
    min_col: int


def _extract_components(grid: Grid, background: int) -> List[Tuple[int, List[Tuple[int, int]]]]:
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    components: List[Tuple[int, List[Tuple[int, int]]]] = []
    for r in range(rows):
        for c in range(cols):
            if visited[r][c] or grid[r][c] == background:
                visited[r][c] = True
                continue
            color = grid[r][c]
            stack = [(r, c)]
            comp: List[Tuple[int, int]] = []
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


# === DSL helpers (pure, no side effects) ===

def extractTemplate(grid: Grid) -> Tuple[Template, int]:
    rows, cols = len(grid), len(grid[0])
    background = grid[0][0]
    components = _extract_components(grid, background)

    multi = [(color, comp) for color, comp in components if len(comp) > 1]
    if not multi:
        # No template; return a passthrough template wrapper
        empty_template: Grid = []
        return (Template(
            rows=rows,
            cols=cols,
            background=background,
            mask=empty_template,
            height=0,
            width=0,
            origin_row=0,
            origin_col=0,
        ), background)

    template_color, template_comp = max(multi, key=lambda item: len(item[1]))
    t_rows = [r for r, _ in template_comp]
    t_cols = [c for _, c in template_comp]
    t_min_r, t_max_r = min(t_rows), max(t_rows)
    t_min_c, t_max_c = min(t_cols), max(t_cols)
    template_height = t_max_r - t_min_r + 1
    template_width = t_max_c - t_min_c + 1

    mask: Grid = [[background] * template_width for _ in range(template_height)]
    for r, c in template_comp:
        mask[r - t_min_r][c - t_min_c] = template_color

    origin_row = t_min_r - template_height
    origin_col = t_min_c - template_width

    tpl = Template(
        rows=rows,
        cols=cols,
        background=background,
        mask=mask,
        height=template_height,
        width=template_width,
        origin_row=origin_row,
        origin_col=origin_col,
    )
    return tpl, template_color


def collectMarkers(grid: Grid) -> Markers:
    background = grid[0][0]
    components = _extract_components(grid, background)
    singletons: List[Tuple[int, int, int]] = [
        (color, comp[0][0], comp[0][1]) for color, comp in components if len(comp) == 1
    ]
    return Markers(markers=singletons)


def computeLattice(markers: Markers) -> Lattice:
    singles = markers["markers"]
    if not singles:
        return Lattice(markers=[], row_step=None, col_step=None, min_row=0, min_col=0)
    rows = sorted({r for _, r, _ in singles})
    cols = sorted({c for _, _, c in singles})
    min_row = rows[0]
    min_col = cols[0]
    row_step_opt: Optional[int] = min((b - a) for a, b in zip(rows, rows[1:])) if len(rows) > 1 else None
    col_step_opt: Optional[int] = min((b - a) for a, b in zip(cols, cols[1:])) if len(cols) > 1 else None
    return Lattice(
        markers=singles,
        row_step=row_step_opt,
        col_step=col_step_opt,
        min_row=min_row,
        min_col=min_col,
    )


def tileTemplate(template: Template, lattice: Lattice) -> Grid:
    rows = template["rows"]
    cols = template["cols"]
    background = template["background"]
    mask = template["mask"]
    template_height = template["height"]
    template_width = template["width"]
    origin_row = template["origin_row"]
    origin_col = template["origin_col"]

    singles = lattice["markers"]
    if template_height == 0 or not singles:
        # No template or no markers: passthrough
        return [[background] * cols for _ in range(rows)]

    # Derive the template colour from the mask (any non-background entry)
    template_color: Optional[int] = None
    for dr in range(template_height):
        for dc in range(template_width):
            if mask[dr][dc] != background:
                template_color = mask[dr][dc]
                break
        if template_color is not None:
            break
    if template_color is None:
        return [[background] * cols for _ in range(rows)]

    # Determine colour swap for markers matching the template colour
    singleton_colors = [color for color, _, _ in singles]
    alt_candidates = [color for color in singleton_colors if color != template_color]
    swap_color = Counter(alt_candidates).most_common(1)[0][0] if alt_candidates else template_color

    row_step_opt = lattice["row_step"]
    col_step_opt = lattice["col_step"]
    min_row = lattice["min_row"]
    min_col = lattice["min_col"]
    row_step = row_step_opt if row_step_opt is not None else template_height
    col_step = col_step_opt if col_step_opt is not None else template_width

    output = [[background] * cols for _ in range(rows)]
    for color, r, c in singles:
        block_row = (r - min_row) // row_step if row_step else 0
        block_col = (c - min_col) // col_step if col_step else 0
        start_r = origin_row + block_row * template_height
        start_c = origin_col + block_col * template_width
        fill_color = template_color if color != template_color else swap_color
        for dr in range(template_height):
            rr = start_r + dr
            if rr < 0 or rr >= rows:
                continue
            for dc in range(template_width):
                cc = start_c + dc
                if cc < 0 or cc >= cols:
                    continue
                val = mask[dr][dc]
                if val == template_color:
                    output[rr][cc] = fill_color
                elif val != background:
                    output[rr][cc] = val

    return output


def solve_a395ee82(grid: Grid) -> Grid:
    template, template_colour = extractTemplate(grid)
    markers = collectMarkers(grid)
    lattice = computeLattice(markers)
    return tileTemplate(template, lattice)


p = solve_a395ee82
