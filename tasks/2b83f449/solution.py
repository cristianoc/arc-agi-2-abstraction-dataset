"""Solver for ARC-AGI-2 task 2b83f449, refactored to DSL-style pipeline."""

from typing import List, Tuple, Set, Optional

Grid = List[List[int]]
Cell = Tuple[int, int]
Matrix = List[List[int]]


def precomputeZeroDistances(grid: Grid) -> Tuple[Matrix, Matrix]:
    h = len(grid)
    w = len(grid[0])
    above: Matrix = [[0] * w for _ in range(h)]
    below: Matrix = [[0] * w for _ in range(h)]
    for c in range(w):
        cnt = 0
        for r in range(h):
            above[r][c] = cnt
            if grid[r][c] == 0:
                cnt += 1
        cnt = 0
        for r in range(h - 1, -1, -1):
            below[r][c] = cnt
            if grid[r][c] == 0:
                cnt += 1
    return above, below


def paintCrossRuns(grid: Grid) -> Grid:
    h = len(grid)
    w = len(grid[0])
    res = [row[:] for row in grid]
    for r, row in enumerate(grid):
        c = 0
        while c < w:
            if row[c] == 7:
                start = c
                while c < w and row[c] == 7:
                    c += 1
                if c - start == 3:
                    center = start + 1
                    res[r][start] = 8
                    res[r][center] = 6
                    res[r][start + 2] = 8
                    for dr in (-1, 1):
                        rr = r + dr
                        if 0 <= rr < h and grid[rr][center] == 8:
                            res[rr][center] = 6
                continue
            c += 1
    return res


def _val(grid: Grid, r: int, c: int) -> Optional[int]:
    h = len(grid)
    w = len(grid[0])
    if 0 <= r < h and 0 <= c < w:
        return grid[r][c]
    return None


def collectBoundaryCells(grid: Grid, distances: Tuple[Matrix, Matrix]) -> Set[Cell]:
    h = len(grid)
    w = len(grid[0])
    above, below = distances

    to_three: Set[Cell] = set()
    keep_neighbors: Set[Cell] = set()

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 8:
                continue
            up = _val(grid, r - 1, c)
            down = _val(grid, r + 1, c)
            left = _val(grid, r, c - 1)
            right = _val(grid, r, c + 1)
            diag_ul = _val(grid, r - 1, c - 1)
            diag_ur = _val(grid, r - 1, c + 1)
            diag_dl = _val(grid, r + 1, c - 1)
            diag_dr = _val(grid, r + 1, c + 1)
            zeros_above = above[r][c]
            zeros_below = below[r][c]

            if up == 0 and down == 0 and right == 0 and left == 8:
                to_three.add((r, c))
                keep_neighbors.add((r, c + 1))
                continue

            if up == 0 and down == 0 and left == 3 and right == 8 and diag_ur == 7 and diag_dr == 0:
                to_three.add((r, c))
                keep_neighbors.add((r, c - 1))
                continue

            if up == 0 and down == 0 and left == 8 and right == 3 and diag_ul == 7 and diag_dl == 0:
                to_three.add((r, c))
                keep_neighbors.add((r, c + 1))
                continue

            if (
                up == 0
                and down == 0
                and left == 3
                and right == 8
                and diag_ul == 0
                and diag_ur == 0
                and diag_dl == 0
                and diag_dr == 0
                and zeros_above == 1
            ):
                to_three.add((r, c))
                keep_neighbors.add((r, c - 1))
                continue

            if (
                up == 0
                and down == 0
                and left == 8
                and right == 3
                and diag_ul == 0
                and diag_ur == 0
                and diag_dl == 0
                and diag_dr == 0
                and zeros_below == 1
                and zeros_above <= 4
            ):
                to_three.add((r, c))
                keep_neighbors.add((r, c + 1))
                continue

            if down is None and up == 0 and left == 0 and right == 8:
                to_three.add((r, c))
                keep_neighbors.add((r, c - 1))
                continue

            if down is None and up == 0 and right is None and left == 8:
                to_three.add((r, c))
                keep_neighbors.add((r, c - 1))
                continue

            if (
                down is None
                and up == 0
                and left is None
                and right == 8
                and zeros_above <= 5
            ):
                to_three.add((r, c))
                keep_neighbors.add((r, c + 1))
                continue

    # Edge-adjacent 3s when a row contains zero(s)
    for r in range(1, h - 1):
        if 0 in grid[r]:
            for c in (0, w - 1):
                if grid[r][c] == 3:
                    if _val(grid, r - 1, c) == 0 or _val(grid, r + 1, c) == 0:
                        to_three.add((r, c))

    # Promote neighbor 3s that must be kept
    for (nr, nc) in keep_neighbors:
        if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 3:
            to_three.add((nr, nc))

    return to_three


def applyBoundaryRecolor(grid: Grid, cross_painted: Grid, boundary_cells: Set[Cell]) -> Grid:
    h = len(grid)
    w = len(grid[0])
    result: Grid = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 0:
                result[r][c] = 0
            elif cross_painted[r][c] == 6:
                result[r][c] = 6
            else:
                result[r][c] = 8

    for (r, c) in boundary_cells:
        if 0 <= r < h and 0 <= c < w:
            result[r][c] = 3
    return result


def solve_2b83f449(grid: Grid) -> Grid:
    distances = precomputeZeroDistances(grid)
    cross_painted = paintCrossRuns(grid)
    boundary_cells = collectBoundaryCells(grid, distances)
    return applyBoundaryRecolor(grid, cross_painted, boundary_cells)


p = solve_2b83f449
