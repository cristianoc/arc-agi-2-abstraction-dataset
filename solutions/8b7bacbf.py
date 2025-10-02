"""Solver for ARC-AGI-2 task 8b7bacbf (evaluation split)."""

from collections import Counter, defaultdict, deque


def solve_8b7bacbf(grid):
    """Fill selected enclosed voids with the grid's maximal color."""

    h, w = len(grid), len(grid[0])
    colour_counts = Counter()
    colour_positions = defaultdict(list)
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            colour_counts[value] += 1
            colour_positions[value].append((r, c))

    fill_colour = max(colour_counts)
    result = [row[:] for row in grid]
    visited = [[False] * w for _ in range(h)]

    def min_manhattan_distance(component, colour):
        points = colour_positions.get(colour)
        if not points:
            return None
        best = None
        for rr, cc in component:
            for pr, pc in points:
                dist = abs(rr - pr) + abs(cc - pc)
                if best is None or dist < best:
                    best = dist
                    if best == 0:
                        return 0
        return best

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 0 or visited[r][c]:
                continue

            queue = deque([(r, c)])
            visited[r][c] = True
            component = []
            boundary_colours = set()

            while queue:
                rr, cc = queue.popleft()
                component.append((rr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w:
                        if grid[nr][nc] == 0 and not visited[nr][nc]:
                            visited[nr][nc] = True
                            queue.append((nr, nc))
                        elif grid[nr][nc] != 0:
                            boundary_colours.add(grid[nr][nc])

            if len(boundary_colours) != 1:
                continue

            border_colour = next(iter(boundary_colours))
            candidate_colours = [
                colour
                for colour, count in colour_counts.items()
                if colour not in (0, border_colour) and count > 1
            ]
            if not candidate_colours:
                continue

            higher_colours = [c for c in candidate_colours if c > border_colour]
            lower_colours = [c for c in candidate_colours if c <= border_colour]

            fill = False

            if higher_colours:
                distances = [
                    min_manhattan_distance(component, colour)
                    for colour in higher_colours
                ]
                distances = [d for d in distances if d is not None]
                if distances and min(distances) <= 4:
                    fill = True

            if not fill and (not higher_colours or border_colour > 2) and lower_colours:
                distances = [
                    min_manhattan_distance(component, colour)
                    for colour in lower_colours
                ]
                distances = [d for d in distances if d is not None]
                if distances and min(distances) <= 3:
                    fill = True

            if fill:
                for rr, cc in component:
                    result[rr][cc] = fill_colour

    return result


p = solve_8b7bacbf
