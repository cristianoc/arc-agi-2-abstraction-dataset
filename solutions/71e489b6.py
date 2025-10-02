"""Solver for ARC-AGI-2 task 71e489b6 (evaluation split)."""

from collections import deque

OFFSETS4 = ((1, 0), (-1, 0), (0, 1), (0, -1))


def solve_71e489b6(grid):
    """Detect 0-tips and draw 7 halos while pruning stray 1s."""
    h, w = len(grid), len(grid[0])
    original = [row[:] for row in grid]
    result = [row[:] for row in grid]

    def zero_neighbors(r, c):
        return sum(
            1
            for dr, dc in OFFSETS4
            if 0 <= r + dr < h and 0 <= c + dc < w and original[r + dr][c + dc] == 0
        )

    # Step 1: turn lonely 1s into 0s when they are surrounded by zeros.
    for r in range(h):
        for c in range(w):
            if original[r][c] == 1 and zero_neighbors(r, c) >= 3:
                result[r][c] = 0

    # Step 2: locate zero components and their degree-≤1 "tips".
    seen = [[False] * w for _ in range(h)]
    tips = set()
    for r in range(h):
        for c in range(w):
            if original[r][c] == 0 and not seen[r][c]:
                comp = []
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

    # Pre-compute, for each original zero cell, how many tip neighbours it has.
    tip_adj = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            if original[r][c] == 0:
                tip_adj[r][c] = sum(
                    1
                    for dr, dc in OFFSETS4
                    if 0 <= r + dr < h and 0 <= c + dc < w and (r + dr, c + dc) in tips
                )

    # Step 3: paint 7 halos around each tip (and its unique zero neighbour).
    for tr, tc in tips:
        zero_neighbor = None
        for dr, dc in OFFSETS4:
            nr, nc = tr + dr, tc + dc
            if 0 <= nr < h and 0 <= nc < w and original[nr][nc] == 0:
                zero_neighbor = (nr, nc)
                break

        pivots = [(tr, tc)]
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


p = solve_71e489b6
