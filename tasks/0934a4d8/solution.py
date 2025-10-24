"""Solver for ARC-AGI-2 task 0934a4d8 (typed DSL style)."""

from __future__ import annotations

from typing import List, Tuple, NamedTuple


# Typed aliases matching the DSL docs
Grid = List[List[int]]
Block = Grid


class Candidate(NamedTuple):
    block: Block
    distance: int
    count8: int
    axis: str  # 'H' or 'V'


def bbox(grid: Grid) -> Tuple[int, int, int, int]:
    positions = [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == 8]
    if not positions:
        raise ValueError("target value not found in grid")
    rows = [r for r, _ in positions]
    cols = [c for _, c in positions]
    r0 = min(rows)
    r1 = max(rows) + 1
    c0 = min(cols)
    c1 = max(cols) + 1
    return (r0, r1, c0, c1)


def _extract_block(grid: Grid, r_start: int, c_start: int, height: int, width: int) -> Block:
    return [row[c_start : c_start + width] for row in grid[r_start : r_start + height]]


def _flip_lr(block: Block) -> Block:
    return [list(reversed(row)) for row in block]


def _flip_ud(block: Block) -> Block:
    return [row[:] for row in block[::-1]]


def mirrorH(grid: Grid, box: Tuple[int, int, int, int]) -> Candidate:
    r0, r1, c0, c1 = box
    height = r1 - r0
    width = c1 - c0
    total_cols = len(grid[0])
    offset = 2
    start = total_cols - width - c0 + offset
    valid = 0 <= start <= total_cols - width
    block = _extract_block(grid, r0, start, height, width) if valid else []
    dist = abs(c0 - start) if valid else -1
    cnt8 = sum(v == 8 for row in block for v in row) if valid else -1
    return Candidate(block=block, distance=dist, count8=cnt8, axis='H')


def mirrorV(grid: Grid, box: Tuple[int, int, int, int]) -> Candidate:
    r0, r1, c0, c1 = box
    height = r1 - r0
    width = c1 - c0
    total_rows = len(grid)
    offset = 2
    start = total_rows - height - r0 + offset
    valid = 0 <= start <= total_rows - height
    block = _extract_block(grid, start, c0, height, width) if valid else []
    dist = abs(r0 - start) if valid else -1
    cnt8 = sum(v == 8 for row in block for v in row) if valid else -1
    return Candidate(block=block, distance=dist, count8=cnt8, axis='V')


def selectCandidate(a: Candidate, b: Candidate) -> Candidate:
    if a.distance > b.distance:
        return a
    if b.distance > a.distance:
        return b
    if a.distance < 0 <= b.distance:
        return b
    if b.distance < 0 <= a.distance:
        return a
    if b.count8 < a.count8:
        return b
    if a.count8 < b.count8:
        return a
    return a


def flipOutput(chosen: Candidate) -> Block:
    return _flip_lr(chosen.block) if chosen.axis == 'H' else _flip_ud(chosen.block)


def solve_0934a4d8(grid: Grid) -> Block:
    bbox_val = bbox(grid)
    h_candidate = mirrorH(grid, bbox_val)
    v_candidate = mirrorV(grid, bbox_val)
    chosen = selectCandidate(h_candidate, v_candidate)
    return flipOutput(chosen)


p = solve_0934a4d8
