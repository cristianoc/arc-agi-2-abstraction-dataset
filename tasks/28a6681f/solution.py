"""Solver for ARC-AGI-2 task 28a6681f (split: evaluation)."""


def solve_28a6681f(grid):
    """Relocate color-1 cells into horizontal gaps bounded by non-zero colors."""

    height = len(grid)
    width = len(grid[0]) if height else 0

    # Copy so we do not mutate the input grid.
    result = [row[:] for row in grid]

    # Supply of existing 1-cells (sorted top-to-bottom, left-to-right).
    supply = sorted(
        (r, c) for r in range(height) for c in range(width) if grid[r][c] == 1
    )

    # Zero cells that lie between two non-zero cells in the same row.
    candidates = []
    for r, row in enumerate(grid):
        c = 0
        while c < width:
            if row[c] != 0:
                c += 1
                continue

            start = c
            while c < width and row[c] == 0:
                c += 1
            end = c - 1

            left_color = row[start - 1] if start > 0 else 0
            right_color = row[end + 1] if end + 1 < width else 0
            if left_color != 0 and right_color != 0:
                for cc in range(start, end + 1):
                    candidates.append((r, cc))

    # Prefer filling from the bottom-right candidates first.
    candidates.sort(key=lambda rc: (-rc[0], -rc[1]))

    removed = []
    for r, c in candidates:
        if not supply:
            break
        if supply[0][0] <= r:
            removed.append(supply.pop(0))
            result[r][c] = 1

    for r, c in removed:
        result[r][c] = 0

    return result


p = solve_28a6681f
