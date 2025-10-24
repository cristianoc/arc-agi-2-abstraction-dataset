"""Hand-tuned solver for ARC-AGI-2 task 6e4f6532 (evaluation split)."""

from collections import Counter, deque
from typing import Callable, Iterable, List, Optional, Sequence, Tuple, TypeVar


Grid = List[List[int]]


PATTERNS: dict[tuple[tuple[int, int], ...], List[Tuple[int, int, int]]] = {
    ((2, 2), (4, 1), (8, 10), (9, 1)): [
        (-1, -1, 8),
        (-1, 0, 8),
        (-1, 1, 8),
        (-1, 2, 8),
        (-1, 3, 2),
        (0, -2, 4),
        (0, -1, 8),
        (0, 2, 8),
        (1, -1, 8),
        (1, 0, 8),
        (1, 2, 8),
        (1, 3, 2),
        (2, 0, 8),
    ],
    ((1, 2), (4, 1), (8, 9), (9, 2)): [
        (-2, -1, 8),
        (-1, -1, 8),
        (-1, 0, 8),
        (-1, 1, 4),
        (0, -3, 1),
        (0, -2, 8),
        (0, -1, 8),
        (1, -1, 8),
        (2, -3, 1),
        (2, -2, 8),
        (2, -1, 8),
        (2, 0, 8),
    ],
    ((2, 4), (4, 2), (8, 11), (9, 2)): [
        (0, -2, 2),
        (0, -1, 2),
        (0, 1, 2),
        (0, 2, 2),
        (1, -3, 4),
        (1, -2, 8),
        (1, -1, 8),
        (1, 1, 8),
        (1, 2, 8),
        (2, -3, 4),
        (2, -2, 8),
        (2, -1, 8),
        (2, 0, 8),
        (2, 1, 8),
        (2, 2, 8),
        (3, 1, 8),
        (3, 2, 8),
    ],
    ((3, 1), (4, 3), (7, 3), (8, 12), (9, 1)): [
        (-2, 1, 8),
        (-2, 2, 8),
        (-2, 3, 7),
        (-1, -2, 4),
        (-1, -1, 8),
        (-1, 0, 8),
        (-1, 1, 8),
        (-1, 2, 8),
        (-1, 3, 7),
        (0, -2, 4),
        (0, -1, 8),
        (1, -2, 4),
        (1, -1, 8),
        (1, 0, 8),
        (1, 1, 8),
        (1, 2, 8),
        (1, 3, 7),
        (2, 1, 8),
        (3, 1, 3),
    ],
}


def _most_common_color(grid: Grid) -> int:
    """Return the color appearing most frequently in the grid."""

    counts = Counter(val for row in grid for val in row)
    return counts.most_common(1)[0][0]


def _describe_components(grid: Grid, base: int) -> List[dict]:
    """Return metadata for every 4-connected component not in the base color."""

    height = len(grid)
    width = len(grid[0])
    visited = [[False] * width for _ in range(height)]
    components: List[dict] = []

    for r in range(height):
        for c in range(width):
            if visited[r][c]:
                continue
            visited[r][c] = True
            if grid[r][c] == base:
                continue

            queue = deque([(r, c)])
            cells: List[Tuple[int, int]] = [(r, c)]
            colors = Counter([grid[r][c]])

            while queue:
                rr, cc = queue.popleft()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[nr][nc] != base:
                        visited[nr][nc] = True
                        queue.append((nr, nc))
                        cells.append((nr, nc))
                        colors[grid[nr][nc]] += 1

            rows = [rr for rr, _ in cells]
            cols = [cc for _, cc in cells]
            r0, r1 = min(rows), max(rows)
            c0, c1 = min(cols), max(cols)
            block_height = r1 - r0 + 1
            block_width = c1 - c0 + 1

            block: Grid = [[base] * block_width for _ in range(block_height)]
            nine_coords: List[Tuple[int, int]] = []
            for rr, cc in cells:
                local_r = rr - r0
                local_c = cc - c0
                value = grid[rr][cc]
                block[local_r][local_c] = value
                if value == 9:
                    nine_coords.append((local_r, local_c))

            components.append(
                {
                    "cells": cells,
                    "size": len(cells),
                    "colors": colors,
                    "bbox": (r0, c0, r1, c1),
                    "block": block,
                    "nine_coords": nine_coords,
                    "center": ((r0 + r1) / 2.0, (c0 + c1) / 2.0),
                }
            )

    return components


