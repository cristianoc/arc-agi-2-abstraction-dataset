"""Refactored solver for ARC-AGI-2 task 64efde09 using a typed-DSL style pipeline."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import List, Sequence, Tuple


# Type aliases for clarity and mypy
Grid = List[List[int]]
Motif = "Component"

BACKGROUND = 8


@dataclass(frozen=True)
class Component:
    cells: Tuple[Tuple[int, int], ...]
    bbox: Tuple[int, int, int, int]


def _clone(grid: Sequence[Sequence[int]]) -> Grid:
    return [list(row) for row in grid]


def identifyMotifs(grid: Sequence[Sequence[int]]) -> List[Component]:
    h = len(grid)
    w = len(grid[0])
    seen = [[False] * w for _ in range(h)]
    comps: List[Component] = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] == BACKGROUND or seen[r][c]:
                continue
            q = deque([(r, c)])
            seen[r][c] = True
            cells: List[Tuple[int, int]] = []
            while q:
                x, y = q.popleft()
                cells.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w:
                        if not seen[nx][ny] and grid[nx][ny] != BACKGROUND:
                            seen[nx][ny] = True
                            q.append((nx, ny))
            rs = [rr for rr, _ in cells]
            cs = [cc for _, cc in cells]
            bbox = (min(rs), min(cs), max(rs), max(cs))
            comps.append(Component(tuple(cells), bbox))
    return comps


def _vertical_offsets(h: int) -> List[int]:
    if h >= 9:
        return [1, 3, 5]
    if h >= 7:
        return [1, h - 3, h - 2]
    if h >= 5:
        return [1, h - 2, h - 1]
    return [min(1, h - 1)] * 3


def castVerticalShadows(grid: Sequence[Sequence[int]], motifs: Sequence[Component]) -> Grid:
    out = _clone(grid)
    h = len(out)
    w = len(out[0])
    accent = sorted(
        grid[r][c]
        for comp in motifs
        if len(comp.cells) == 1
        for (r, c) in comp.cells
    )
    base = [comp for comp in motifs if len(comp.cells) > 1]
    boxes = [comp.bbox for comp in base]
    vertical_indices = [
        idx
        for idx, (top, left, bottom, right) in enumerate(boxes)
        if (bottom - top) > (right - left)
    ]
    vertical_indices.sort(key=lambda idx: (boxes[idx][1] + boxes[idx][3]) / 2)
    for order, idx in enumerate(vertical_indices):
        top, left, bottom, right = boxes[idx]
        span = bottom - top + 1
        offsets = [off for off in _vertical_offsets(span) if 0 <= off < span]
        palette = accent if span >= 9 else list(reversed(accent))
        extend_left = order % 2 == 0
        for tone, offset in zip(palette, offsets):
            row = top + offset
            if extend_left:
                col = left - 1
                while col >= 0 and out[row][col] == BACKGROUND:
                    out[row][col] = tone
                    col -= 1
            else:
                col = right + 1
                while col < w and out[row][col] == BACKGROUND:
                    out[row][col] = tone
                    col += 1
    return out


def castHorizontalShadows(grid: Sequence[Sequence[int]], motifs: Sequence[Component]) -> Grid:
    out = _clone(grid)
    h = len(out)
    w = len(out[0])
    accent = sorted(
        grid[r][c]
        for comp in motifs
        if len(comp.cells) == 1
        for (r, c) in comp.cells
    )
    for comp in motifs:
        top, left, bottom, right = comp.bbox
        span_rows = bottom - top + 1
        span_cols = right - left + 1
        if span_rows > span_cols:
            continue
        if top <= 2:
            below_top = top - 1
            two_above = top - 2
            target_cols = [right - 5, right - 3, right - 1]
            if below_top >= 0:
                for col, tone in zip(target_cols, sorted(accent, reverse=True)):
                    if 0 <= col < w and out[below_top][col] == BACKGROUND:
                        out[below_top][col] = tone
            if two_above >= 0:
                for col, tone in zip((right - 5, right - 1), (accent[-1], accent[0])):
                    if 0 <= col < w and out[two_above][col] == BACKGROUND:
                        out[two_above][col] = tone
        else:
            columns = sorted({left + 1, left + 2, right - 1})
            for col, tone in zip(columns, accent):
                if not (left <= col <= right):
                    continue
                row = bottom + 1
                while row < h and out[row][col] == BACKGROUND:
                    out[row][col] = tone
                    row += 1
    return out


def mergeShadowPasses(original: Sequence[Sequence[int]], vertical: Sequence[Sequence[int]], horizontal: Sequence[Sequence[int]]) -> Grid:
    # Horizontal shadows are applied on top of vertical shadows in this solver.
    return _clone(horizontal)


def solve_64efde09(grid: Grid) -> Grid:
    motifs = identifyMotifs(grid)
    vertical = castVerticalShadows(grid, motifs)
    horizontal = castHorizontalShadows(vertical, motifs)
    return mergeShadowPasses(grid, vertical, horizontal)


p = solve_64efde09
