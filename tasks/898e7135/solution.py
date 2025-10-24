"""Solver for ARC-AGI-2 task 898e7135 (evaluation split)."""

from collections import Counter, defaultdict, deque
from math import gcd, sqrt
from typing import Dict, List, Optional, Sequence, Tuple

Grid = List[List[int]]
Coord = Tuple[int, int]


def _dominant_color(grid: Grid) -> int:
    """Return the most common nonzero color as the background color."""
    freq = Counter(val for row in grid for val in row if val != 0)
    return max(freq, key=lambda k: freq[k])


def _bbox_of_color(grid: Grid, color: int) -> Tuple[int, int, int, int]:
    rows, cols = zip(*[(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == color])
    return min(rows), max(rows), min(cols), max(cols)


def _zero_components_within_bbox(grid: Grid, bbox: Tuple[int, int, int, int]) -> List[List[Coord]]:
    """Find 4-connected zero components restricted to the given bounding box."""
    r0, r1, c0, c1 = bbox
    h, w = r1 - r0 + 1, c1 - c0 + 1
    seen = [[False] * w for _ in range(h)]
    comps: List[List[Coord]] = []
    for rr in range(h):
        for cc in range(w):
            if seen[rr][cc] or grid[r0 + rr][c0 + cc] != 0:
                continue
            queue = deque([(rr, cc)])
            seen[rr][cc] = True
            cells: List[Coord] = []
            while queue:
                cr, cc2 = queue.popleft()
                cells.append((r0 + cr, c0 + cc2))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc2 + dc
                    if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc] and grid[r0 + nr][c0 + nc] == 0:
                        seen[nr][nc] = True
                        queue.append((nr, nc))
            comps.append(cells)
    return comps


def _color_components(grid: Grid, skip_color: int) -> List[Tuple[int, List[Coord]]]:
    """Return 4-connected components for all colors except the skip_color."""
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    comps: List[Tuple[int, List[Coord]]] = []
    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            if val == 0 or val == skip_color or seen[r][c]:
                continue
            queue = deque([(r, c)])
            seen[r][c] = True
            cells: List[Coord] = []
            while queue:
                cr, cc = queue.popleft()
                cells.append((cr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc] and grid[nr][nc] == val:
                        seen[nr][nc] = True
                        queue.append((nr, nc))
            comps.append((val, cells))
    return comps


def _scale_grid(coarse: Grid, factor: int) -> Grid:
    """Upscale a coarse grid by the given factor via nearest-neighbour copy."""
    h, w = len(coarse), len(coarse[0])
    upscaled = [[0] * (w * factor) for _ in range(h * factor)]
    for r in range(h):
        for c in range(w):
            val = coarse[r][c]
            for dr in range(factor):
                row = factor * r + dr
                row_slice = upscaled[row]
                base = factor * c
                for dc in range(factor):
                    row_slice[base + dc] = val
    return upscaled


def solve_898e7135(grid: Grid) -> Grid:
    components = extractComponents(grid)
    scale = inferScaleFactor(components)
    upscaled = [expandComponent(component, scale) for component in components]
    return composeUpscaledGrid(upscaled)


p = solve_898e7135


# === DSL-friendly helper wrappers (pure, no side effects) ===

ComponentData = Dict[str, Grid]


def extractComponents(grid: Grid) -> List[ComponentData]:
    # Represent components abstractly by carrying the original grid once.
    return [{"grid": grid}]


def inferScaleFactor(components: List[ComponentData]) -> int:
    grid = components[0]["grid"]
    return _infer_scale_from_grid(grid)


def expandComponent(component: ComponentData, scale: int) -> Grid:
    grid = component["grid"]
    return _solve_with_scale(grid, forced_scale=scale)


def composeUpscaledGrid(upscaled: List[Grid]) -> Grid:
    return upscaled[0]


# === Original logic, factored as pure helpers ===

def _infer_scale_from_grid(grid: Grid) -> int:
    bg = _dominant_color(grid)
    color_comps = _color_components(grid, bg)
    significant = [cells for _, cells in color_comps if len(cells) >= 4]
    scale_sq = 0
    for cells in significant:
        area = len(cells)
        scale_sq = area if scale_sq == 0 else gcd(scale_sq, area)
    if scale_sq <= 0:
        scale_sq = 1
    scale = max(1, int(round(sqrt(scale_sq))))
    if scale * scale != scale_sq:
        scale_sq = scale * scale
        scale = int(round(sqrt(scale_sq)))
    return scale


def _solve_with_scale(grid: Grid, forced_scale: Optional[int] = None) -> Grid:
    bg = _dominant_color(grid)
    r0, r1, c0, c1 = _bbox_of_color(grid, bg)
    h, w = r1 - r0 + 1, c1 - c0 + 1

    coarse = [[grid[r0 + r][c0 + c] for c in range(w)] for r in range(h)]

    zero_comps = _zero_components_within_bbox(grid, (r0, r1, c0, c1))
    color_comps = _color_components(grid, bg)

    significant = [(color, cells) for color, cells in color_comps if len(cells) >= 4]

    if forced_scale is not None:
        scale = max(1, forced_scale)
        scale_sq = scale * scale
    else:
        scale_sq = 0
        for _, cells in significant:
            area = len(cells)
            scale_sq = area if scale_sq == 0 else gcd(scale_sq, area)
        if scale_sq <= 0:
            scale_sq = 1
        scale = max(1, int(round(sqrt(scale_sq))))
        if scale * scale != scale_sq:
            scale_sq = scale * scale

    if not zero_comps:
        return _scale_grid(coarse, scale)

    zeros_by_size: Dict[int, List[Tuple[Tuple[float, float], List[Coord]]]] = defaultdict(list)
    for cells in zero_comps:
        zr = sum(r for r, _ in cells) / len(cells)
        zc = sum(c for _, c in cells) / len(cells)
        zeros_by_size[len(cells)].append(((zr, zc), cells))

    colors_by_size: Dict[int, List[Tuple[int, Tuple[float, float]]]] = defaultdict(list)
    for color, cells in significant:
        area = len(cells)
        if area % (scale * scale) != 0:
            continue
        coarse_cells = area // (scale * scale)
        if coarse_cells <= 0:
            continue
        cr = sum(r for r, _ in cells) / area
        cc = sum(c for _, c in cells) / area
        colors_by_size[coarse_cells].append((color, (cr, cc)))

    for size, z_entries in zeros_by_size.items():
        palette = colors_by_size.get(size)
        if not palette:
            continue
        used = [False] * len(palette)
        for centroid, cells in z_entries:
            zr, zc = centroid
            best_idx = None
            best_dist = float("inf")
            for idx, (color, (cr, cc)) in enumerate(palette):
                if used[idx]:
                    continue
                dist = (zr - cr) ** 2 + (zc - cc) ** 2
                if dist < best_dist:
                    best_dist = dist
                    best_idx = idx
            if best_idx is None:
                continue
            used[best_idx] = True
            color = palette[best_idx][0]
            for r, c in cells:
                coarse[r - r0][c - c0] = color

    return _scale_grid(coarse, scale)
