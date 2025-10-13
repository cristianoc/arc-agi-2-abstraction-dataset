"""Solver for ARC-AGI-2 task db695cfb (split: evaluation)."""

from collections import defaultdict


def _fill_nwse_path(grid, output, coords, six_seeds):
    """Fill the NW-SE diagonal segment defined by coords with color 1."""
    key = coords[0][0] - coords[0][1]  # r - c stays constant on NW-SE diagonals
    rows = [r for r, _ in coords]
    r_min, r_max = min(rows), max(rows)
    width = len(grid[0])
    for r in range(r_min, r_max + 1):
        c = r - key
        if not (0 <= c < width):
            continue
        if grid[r][c] != 6:
            output[r][c] = 1
        if grid[r][c] == 6:
            six_seeds['anti'].add((r, c))  # need NE-SW fill through this seed


def _fill_nesw_path(grid, output, coords, six_seeds):
    """Fill the NE-SW diagonal segment defined by coords with color 1."""
    key = coords[0][0] + coords[0][1]  # r + c stays constant on NE-SW diagonals
    rows = [r for r, _ in coords]
    r_min, r_max = min(rows), max(rows)
    width = len(grid[0])
    for r in range(r_min, r_max + 1):
        c = key - r
        if not (0 <= c < width):
            continue
        if grid[r][c] != 6:
            output[r][c] = 1
        if grid[r][c] == 6:
            six_seeds['main'].add((r, c))  # need NW-SE fill through this seed


def _fill_diag(output, seed, orientation):
    """Paint color 6 along a full diagonal passing through the seed."""
    height, width = len(output), len(output[0])
    r0, c0 = seed
    if orientation == 'anti':  # NE-SW diagonal (constant r + c)
        diag_sum = r0 + c0
        for r in range(height):
            c = diag_sum - r
            if 0 <= c < width:
                if output[r][c] == 1 and (r, c) != seed:
                    continue
                output[r][c] = 6
    else:  # 'main' -> NW-SE diagonal (constant r - c)
        diff = r0 - c0
        for r in range(height):
            c = r - diff
            if 0 <= c < width:
                if output[r][c] == 1 and (r, c) != seed:
                    continue
                output[r][c] = 6


def solve_db695cfb(grid):
    """Connect 1s diagonally and extend perpendicular diagonals from embedded 6s."""
    if not grid:
        return []

    height, width = len(grid), len(grid[0])
    output = [row[:] for row in grid]

    ones = [(r, c) for r in range(height) for c in range(width) if grid[r][c] == 1]

    # No work to do if we lack enough anchors.
    if len(ones) < 2:
        return output

    six_seeds = {'anti': set(), 'main': set()}

    # Group 1s by both diagonal orientations.
    groups_nwse = defaultdict(list)
    groups_nesw = defaultdict(list)
    for r, c in ones:
        groups_nwse[r - c].append((r, c))
        groups_nesw[r + c].append((r, c))

    for coords in groups_nwse.values():
        if len(coords) >= 2:
            _fill_nwse_path(grid, output, coords, six_seeds)

    for coords in groups_nesw.values():
        if len(coords) >= 2:
            _fill_nesw_path(grid, output, coords, six_seeds)

    # Extend diagonals of 6s perpendicular to the 1-paths.
    for orientation, seeds in six_seeds.items():
        for seed in seeds:
            _fill_diag(output, seed, orientation)

    return output


p = solve_db695cfb
