"""Solver for ARC-AGI-2 task 332f06d7 (evaluation split)."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple


Grid = List[List[int]]
Block = Tuple[int, int, int, int]  # (r0, c0, r1, c1)

DIRECTIONS: Tuple[Tuple[int, int, str], ...] = (
    (-1, 0, "up"),
    (1, 0, "down"),
    (0, -1, "left"),
    (0, 1, "right"),
)


def _collect(grid: Grid, colour: int) -> List[Tuple[int, int]]:
    return [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == colour]


def _bbox(cells: Sequence[Tuple[int, int]]) -> Block:
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    return (min(rows), min(cols), max(rows), max(cols))


def _centre(box: Block) -> Tuple[float, float]:
    r0, c0, r1, c1 = box
    return (r0 + r1) / 2.0, (c0 + c1) / 2.0


def _materialise_box(box: Block) -> List[Tuple[int, int]]:
    r0, c0, r1, c1 = box
    return [(r, c) for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)]


def _adjacency(grid: Grid, cells: Iterable[Tuple[int, int]], target: int = 3) -> set[str]:
    h, w = len(grid), len(grid[0])
    adj: set[str] = set()
    for r, c in cells:
        for dr, dc, name in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w:
                if grid[nr][nc] == target:
                    adj.add(name)
            else:
                adj.add(name)
    return adj


# === DSL helpers (typed names) ===

def locateZeroBlock(grid: Grid) -> Block:
    zeros = _collect(grid, 0)
    return _bbox(zeros) if zeros else (0, 0, -1, -1)


def locateColor2Block(grid: Grid) -> Block:
    twos = _collect(grid, 2)
    return _bbox(twos) if twos else (0, 0, -1, -1)


def collectCandidateBlocks(grid: Grid) -> List[Tuple[Block, int]]:
    zeros = _collect(grid, 0)
    ones = _collect(grid, 1)
    twos = _collect(grid, 2)
    if not zeros or not ones or not twos:
        # Provide a safe fallback candidate so selection does not crash.
        two_box = _bbox(twos) if twos else (0, 0, -1, -1)
        return [(two_box, -10)]

    zero_box = _bbox(zeros)
    one_box = _bbox(ones)
    two_box = _bbox(twos)

    zero_h = zero_box[2] - zero_box[0] + 1
    zero_w = zero_box[3] - zero_box[1] + 1

    one_center = _centre(one_box)
    two_center = _centre(two_box)
    color2_adj = _adjacency(grid, _materialise_box(two_box))
    missing = {name for _, _, name in DIRECTIONS} - color2_adj
    color2_dist_one = abs(two_center[0] - one_center[0]) + abs(two_center[1] - one_center[1])

    h, w = len(grid), len(grid[0])
    out: List[Tuple[Block, int]] = []
    for top in range(h - zero_h + 1):
        for left in range(w - zero_w + 1):
            # window contents
            vals = [grid[r][c] for r in range(top, top + zero_h) for c in range(left, left + zero_w)]
            if len(set(vals)) != 1 or vals[0] != 1:
                continue
            box = (top, left, top + zero_h - 1, left + zero_w - 1)
            adj = _adjacency(grid, _materialise_box(box))
            if missing and not (missing <= adj):
                continue
            if len(adj) != len(color2_adj):
                continue
            centre_r = top + (zero_h - 1) / 2.0
            centre_c = left + (zero_w - 1) / 2.0
            dist_one = abs(centre_r - one_center[0]) + abs(centre_c - one_center[1])
            improvement = int(color2_dist_one - dist_one)
            out.append((box, improvement))

    # Ensure a fallback exists for max(); two_box with poor score.
    out.append((two_box, -10))
    return out


def scoreCandidates(zero_block: Block, candidates: List[Tuple[Block, int]]) -> List[Tuple[Block, int]]:
    # Scoring is precomputed during candidate collection; pass through.
    return candidates


def relocateZeroBlock(grid: Grid, zero_block: Block, target_block: Block) -> Grid:
    r0, c0, r1, c1 = zero_block
    if r1 < r0 or c1 < c0:
        return [row[:] for row in grid]
    zero_cells = _materialise_box(zero_block)
    out = [row[:] for row in grid]
    for r, c in zero_cells:
        out[r][c] = 1
    for r, c in _materialise_box(target_block):
        out[r][c] = 0
    return out


# === Main (must match abstractions.md lambda exactly) ===
def solve_332f06d7(grid: Grid) -> Grid:
    zero_block = locateZeroBlock(grid)
    candidates = collectCandidateBlocks(grid)
    scored = scoreCandidates(zero_block, candidates)
    best = max(scored, key=lambda x: x[1])
    two_block = locateColor2Block(grid)
    return relocateZeroBlock(grid, zero_block, best[0] if best[1] >= 5 else two_block)


p = solve_332f06d7
