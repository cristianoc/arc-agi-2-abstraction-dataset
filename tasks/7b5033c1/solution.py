"""Solver for ARC-AGI-2 task 7b5033c1."""

from typing import Dict, List, Tuple
from collections import Counter

Grid = List[List[int]]


def tallyColours(grid: Grid) -> Dict[int, int]:
    return dict(Counter(color for row in grid for color in row))


def findFirstPosition(grid: Grid) -> Dict[int, Tuple[int, int]]:
    positions = [(color, (r, c)) for r, row in enumerate(grid) for c, color in enumerate(row)]
    ordered = sorted(positions, key=lambda t: (t[1][0], t[1][1]))
    return {color: pos for color, pos in reversed(ordered)}


def orderColoursByFirstSeen(counts: Dict[int, int], first_seen: Dict[int, Tuple[int, int]]) -> List[Tuple[int, int]]:
    if not counts:
        return []
    background = max(counts.items(), key=lambda item: (item[1], -item[0]))[0]
    items = [
        (first_seen[c][0], first_seen[c][1], c, counts[c])
        for c in counts
        if c != background and c in first_seen
    ]
    items_sorted = sorted(items, key=lambda t: (t[0], t[1], t[2]))
    return [(c, cnt) for _, _, c, cnt in items_sorted]


def buildHistogramColumn(ordered: List[Tuple[int, int]]) -> Grid:
    return [[color] for color, count in ordered for _ in range(count)]


def solve_7b5033c1(grid: Grid) -> Grid:
    counts = tallyColours(grid)
    first_seen = findFirstPosition(grid)
    ordered = orderColoursByFirstSeen(counts, first_seen)
    return buildHistogramColumn(ordered)


p = solve_7b5033c1
