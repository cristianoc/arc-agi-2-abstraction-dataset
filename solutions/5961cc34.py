"""Solver for ARC-AGI-2 task 5961cc34 (split: evaluation)."""

from collections import deque


def _component_scan(grid):
    """Enumerate connected components with boundary metadata."""

    h, w = len(grid), len(grid[0])
    visited = [[False] * w for _ in range(h)]
    components = []

    for r in range(h):
        for c in range(w):
            if grid[r][c] == 8 or visited[r][c]:
                continue

            stack = [(r, c)]
            visited[r][c] = True
            coords = []
            colors = set()

            while stack:
                x, y = stack.pop()
                coords.append((x, y))
                colors.add(grid[x][y])

                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < h and 0 <= ny < w and not visited[nx][ny] and grid[nx][ny] != 8:
                        visited[nx][ny] = True
                        stack.append((nx, ny))

            rows = [x for x, _ in coords]
            cols = [y for _, y in coords]
            min_r, min_c, max_r, max_c = min(rows), min(cols), max(rows), max(cols)

            threes = []
            fours = []
            for x, y in coords:
                directions = []
                if x == min_r:
                    directions.append((-1, 0))
                if x == max_r:
                    directions.append((1, 0))
                if y == min_c:
                    directions.append((0, -1))
                if y == max_c:
                    directions.append((0, 1))

                value = grid[x][y]
                if value == 3:
                    threes.append(((x, y), directions))
                elif value == 4:
                    fours.append(((x, y), directions))

            components.append(
                {
                    "coords": coords,
                    "colors": colors,
                    "bbox": (min_r, min_c, max_r, max_c),
                    "threes": threes,
                    "fours": fours,
                }
            )

    return components


def _extend_ray(grid, origin, direction):
    """Collect background cells reached from origin while following direction."""

    h, w = len(grid), len(grid[0])
    dr, dc = direction
    r, c = origin[0] + dr, origin[1] + dc
    ray = []

    while 0 <= r < h and 0 <= c < w and grid[r][c] == 8:
        ray.append((r, c))
        r += dr
        c += dc

    return ray


def solve_5961cc34(grid):
    """Construct the connected blue scaffold defined by the oriented motifs."""

    components = _component_scan(grid)
    sentinel = next(comp for comp in components if 2 in comp["colors"])
    others = [comp for comp in components if comp is not sentinel]

    candidates = set(sentinel["coords"])

    # The red cap (4) indicates where to shoot the sentinel's vertical ray.
    for (cell, directions) in sentinel["fours"]:
        direction = next((d for d in directions if d == (-1, 0)), None)
        if direction is None and directions:
            direction = directions[0]
        if direction:
            candidates.update(_extend_ray(grid, cell, direction))

    for comp in others:
        if len(comp["threes"]) < 2:
            continue  # Skip motifs that lack the paired orange guides.

        candidates.update(comp["coords"])

        for (cell, directions) in comp["threes"]:
            if not directions:
                continue
            candidates.update(_extend_ray(grid, cell, directions[0]))

    queue = deque(candidates & set(sentinel["coords"]))
    reachable = set(queue)

    while queue:
        r, c = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if (nr, nc) in candidates and (nr, nc) not in reachable:
                reachable.add((nr, nc))
                queue.append((nr, nc))

    h, w = len(grid), len(grid[0])
    output = [[8] * w for _ in range(h)]
    for r, c in reachable:
        output[r][c] = 2

    return output


p = solve_5961cc34
