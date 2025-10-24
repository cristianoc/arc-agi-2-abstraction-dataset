"""Typed-DSL style solver for ARC-AGI-2 task 89565ca0 (evaluation split).

This refactor preserves the original solver's behavior while expressing the
top-level logic as a pure, staged pipeline to match the DSL lambda.
"""

from collections import Counter, defaultdict, deque
from typing import Dict, List, Optional, Tuple

Grid = List[List[int]]


class ColourStats:
    def __init__(
        self,
        filler_colour: Optional[int],
        areas: Dict[int, int],
        non_filler: List[int],
    ) -> None:
        self.filler_colour = filler_colour
        self.areas = areas
        self.non_filler = non_filler


def _height_width(grid: Grid) -> Tuple[int, int]:
    return (len(grid), len(grid[0]) if grid and grid[0] else 0)


def _stripe_ranges(length: int, parts: int) -> List[Tuple[int, int]]:
    base = length // parts
    extra = length % parts
    start = 0
    ranges: List[Tuple[int, int]] = []
    for idx in range(parts):
        end = start + base + (1 if idx < extra else 0)
        ranges.append((start, end))
        start = end
    return ranges


def _component_count(grid: Grid, color: int) -> int:
    h, w = _height_width(grid)
    seen = [[False] * w for _ in range(h)]
    components = 0
    for sr in range(h):
        for sc in range(w):
            if grid[sr][sc] == color and not seen[sr][sc]:
                components += 1
                dq = deque([(sr, sc)])
                seen[sr][sc] = True
                while dq:
                    cr, cc = dq.pop()
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc] and grid[nr][nc] == color:
                            seen[nr][nc] = True
                            dq.append((nr, nc))
    return components


def tallyColours(grid: Grid) -> ColourStats:
    h, w = _height_width(grid)
    if h == 0 or w == 0:
        return ColourStats(None, {}, [])

    color_cells: Dict[int, int] = defaultdict(int)
    for r in range(h):
        for c in range(w):
            v = grid[r][c]
            if v != 0:
                color_cells[v] += 1

    if not color_cells:
        return ColourStats(None, {}, [])

    components = {col: _component_count(grid, col) for col in color_cells}
    filler = max(components, key=lambda col: components[col])
    areas = dict(color_cells)
    non_filler = [c for c in areas if c != filler]
    return ColourStats(filler, areas, non_filler)


def computeStripeDominators(grid: Grid, stats: ColourStats) -> Dict[int, Optional[int]]:
    h, w = _height_width(grid)
    if h == 0 or w == 0 or stats.filler_colour is None:
        return {}

    filler = stats.filler_colour
    dominators: List[Optional[int]] = []
    for start, end in _stripe_ranges(h, 4):
        if start == end:
            dominators.append(None)
            continue
        counts: Dict[int, int] = Counter()
        for r in range(start, end):
            for c in range(w):
                v = grid[r][c]
                if v != 0:
                    counts[v] += 1
        if not counts:
            dominators.append(None)
            continue
        winner = None
        winner_count = -1
        for col, cnt in counts.items():
            if winner is None or cnt > winner_count or (cnt == winner_count and col == filler and winner != filler):
                winner = col
                winner_count = cnt
        dominators.append(winner)

    bottommost: Dict[int, Optional[int]] = {col: None for col in stats.areas}
    for idx, dom in enumerate(dominators):
        if dom is None:
            continue
        prev = bottommost.get(dom)
        if prev is None or idx > prev:
            bottommost[dom] = idx
    return bottommost


def derivePrefixLengths(stats: ColourStats, stripe_dominators: Dict[int, Optional[int]]) -> Dict[int, int]:
    if stats.filler_colour is None:
        return {}

    filler = stats.filler_colour
    non_filler = stats.non_filler
    areas = stats.areas

    # Fallback for colours that never dominate a stripe.
    prefix_lengths: Dict[int, int] = {}
    no_dom = sorted((c for c in non_filler if stripe_dominators.get(c) is None), key=lambda c: (areas[c], c))
    for rank, col in enumerate(no_dom):
        prefix_lengths[col] = 1 if rank == 0 else 2

    # Map bottommost dominant stripe to refined prefix length.
    for col in non_filler:
        dom_idx = stripe_dominators.get(col)
        if dom_idx is None:
            continue
        if dom_idx == 0:
            prefix_lengths[col] = 2
        elif dom_idx in (1, 2):
            prefix_lengths[col] = 3
        else:
            prefix_lengths[col] = 4

    return prefix_lengths


def renderSummaryRows(prefix_lengths: Dict[int, int], filler_colour: Optional[int]) -> Grid:
    # Distinguish an actually empty grid (no colours at all)
    # from a single-colour grid (only the filler present).
    if filler_colour is None:
        return []

    if not prefix_lengths:
        return [[filler_colour] * 4]

    rows: Grid = []
    for col in sorted(prefix_lengths, key=lambda c: (prefix_lengths[c], c)):
        length = max(1, min(4, prefix_lengths[col]))
        rows.append([col] * length + [filler_colour] * (4 - length))
    return rows


def solve_89565ca0(grid: Grid) -> Grid:
    stats = tallyColours(grid)
    stripe_dominators = computeStripeDominators(grid, stats)
    prefix_lengths = derivePrefixLengths(stats, stripe_dominators)
    return renderSummaryRows(prefix_lengths, stats.filler_colour)


p = solve_89565ca0
