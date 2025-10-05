"""Auto-generated identity stub for ARC-AGI-2 task 8f3a5a89 (split: evaluation)."""

def solve_8f3a5a89(grid):
    """Solve ARC task 8f3a5a89."""
    from collections import deque

    h = len(grid)
    w = len(grid[0]) if h else 0
    result = [row[:] for row in grid]

    # Step 1: collect all background cells (color 8) reachable from the left edge.
    accessible = set()
    seen = [[False] * w for _ in range(h)]
    q = deque()
    for r in range(h):
        if grid[r][0] == 8 and not seen[r][0]:
            seen[r][0] = True
            q.append((r, 0))
    while q:
        r, c = q.popleft()
        accessible.add((r, c))
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 8 and not seen[nr][nc]:
                seen[nr][nc] = True
                q.append((nr, nc))

    # Step 2: label non-accessible components to know which ones touch the border.
    comp_touch = [[False] * w for _ in range(h)]
    all_cells = {(r, c) for r in range(h) for c in range(w)}
    blocked = all_cells - accessible
    visited = set()
    for cell in blocked:
        if cell in visited:
            continue
        q = deque([cell])
        visited.add(cell)
        component = []
        touches_border = False
        while q:
            r, c = q.popleft()
            component.append((r, c))
            if r in (0, h - 1) or c in (0, w - 1):
                touches_border = True
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w and (nr, nc) in blocked and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append((nr, nc))
        for r, c in component:
            comp_touch[r][c] = touches_border

    # Step 3: prune colour-1 components that are irrelevant to the left-accessible region.
    seen_ones = [[False] * w for _ in range(h)]
    for sr in range(h):
        for sc in range(w):
            if grid[sr][sc] != 1 or seen_ones[sr][sc]:
                continue
            q = deque([(sr, sc)])
            seen_ones[sr][sc] = True
            component = []
            touches_left = False
            near_access = False
            while q:
                r, c = q.popleft()
                component.append((r, c))
                if c == 0:
                    touches_left = True
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < h and 0 <= nc < w and (nr, nc) in accessible:
                            near_access = True
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 1 and not seen_ones[nr][nc]:
                        seen_ones[nr][nc] = True
                        q.append((nr, nc))
            if touches_left or near_access:
                continue
            for r, c in component:
                result[r][c] = 8

    # Step 4: paint the accessible frontier with colour 7.
    sevens = set()

    def touches_outside(r, c):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if not (0 <= nr < h and 0 <= nc < w):
                return True
            if (nr, nc) not in accessible:
                if comp_touch[nr][nc]:
                    return True
        return False

    for r, c in accessible:
        if touches_outside(r, c):
            sevens.add((r, c))

    for r, c in accessible:
        if (r, c) in sevens:
            continue
        for dr, dc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 1 and comp_touch[nr][nc]:
                sevens.add((r, c))
                break

    for r, c in accessible:
        result[r][c] = 7 if (r, c) in sevens else 8

    return result


p = solve_8f3a5a89
