"""Solver for ARC-AGI-2 task 9385bd28 (split: evaluation)."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from typing import Dict, Iterable, List, Sequence, Tuple, TypedDict


Grid = List[List[int]]
Coord = Tuple[int, int]
BBox = Tuple[int, int, int, int]
Boxes = Dict[int, BBox]


class LegendPairs(TypedDict):
    zero_pairs: List[Tuple[int, int]]
    fill_pairs: List[Tuple[int, int]]
    legend_sources: Sequence[int]
    background: int
    legend_row_start: int
    legend_cols: int


def _extract_components(grid: Grid) -> Tuple[Dict[int, List[List[Coord]]], Dict[Coord, Tuple[int, int]]]:
    """Return connected components per color and a lookup by cell."""
    height, width = len(grid), len(grid[0])
    coords_by_color: Dict[int, List[Coord]] = defaultdict(list)
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val:
                coords_by_color[val].append((r, c))

    comps_by_color: Dict[int, List[List[Coord]]] = {}
    comp_lookup: Dict[Coord, Tuple[int, int]] = {}
    for color, coords in coords_by_color.items():
        visited = set()
        comps: List[List[Coord]] = []
        for coord in coords:
            if coord in visited:
                continue
            queue = deque([coord])
            visited.add(coord)
            comp: List[Coord] = []
            while queue:
                r, c = queue.popleft()
                comp.append((r, c))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < height and 0 <= nc < width and grid[nr][nc] == color and (nr, nc) not in visited):
                        visited.add((nr, nc))
                        queue.append((nr, nc))
            comp_index = len(comps)
            for cell in comp:
                comp_lookup[cell] = (color, comp_index)
            comps.append(comp)
        comps_by_color[color] = comps
    return comps_by_color, comp_lookup


def extractLegendPairs(grid: Grid) -> LegendPairs:
    """Read legend rows/cols to identify zero and fill pairs and related metadata."""
    height, width = len(grid), len(grid[0])
    legend_rows = min(5, height)
    legend_cols = min(4, width)
    legend_row_start = max(0, height - legend_rows)
    background = Counter(cell for row in grid for cell in row).most_common(1)[0][0]

    comps_by_color, comp_lookup = _extract_components(grid)

    zero_pairs: List[Tuple[int, int]] = []
    fill_pairs: List[Tuple[int, int]] = []
    seen_pairs = set()
    max_c = max(0, legend_cols - 1)
    for r in range(legend_row_start, height):
        for c in range(max_c):
            left = grid[r][c]
            right = grid[r][c + 1]
            if left == 0:
                continue
            if right == 0 and background == 0:
                continue
            if right == background:
                continue
            lookup = comp_lookup.get((r, c))
            if lookup is None:
                continue
            color, comp_idx = lookup
            comp = comps_by_color[color][comp_idx]
            if not all(legend_row_start <= rr and cc < legend_cols for rr, cc in comp):
                continue
            pair = (left, right)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            if right == 0:
                zero_pairs.append(pair)
            else:
                fill_pairs.append(pair)

    legend_sources = tuple({source for source, _ in zero_pairs + fill_pairs if source != 0})

    return LegendPairs(
        zero_pairs=zero_pairs,
        fill_pairs=fill_pairs,
        legend_sources=legend_sources,
        background=background,
        legend_row_start=legend_row_start,
        legend_cols=legend_cols,
    )


def computeBoundingBoxes(grid: Grid) -> Boxes:
    """Compute bboxes of non-legend components for each color."""
    height, width = len(grid), len(grid[0])
    legend_rows = min(5, height)
    legend_cols = min(4, width)
    legend_row_start = max(0, height - legend_rows)

    comps_by_color, _ = _extract_components(grid)
    bbox_by_color: Boxes = {}
    for color, comps in comps_by_color.items():
        cells = [cell for comp in comps if not all(legend_row_start <= r and c < legend_cols for r, c in comp) for cell in comp]
        if not cells:
            continue
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        bbox_by_color[color] = (min(rows), max(rows), min(cols), max(cols))
    return bbox_by_color


def clearZeroPairs(grid: Grid, legend_pairs: LegendPairs, boxes: Boxes) -> Grid:
    """Clear interior of boxes whose source color maps to zero."""
    result = [row[:] for row in grid]
    for source, _ in legend_pairs["zero_pairs"]:
        bbox = boxes.get(source)
        if not bbox:
            continue
        r0, r1, c0, c1 = bbox
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if result[r][c] == source:
                    result[r][c] = 0
    return result


def fillBoxes(grid: Grid, legend_pairs: LegendPairs, boxes: Boxes) -> Grid:
    """Recolour each remaining box according to target while respecting protection and purity rules."""
    background = legend_pairs["background"]
    protected_boxes = [bbox for color, bbox in boxes.items() if color not in legend_pairs["legend_sources"] and color != background]

    result = [row[:] for row in grid]

    for source, target in legend_pairs["fill_pairs"]:
        bbox = boxes.get(source)
        if not bbox:
            continue
        r0, r1, c0, c1 = bbox
        # Recolor entire if box contains no background or zeros in original grid
        recolor_entire = True
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if grid[r][c] in (0, background):
                    recolor_entire = False
                    break
            if not recolor_entire:
                break

        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if result[r][c] == source:
                    if recolor_entire:
                        result[r][c] = target
                    continue
                skip = False
                for pr0, pr1, pc0, pc1 in protected_boxes:
                    if pr0 <= r <= pr1 and pc0 <= c <= pc1:
                        skip = True
                        break
                if skip:
                    continue
                if result[r][c] in (0, background):
                    result[r][c] = target
    return result


def solve_9385bd28(grid: Grid) -> Grid:
    legend_pairs = extractLegendPairs(grid)
    boxes = computeBoundingBoxes(grid)
    cleared = clearZeroPairs(grid, legend_pairs, boxes)
    return fillBoxes(cleared, legend_pairs, boxes)


p = solve_9385bd28
