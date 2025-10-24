"""Solver for ARC-AGI-2 task 71e489b6 (evaluation split)."""

from __future__ import annotations

from collections import deque
from typing import List, Sequence, Set, Tuple


Grid = List[List[int]]
Cell = Tuple[int, int]
OFFSETS4: Tuple[Tuple[int, int], ...] = ((1, 0), (-1, 0), (0, 1), (0, -1))


def countZeroNeighbours(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    h, w = len(grid), len(grid[0])
    counts: List[List[int]] = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            counts[r][c] = sum(
                1
                for dr, dc in OFFSETS4
                if 0 <= r + dr < h and 0 <= c + dc < w and grid[r + dr][c + dc] == 0
            )
    return counts


def pruneLonelyOnes(grid: Sequence[Sequence[int]], zero_counts: Sequence[Sequence[int]]) -> Grid:
    h, w = len(grid), len(grid[0])
    result: Grid = [list(row) for row in grid]
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 1 and zero_counts[r][c] >= 3:
                result[r][c] = 0
    return result


def collectZeroTips(original: Sequence[Sequence[int]], zero_counts: Sequence[Sequence[int]]) -> Set[Cell]:
    h, w = len(original), len(original[0])
    seen = [[False] * w for _ in range(h)]
    tips: Set[Cell] = set()

    def zero_neighbors(r: int, c: int) -> int:
        return sum(
            1
            for dr, dc in OFFSETS4
            if 0 <= r + dr < h and 0 <= c + dc < w and original[r + dr][c + dc] == 0
        )

    for r in range(h):
        for c in range(w):
            if original[r][c] == 0 and not seen[r][c]:
                comp: List[Cell] = []
                queue = deque([(r, c)])
                seen[r][c] = True
                while queue:
                    rr, cc = queue.popleft()
                    comp.append((rr, cc))
                    for dr, dc in OFFSETS4:
                        nr, nc = rr + dr, cc + dc
                        if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc] and original[nr][nc] == 0:
                            seen[nr][nc] = True
                            queue.append((nr, nc))
                for rr, cc in comp:
                    if zero_neighbors(rr, cc) <= 1:
                        tips.add((rr, cc))
    return tips


def paintTipHalos(
    original: Sequence[Sequence[int]],
    cleaned: Sequence[Sequence[int]],
    tips: Set[Cell],
    zero_counts: Sequence[Sequence[int]],
) -> Grid:
    h, w = len(cleaned), len(cleaned[0])
    base: Grid = [list(row) for row in cleaned]
    result: Grid = [list(row) for row in cleaned]

    # Pre-compute, for each zero cell in the original (pre-halo) canvas, how many tip neighbours it has.
    tip_adj: List[List[int]] = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            if original[r][c] == 0:
                tip_adj[r][c] = sum(
                    1
                    for dr, dc in OFFSETS4
                    if 0 <= r + dr < h and 0 <= c + dc < w and (r + dr, c + dc) in tips
                )

    for tr, tc in tips:
        zero_neighbor: Cell | None = None
        for dr, dc in OFFSETS4:
            nr, nc = tr + dr, tc + dc
            if 0 <= nr < h and 0 <= nc < w and original[nr][nc] == 0:
                zero_neighbor = (nr, nc)
                break

        pivots: List[Cell] = [(tr, tc)]
        if zero_neighbor is not None:
            pivots.append(zero_neighbor)

        for pr, pc in pivots:
            is_tip = (pr, pc) == (tr, tc)
            delta_r = pr - tr if not is_tip else 0
            delta_c = pc - tc if not is_tip else 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = pr + dr, pc + dc
                    if not (0 <= nr < h and 0 <= nc < w):
                        continue
                    if (nr, nc) in tips:
                        continue
                    if original[nr][nc] == 0 and tip_adj[nr][nc] >= 2:
                        continue
                    if dr == 0 and dc == 0:
                        if is_tip:
                            result[nr][nc] = 0
                        elif tip_adj[pr][pc] < 2:
                            result[nr][nc] = 7
                        continue
                    if not is_tip:
                        if original[nr][nc] == 0:
                            continue
                        if delta_r == dr and delta_c == dc:
                            continue
                    result[nr][nc] = 7

        result[tr][tc] = 0

    return result


def solve_71e489b6(grid: Grid) -> Grid:
    zero_counts = countZeroNeighbours(grid)
    cleaned = pruneLonelyOnes(grid, zero_counts)
    tips = collectZeroTips(grid, zero_counts)
    return paintTipHalos(grid, cleaned, tips, zero_counts)


p = solve_71e489b6
