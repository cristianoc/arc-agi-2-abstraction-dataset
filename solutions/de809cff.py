"""Solver for ARC-AGI-2 task de809cff."""

from typing import List

Grid = List[List[int]]


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def solve_de809cff(grid: Grid) -> Grid:
    """Apply halo expansion around strong zero-pockets and prune stragglers."""
    height = len(grid)
    width = len(grid[0])
    colors = sorted({value for row in grid for value in row if value != 0})
    if len(colors) != 2:
        return _copy_grid(grid)

    primary, secondary = colors
    other = {primary: secondary, secondary: primary}
    orth_offsets = ((1, 0), (-1, 0), (0, 1), (0, -1))

    def in_bounds(r: int, c: int) -> bool:
        return 0 <= r < height and 0 <= c < width

    seeds = []
    for r in range(height):
        for c in range(width):
            if grid[r][c] != 0:
                continue
            neighbours = [
                grid[nr][nc]
                for dr, dc in orth_offsets
                if in_bounds(nr := r + dr, nc := c + dc) and grid[nr][nc] != 0
            ]
            if len(neighbours) >= 3 and len(set(neighbours)) == 1:
                seeds.append((r, c, neighbours[0]))

    out = _copy_grid(grid)
    for r, c, _ in seeds:
        out[r][c] = 8

    for r, c, colour in seeds:
        halo_colour = other[colour]
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if not in_bounds(nr, nc) or (nr, nc) == (r, c):
                    continue
                if out[nr][nc] == 8:
                    continue
                original = grid[nr][nc]
                if original == colour or original == 0:
                    out[nr][nc] = halo_colour

    for r in range(height):
        for c in range(width):
            if grid[r][c] != secondary or out[r][c] != grid[r][c]:
                continue
            primary_neighbours = sum(
                1
                for dr, dc in orth_offsets
                if in_bounds(r + dr, c + dc) and grid[r + dr][c + dc] == primary
            )
            if primary_neighbours >= 3:
                out[r][c] = primary

    for r in range(height):
        for c in range(width):
            if grid[r][c] == 0 or out[r][c] != grid[r][c]:
                continue
            zero_neighbours = sum(
                1
                for dr, dc in orth_offsets
                if not in_bounds(r + dr, c + dc) or grid[r + dr][c + dc] == 0
            )
            if zero_neighbours >= 3:
                out[r][c] = 0

    return out


p = solve_de809cff
