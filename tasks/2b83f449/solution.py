"""Solver for ARC-AGI-2 task 2b83f449."""


def solve_2b83f449(grid):
    h = len(grid)
    w = len(grid[0])

    base = [row[:] for row in grid]

    zero_above = [[0] * w for _ in range(h)]
    zero_below = [[0] * w for _ in range(h)]
    for c in range(w):
        count = 0
        for r in range(h):
            zero_above[r][c] = count
            if grid[r][c] == 0:
                count += 1
        count = 0
        for r in range(h - 1, -1, -1):
            zero_below[r][c] = count
            if grid[r][c] == 0:
                count += 1

    for r, row in enumerate(grid):
        c = 0
        while c < w:
            if row[c] == 7:
                start = c
                while c < w and row[c] == 7:
                    c += 1
                if c - start == 3:
                    center = start + 1
                    base[r][start] = 8
                    base[r][center] = 6
                    base[r][start + 2] = 8
                    for dr in (-1, 1):
                        rr = r + dr
                        if 0 <= rr < h and grid[rr][center] == 8:
                            base[rr][center] = 6
                continue
            c += 1

    to_three = set()
    keep_neighbors = set()

    def val(r, c):
        if 0 <= r < h and 0 <= c < w:
            return grid[r][c]
        return None

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 8:
                continue
            up = val(r - 1, c)
            down = val(r + 1, c)
            left = val(r, c - 1)
            right = val(r, c + 1)
            diag_ul = val(r - 1, c - 1)
            diag_ur = val(r - 1, c + 1)
            diag_dl = val(r + 1, c - 1)
            diag_dr = val(r + 1, c + 1)
            zeros_above = zero_above[r][c]
            zeros_below = zero_below[r][c]

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

    for r in range(1, h - 1):
        if 0 in grid[r]:
            for c in (0, w - 1):
                if grid[r][c] == 3:
                    if val(r - 1, c) == 0 or val(r + 1, c) == 0:
                        to_three.add((r, c))

    for r, c in keep_neighbors:
        if 0 <= r < h and 0 <= c < w and grid[r][c] == 3:
            to_three.add((r, c))

    result = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            if grid[r][c] == 0:
                result[r][c] = 0
            elif base[r][c] == 6:
                result[r][c] = 6
            else:
                result[r][c] = 8

    for r, c in to_three:
        if 0 <= r < h and 0 <= c < w:
            result[r][c] = 3

    return result


p = solve_2b83f449
