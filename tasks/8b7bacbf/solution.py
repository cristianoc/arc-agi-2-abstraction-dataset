"""Solver for ARC-AGI-2 task 8b7bacbf (evaluation split)."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


Grid = List[List[int]]
# Use an immutable, hashable representation for components so they can be dict keys.
Component = Tuple[Tuple[int, int], ...]


# --- Minimal functional DSL helpers (runtime implementations) ---

def fold_repaint(initial: Grid, items: List[Component], update):
    canvas = [row[:] for row in initial]
    for item in items:
        canvas = update(canvas, item)
    return canvas


class _Info:
    def __init__(
        self,
        colour: int,
        border_colour: int,
        min_higher: Optional[int],
        min_lower: Optional[int],
        has_higher: bool,
    ) -> None:
        self.colour = colour
        self.border_colour = border_colour
        self.min_higher = min_higher
        self.min_lower = min_lower
        self.has_higher = has_higher


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _zero_components(grid: Sequence[Sequence[int]]) -> List[Component]:
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    comps: List[Component] = []

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 0 or seen[r][c]:
                continue
            queue = deque([(r, c)])
            seen[r][c] = True
            cells: List[Tuple[int, int]] = []
            while queue:
                rr, cc = queue.popleft()
                cells.append((rr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc] and grid[nr][nc] == 0:
                        seen[nr][nc] = True
                        queue.append((nr, nc))
            comps.append(tuple(sorted(cells)))
    return comps


def _component_border_colour(grid: Sequence[Sequence[int]], component: Component) -> Optional[int]:
    h, w = len(grid), len(grid[0])
    boundary: set[int] = set()
    for rr, cc in component:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = rr + dr, cc + dc
            if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] != 0:
                boundary.add(grid[nr][nc])
    return next(iter(boundary)) if len(boundary) == 1 else None


def _min_distance(points_a: Iterable[Tuple[int, int]], points_b: Iterable[Tuple[int, int]]) -> Optional[int]:
    best: Optional[int] = None
    pts_b = list(points_b)
    if not pts_b:
        return None
    for rr, cc in points_a:
        for pr, pc in pts_b:
            dist = abs(rr - pr) + abs(cc - pc)
            if best is None or dist < best:
                best = dist
                if best == 0:
                    return 0
    return best


# --- Publicly named helpers to align with the DSL lambda ---

def extractZeroComponents(grid: Grid) -> List[Component]:
    return _zero_components(grid)


def measureBoundaryDistances(grid: Grid, cavities: List[Component]) -> Dict[Component, _Info]:
    h, w = len(grid), len(grid[0])
    counts: Counter[int] = Counter()
    positions = defaultdict(list)
    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            counts[val] += 1
            positions[val].append((r, c))

    fill_colour = max(counts)
    out: Dict[Component, _Info] = {}

    for comp in cavities:
        border = _component_border_colour(grid, comp)
        if border is None:
            continue
        candidate_colours = [
            colour
            for colour, cnt in counts.items()
            if colour not in (0, border) and cnt > 1
        ]
        if not candidate_colours:
            continue
        higher = [c for c in candidate_colours if c > border]
        lower = [c for c in candidate_colours if c <= border]

        min_higher = None
        if higher:
            dists_opt = [
                _min_distance(comp, positions[colour])
                for colour in higher
            ]
            dists: List[int] = [d for d in dists_opt if d is not None]
            min_higher = min(dists) if dists else None

        min_lower = None
        if lower:
            dists_opt_lower = [
                _min_distance(comp, positions[colour])
                for colour in lower
            ]
            dists_lower: List[int] = [d for d in dists_opt_lower if d is not None]
            min_lower = min(dists_lower) if dists_lower else None

        out[comp] = _Info(
            colour=fill_colour,
            border_colour=border,
            min_higher=min_higher,
            min_lower=min_lower,
            has_higher=bool(higher),
        )

    return out


def shouldFill(component: Component, info: _Info) -> bool:
    if info.has_higher and info.min_higher is not None and info.min_higher <= 4:
        return True
    if (not info.has_higher or info.border_colour > 2) and info.min_lower is not None and info.min_lower <= 3:
        return True
    return False


def paintComponent(canvas: Grid, component: Component, colour: int) -> Grid:
    result = _copy_grid(canvas)
    for r, c in component:
        result[r][c] = colour
    return result


def solve_8b7bacbf(grid: Grid) -> Grid:
    cavities = extractZeroComponents(grid)
    distance_info = measureBoundaryDistances(grid, cavities)

    def repaint(canvas: Grid, component: Component) -> Grid:
        info = distance_info.get(component)
        if info is None or not shouldFill(component, info):
            return canvas
        return paintComponent(canvas, component, info.colour)

    return fold_repaint(grid, cavities, repaint)


p = solve_8b7bacbf
