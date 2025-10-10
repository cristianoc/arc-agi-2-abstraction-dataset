"""Solver for ARC-AGI-2 task 35ab12c3."""

from collections import defaultdict
from typing import Dict, Iterable, List, Sequence, Set, Tuple

Coord = Tuple[int, int]
Grid = List[List[int]]


def _line_points(a: Coord, b: Coord) -> List[Coord]:
    """Return grid coordinates along the straight segment between two points."""
    (r1, c1), (r2, c2) = a, b
    dr = r2 - r1
    dc = c2 - c1
    steps = max(abs(dr), abs(dc))
    if steps == 0:
        return [a]
    return [
        (
            r1 + int(round(dr * t / steps)),
            c1 + int(round(dc * t / steps)),
        )
        for t in range(steps + 1)
    ]


def _cross(o: Coord, a: Coord, b: Coord) -> int:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _convex_hull(points: Sequence[Coord]) -> List[Coord]:
    pts = sorted(set(points))
    if len(pts) <= 1:
        return list(pts)

    lower: List[Coord] = []
    for p in pts:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper: List[Coord] = []
    for p in reversed(pts):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def _build_base_shape(points: Sequence[Coord], grid: Grid) -> Set[Coord]:
    if not points:
        return set()
    if len(points) == 1:
        return {points[0]}

    edges: Set[Tuple[Coord, Coord]] = set()
    rows: Dict[int, List[Coord]] = defaultdict(list)
    cols: Dict[int, List[Coord]] = defaultdict(list)

    for r, c in points:
        rows[r].append((r, c))
        cols[c].append((r, c))

    for arr in rows.values():
        arr.sort(key=lambda x: x[1])
        for a, b in zip(arr, arr[1:]):
            if b[1] - a[1] == 1:
                edges.add((a, b))

    for arr in cols.values():
        arr.sort(key=lambda x: x[0])
        for a, b in zip(arr, arr[1:]):
            if b[0] - a[0] == 1:
                edges.add((a, b))

    adj: Dict[Coord, Set[Coord]] = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    remaining = set(points)
    components: List[Set[Coord]] = []
    while remaining:
        start = remaining.pop()
        stack = [start]
        comp = {start}
        while stack:
            node = stack.pop()
            for nbr in adj[node]:
                if nbr in remaining:
                    remaining.remove(nbr)
                    stack.append(nbr)
                    comp.add(nbr)
        components.append(comp)

    def _allowed(a: Coord, b: Coord) -> bool:
        dr = abs(a[0] - b[0])
        dc = abs(a[1] - b[1])
        return dr == 0 or dc == 0 or dr == dc

    def _weight(a: Coord, b: Coord) -> int:
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    comps = [set(comp) for comp in components]
    while len(comps) > 1:
        best_edge = None
        best_cost = None
        for i in range(len(comps)):
            for j in range(i + 1, len(comps)):
                for a in comps[i]:
                    for b in comps[j]:
                        if _allowed(a, b):
                            cost = _weight(a, b)
                            if best_cost is None or cost < best_cost:
                                best_cost = cost
                                best_edge = (a, b, i, j)
        if best_edge is None:
            break
        a, b, i, j = best_edge
        edges.add((a, b))
        adj[a].add(b)
        adj[b].add(a)
        comps[i] = comps[i] | comps[j]
        comps.pop(j)

    hull = _convex_hull(points)
    if len(hull) >= 2:
        for a, b in zip(hull, hull[1:] + hull[:1]):
            dr = abs(a[0] - b[0])
            dc = abs(a[1] - b[1])
            if not (dr == 0 or dc == 0 or dr == dc):
                continue
            segment = _line_points(a, b)
            conflict = any(
                grid[r][c] != 0 and (r, c) not in points
                for r, c in segment[1:-1]
            )
            if not conflict:
                edges.add((a, b))

    shape: Set[Coord] = set()
    for a, b in edges:
        shape.update(_line_points(a, b))

    return shape if shape else set(points)


def solve_35ab12c3(grid):
    """Solve the puzzle; implementation filled in iteratively."""
    height = len(grid)
    width = len(grid[0]) if grid else 0

    colors = sorted({cell for row in grid for cell in row if cell != 0})
    coord_map: Dict[int, List[Coord]] = {
        color: [
            (r, c)
            for r, row in enumerate(grid)
            for c, value in enumerate(row)
            if value == color
        ]
        for color in colors
    }

    base_colors = [color for color, pts in coord_map.items() if len(pts) >= 2]
    derived_colors = [color for color, pts in coord_map.items() if len(pts) == 1]

    base_shapes: Dict[int, Set[Coord]] = {
        color: _build_base_shape(coord_map[color], grid)
        for color in base_colors
    }
    base_union: Set[Coord] = set().union(*base_shapes.values()) if base_shapes else set()

    result = [[0 for _ in range(width)] for _ in range(height)]

    for color, shape in base_shapes.items():
        for r, c in shape:
            if 0 <= r < height and 0 <= c < width:
                result[r][c] = color

    for color in derived_colors:
        point = coord_map[color][0]
        best = None
        anchor_color = None
        anchor_point = None
        for base_color in base_colors:
            for candidate in coord_map[base_color]:
                dist = abs(point[0] - candidate[0]) + abs(point[1] - candidate[1])
                if best is None or dist < best:
                    best = dist
                    anchor_color = base_color
                    anchor_point = candidate

        if anchor_color is None or anchor_point is None:
            result[point[0]][point[1]] = color
            continue

        delta_r = point[0] - anchor_point[0]
        delta_c = point[1] - anchor_point[1]

        shifted: Set[Coord] = set()
        for r, c in base_shapes[anchor_color]:
            nr = r + delta_r
            nc = c + delta_c
            if 0 <= nr < height and 0 <= nc < width:
                shifted.add((nr, nc))

        shifted = {cell for cell in shifted if cell not in base_union}
        shifted.add(point)

        for r, c in shifted:
            result[r][c] = color

    return result


p = solve_35ab12c3