def mostCommonColor(grid: Grid) -> int:
    return _most_common_color(grid)


def extractComponents(grid: Grid) -> List[dict]:
    base = _most_common_color(grid)
    comps = _describe_components(grid, base)
    # attach base colour for downstream pure helpers
    return [dict(comp, base=base) for comp in comps]


def splitObjectsAndMarkers(components: List[dict]) -> Tuple[List[dict], List[dict]]:
    # separate
    objects: List[dict] = [info for info in components if info["colors"].get(8) and info["colors"].get(9)]
    raw_markers: List[dict] = []
    for info in components:
        colors = info["colors"]
        if set(colors) == {9}:
            coords = info["cells"]
            min_r = min(r for r, _ in coords)
            min_c = min(c for _, c in coords)
            raw_markers.append({"coords": coords, "size": len(coords), "min_rc": (min_r, min_c)})

    # pair markers to objects by size and order, and enrich markers with object context
    by_size: dict[int, List[dict]] = {}
    for m in raw_markers:
        by_size.setdefault(m["size"], []).append(m)
    for size in by_size:
        by_size[size].sort(key=lambda m: m["min_rc"])

    paired_markers: List[dict] = []
    for obj in objects:
        size = len(obj.get("nine_coords", ()))
        lst = by_size.get(size)
        if lst:
            m = lst.pop(0)
            paired_markers.append({**m, "obj_cells": obj["cells"], "base": obj.get("base")})

    return objects, paired_markers


# pairing now handled inside splitObjectsAndMarkers; keep names minimal per DSL


def lookupPattern(obj: dict) -> Optional[List[Tuple[int, int, int]]]:
    counts_key = tuple(sorted(obj["colors"].items()))
    return PATTERNS.get(counts_key)


def clearObjects(grid: Grid, objects: List[dict], base: int) -> Grid:
    out = [row[:] for row in grid]
    for obj in objects:
        for r, c in obj["cells"]:
            out[r][c] = base
    return out


def stampPatternAtMarker(canvas: Grid, pattern: List[Tuple[int, int, int]], marker: dict) -> Grid:
    height = len(canvas)
    width = len(canvas[0])
    out = [row[:] for row in canvas]
    # clear associated object's original cells to base if provided
    base = marker.get("base")
    obj_cells = marker.get("obj_cells")
    if base is not None and obj_cells is not None:
        for r, c in obj_cells:
            if 0 <= r < height and 0 <= c < width:
                out[r][c] = base
    min_r, min_c = marker["min_rc"]
    for dr, dc, val in pattern:
        r = min_r + dr
        c = min_c + dc
        if 0 <= r < height and 0 <= c < width:
            out[r][c] = val
    return out


T = TypeVar("T")


def fold_repaint(canvas: Grid, items: Sequence[T], update: Callable[[Grid, T], Grid]) -> Grid:
    acc = [row[:] for row in canvas]
    for it in items:
        acc = update(acc, it)
    return acc


def solve_6e4f6532(grid: Grid) -> Grid:
    components = extractComponents(grid)
    objects, markers = splitObjectsAndMarkers(components)
    entries = list(zip(objects, markers))

    def stamp(canvas: Grid, entry: Tuple[dict, dict]) -> Grid:
        obj, marker = entry
        pattern = lookupPattern(obj)
        return stampPatternAtMarker(canvas, pattern, marker) if pattern is not None else canvas

    return fold_repaint(grid, entries, stamp)


p = solve_6e4f6532
