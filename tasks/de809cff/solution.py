"""Solver for ARC-AGI-2 task de809cff."""

from typing import List, Tuple

Grid = List[List[int]]
Cell = Tuple[int, int]
Color = int
Seed = Tuple[Cell, Color]


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _dims(grid: Grid) -> Tuple[int, int]:
    return len(grid), len(grid[0]) if grid else 0


def _in_bounds(r: int, c: int, h: int, w: int) -> bool:
    return 0 <= r < h and 0 <= c < w


def _nonzero_colors(grid: Grid) -> List[int]:
    return sorted({v for row in grid for v in row if v != 0})


def detectZeroSeeds(grid: Grid) -> List[Seed]:
    """Find zero cells with ≥3 matching non-zero orthogonal neighbours, record host colour."""
    h, w = _dims(grid)
    orth = ((1, 0), (-1, 0), (0, 1), (0, -1))
    seeds: List[Seed] = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] != 0:
                continue
            neighbours = [
                grid[nr][nc]
                for dr, dc in orth
                if _in_bounds(nr := r + dr, nc := c + dc, h, w) and grid[nr][nc] != 0
            ]
            if len(neighbours) >= 3 and len(set(neighbours)) == 1:
                seeds.append(((r, c), neighbours[0]))
    return seeds


def paintHalos(grid: Grid, seeds: List[Seed]) -> Grid:
    """Paint seed cell to 8 and surround with the opposite colour halo (incl. diagonals)."""
    colors = _nonzero_colors(grid)
    if len(colors) != 2:
        return _copy_grid(grid)
    primary, secondary = colors
    other = {primary: secondary, secondary: primary}

    h, w = _dims(grid)
    out = _copy_grid(grid)

    for (r, c), _ in seeds:
        out[r][c] = 8

    for (r, c), colour in seeds:
        halo_colour = other[colour]
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if not _in_bounds(nr, nc, h, w) or (nr, nc) == (r, c):
                    continue
                if out[nr][nc] == 8:
                    continue
                original = grid[nr][nc]
                if original == colour or original == 0:
                    out[nr][nc] = halo_colour
    return out


def realignSecondaryPixels(grid: Grid, halo_grid: Grid) -> Grid:
    """Flip unchanged secondary pixels supported by ≥3 primary neighbours in the original grid."""
    colors = _nonzero_colors(grid)
    if len(colors) != 2:
        return _copy_grid(halo_grid)
    primary, secondary = colors
    h, w = _dims(grid)
    orth = ((1, 0), (-1, 0), (0, 1), (0, -1))
    out = _copy_grid(halo_grid)
    for r in range(h):
        for c in range(w):
            if grid[r][c] != secondary or out[r][c] != grid[r][c]:
                continue
            primary_neighbours = sum(
                1
                for dr, dc in orth
                if _in_bounds(r + dr, c + dc, h, w) and grid[r + dr][c + dc] == primary
            )
            if primary_neighbours >= 3:
                out[r][c] = primary
    return out


def pruneStragglers(grid: Grid, realigned: Grid) -> Grid:
    """Remove unchanged pixels that have ≥3 zero neighbours (counting off-grid as zero)."""
    colors = _nonzero_colors(grid)
    if len(colors) != 2:
        return _copy_grid(realigned)
    h, w = _dims(grid)
    orth = ((1, 0), (-1, 0), (0, 1), (0, -1))
    out = _copy_grid(realigned)
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 0 or out[r][c] != grid[r][c]:
                continue
            zero_neighbours = sum(
                1
                for dr, dc in orth
                if not _in_bounds(r + dr, c + dc, h, w) or grid[r + dr][c + dc] == 0
            )
            if zero_neighbours >= 3:
                out[r][c] = 0
    return out


def solve_de809cff(grid: Grid) -> Grid:
    seeds = detectZeroSeeds(grid)
    halo_grid = paintHalos(grid, seeds)
    realigned = realignSecondaryPixels(grid, halo_grid)
    return pruneStragglers(grid, realigned)


p = solve_de809cff
