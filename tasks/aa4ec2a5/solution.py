"""ARC-AGI-2 task aa4ec2a5 – DSL-style solver with identical semantics."""

from collections import Counter
from typing import Callable, Dict, Iterable, List, Set, Tuple


Grid = List[List[int]]
Cell = Tuple[int, int]
# Component representation: (cells, rows_to_cols, bbox(row_min, row_max, col_min, col_max))
Component = Tuple[Set[Cell], Dict[int, List[int]], Tuple[int, int, int, int]]

DIRS: List[Cell] = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def background_color(grid: Grid) -> int:
    return Counter(val for row in grid for val in row).most_common(1)[0][0]


def in_bounds(h: int, w: int, r: int, c: int) -> bool:
    return 0 <= r < h and 0 <= c < w


def extractOneComponents(grid: Grid) -> List[Component]:
    h, w = len(grid), len(grid[0])
    visited: List[List[bool]] = [[False] * w for _ in range(h)]
    out: List[Component] = []

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 1 or visited[r][c]:
                continue
            stack: List[Cell] = [(r, c)]
            visited[r][c] = True
            cells: List[Cell] = []
            rows_to_cols: Dict[int, List[int]] = {}
            while stack:
                rr, cc = stack.pop()
                cells.append((rr, cc))
                rows_to_cols.setdefault(rr, []).append(cc)
                for dr, dc in DIRS:
                    nr, nc = rr + dr, cc + dc
                    if in_bounds(h, w, nr, nc) and grid[nr][nc] == 1 and not visited[nr][nc]:
                        visited[nr][nc] = True
                        stack.append((nr, nc))

            row_min = min(r0 for r0, _ in cells)
            row_max = max(r0 for r0, _ in cells)
            col_min = min(c0 for _, c0 in cells)
            col_max = max(c0 for _, c0 in cells)
            out.append((set(cells), rows_to_cols, (row_min, row_max, col_min, col_max)))

    return out


def findInteriorHoles(canvas: Grid, component: Component, _background_color: int) -> Tuple[bool, Set[Cell]]:
    # Note: compute the true background from the canvas; ignore the passed colour literal.
    bg = background_color(canvas)
    comp_cells, _rows_to_cols, (rmin, rmax, cmin, cmax) = component
    seen_bg: Set[Cell] = set()
    holes: Set[Cell] = set()

    for rr in range(rmin, rmax + 1):
        for cc in range(cmin, cmax + 1):
            if canvas[rr][cc] != bg or (rr, cc) in seen_bg:
                continue
            bucket: List[Cell] = [(rr, cc)]
            seen_bg.add((rr, cc))
            touches_edge = False
            pocket: List[Cell] = []
            while bucket:
                sr, sc = bucket.pop()
                pocket.append((sr, sc))
                if sr in (rmin, rmax) or sc in (cmin, cmax):
                    touches_edge = True
                for dr, dc in DIRS:
                    nr, nc = sr + dr, sc + dc
                    if rmin <= nr <= rmax and cmin <= nc <= cmax:
                        if canvas[nr][nc] == bg and (nr, nc) not in seen_bg:
                            seen_bg.add((nr, nc))
                            bucket.append((nr, nc))
            if not touches_edge:
                holes.update(pocket)

    return (bool(holes), holes)


def frameComponentRows(canvas: Grid, component: Component, hole_cells: Set[Cell]) -> Grid:
    h, w = len(canvas), len(canvas[0])
    bg = background_color(canvas)
    comp_cells, rows_to_cols, (rmin, rmax, cmin, cmax) = component
    result = [row[:] for row in canvas]

    # Immediate adjacency within bbox and mark holes (as skip only — holes get painted later).
    for rr in range(rmin, rmax + 1):
        for cc in range(cmin, cmax + 1):
            if canvas[rr][cc] != bg:
                continue
            if (rr, cc) in hole_cells:
                # leave for markComponentBody to paint 6
                continue
            if any(((rr + dr, cc + dc) in comp_cells) for dr, dc in DIRS):
                result[rr][cc] = 2

    # Segment-aware horizontal borders and vertical skirts.
    for rr, cols in rows_to_cols.items():
        cols_sorted = sorted(cols)
        segments: List[List[int]] = []
        for col in cols_sorted:
            if not segments or col > segments[-1][1] + 1:
                segments.append([col, col])
            else:
                segments[-1][1] = col

        for start, end in segments:
            # Left/right borders on the same row.
            for cc in (start - 1, end + 1):
                if 0 <= cc < w and canvas[rr][cc] == bg and (rr, cc) not in hole_cells:
                    result[rr][cc] = 2
            # Rows above/below spanning the horizontal extent plus margins.
            for adj in (rr - 1, rr + 1):
                if not (0 <= adj < h):
                    continue
                for cc in range(start - 1, end + 2):
                    if 0 <= cc < w and canvas[adj][cc] == bg and (adj, cc) not in hole_cells:
                        result[adj][cc] = 2

    return result


def markComponentBody(canvas: Grid, component: Component, has_hole: bool) -> Grid:
    comp_cells, _rows_to_cols, (_rmin, _rmax, _cmin, _cmax) = component
    result = [row[:] for row in canvas]
    # Paint component body.
    for rr, cc in comp_cells:
        result[rr][cc] = 8 if has_hole else 1
    # Also annotate hole cells when present.
    if has_hole:
        _flag, holes = findInteriorHoles(canvas, component, 0)
        for rr, cc in holes:
            result[rr][cc] = 6
    return result


# (no separate paintHoles; handled by markComponentBody)


def fold_repaint(canvas: Grid, items: Iterable[Component], update: Callable[[Grid, Component], Grid]) -> Grid:
    acc = canvas
    for item in items:
        acc = update(acc, item)
    return acc


def solve_aa4ec2a5(grid: Grid) -> Grid:
    components = extractOneComponents(grid)

    def repaint(canvas: Grid, component: Component) -> Grid:
        has_hole, hole_cells = findInteriorHoles(canvas, component, 0)
        framed = frameComponentRows(canvas, component, hole_cells)
        return markComponentBody(framed, component, has_hole)

    return fold_repaint(grid, components, repaint)


p = solve_aa4ec2a5
