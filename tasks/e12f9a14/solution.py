"""Auto-generated identity stub for ARC-AGI-2 task e12f9a14 (split: evaluation)."""

from collections import Counter

# TODO: refine transformation logic iteratively; start by characterising failures.


DIGIT_TEMPLATE_VARIANTS = {
    1: (
        (
            (-10, -3),
            (-10, 8),
            (-9, -3),
            (-9, 7),
            (-8, -3),
            (-8, 7),
            (-7, -3),
            (-7, 6),
            (-6, -3),
            (-6, 6),
            (-5, -3),
            (-5, 5),
            (-4, -3),
            (-4, 5),
            (-3, -3),
            (-3, 4),
            (-2, -2),
            (-2, 3),
            (-1, -1),
            (-1, 2),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
            (2, -1),
            (2, 2),
            (3, -2),
            (3, 3),
            (4, -3),
            (4, 4),
            (5, -3),
            (5, 5),
            (6, -3),
            (6, 5),
            (7, -3),
            (7, 6),
            (8, -3),
            (8, 6),
            (9, -3),
            (9, 7),
            (10, -2),
            (10, 7),
            (11, -1),
            (11, 8),
            (12, 0),
            (12, 8),
            (13, 1),
            (13, 9),
        ),
    ),
    2: (
        (
            (-6, 14),
            (-5, 13),
            (-4, 12),
            (-3, 11),
            (-2, 10),
            (-1, 9),
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (0, 6),
            (0, 7),
            (0, 8),
            (1, -4),
            (1, -3),
            (1, -2),
            (1, -1),
            (1, 0),
            (1, 1),
        ),
    ),
    4: (
        (
            (-10, 3),
            (-9, 2),
            (-8, 2),
            (-7, 1),
            (-6, 1),
            (-5, 0),
            (-4, 0),
            (-3, 0),
            (-2, 0),
            (-1, 0),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
            (2, 0),
            (3, 0),
            (4, 0),
            (5, 0),
            (6, 0),
            (7, 1),
            (8, 1),
            (9, 2),
            (10, 2),
            (11, 3),
            (12, 3),
            (13, 4),
        ),
        (
            (-10, 7),
            (-9, 6),
            (-8, 5),
            (-7, 4),
            (-6, 3),
            (-5, 2),
            (-4, 1),
            (-3, 1),
            (-2, 1),
            (-1, 1),
            (0, -12),
            (0, -11),
            (0, -10),
            (0, -9),
            (0, -8),
            (0, -7),
            (0, -6),
            (0, -5),
            (0, -4),
            (0, -3),
            (0, -2),
            (0, -1),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
        ),
        (
            (-3, 1),
            (-2, 1),
            (-1, 1),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 5),
            (2, -1),
            (3, -2),
        ),
    ),
    6: (
        (
            (-3, 0),
            (-3, 4),
            (-2, 0),
            (-2, 3),
            (-1, 0),
            (-1, 2),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
            (2, -1),
            (3, -2),
        ),
        (
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (1, 0),
            (1, 1),
            (1, 6),
            (2, 7),
            (3, 8),
        ),
    ),
    7: (
        (
            (0, -6),
            (0, -5),
            (0, -4),
            (0, -3),
            (0, -2),
            (0, -1),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
        ),
    ),
    9: (
        (
            (-10, 4),
            (-9, 4),
            (-8, 4),
            (-7, 4),
            (-6, 4),
            (-5, 4),
            (-4, -4),
            (-4, 4),
            (-3, -3),
            (-3, 4),
            (-2, -2),
            (-2, 3),
            (-1, -1),
            (-1, 2),
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
            (2, -1),
            (2, 2),
            (3, -2),
            (3, 3),
            (4, -3),
            (4, 4),
            (5, -4),
            (5, 4),
            (6, 4),
            (7, 4),
            (8, 4),
            (9, 4),
            (10, 5),
            (11, 6),
            (12, 7),
            (13, 8),
        ),
    ),
}


def _clone(grid):
    return [row[:] for row in grid]


# Helper routines ---------------------------------------------------------


def _dominant_color(grid):
    counter = Counter()
    for row in grid:
        counter.update(row)
    return counter.most_common(1)[0][0]


def _components(grid):
    height = len(grid)
    width = len(grid[0])
    seen = [[False] * width for _ in range(height)]
    for r in range(height):
        for c in range(width):
            if seen[r][c]:
                continue
            color = grid[r][c]
            stack = [(r, c)]
            seen[r][c] = True
            cells = []
            while stack:
                rr, cc = stack.pop()
                cells.append((rr, cc))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not seen[nr][nc] and grid[nr][nc] == color:
                        seen[nr][nc] = True
                        stack.append((nr, nc))
            yield color, cells


def solve_e12f9a14(grid):
    """Expand 2x2 seeds into stylised digits while preserving other structure."""

    height = len(grid)
    width = len(grid[0])
    result = _clone(grid)
    background = _dominant_color(grid)

    for color, cells in _components(grid):
        if color == background or len(cells) != 4:
            continue

        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        if max(rows) - min(rows) != 1 or max(cols) - min(cols) != 1:
            continue  # Not a 2x2 block.

        variants = DIGIT_TEMPLATE_VARIANTS.get(color)
        if not variants:
            continue  # Unknown seed colour; leave untouched.

        anchor_r, anchor_c = min(rows), min(cols)
        seed_cells = set(cells)
        best_cells = None

        for offsets in variants:
            placements = set()
            collision = False
            for dr, dc in offsets:
                target_r = anchor_r + dr
                target_c = anchor_c + dc
                if not (0 <= target_r < height and 0 <= target_c < width):
                    continue
                if (target_r, target_c) not in seed_cells and grid[target_r][target_c] != background:
                    collision = True
                    break
                placements.add((target_r, target_c))

            if collision:
                continue

            if best_cells is None or len(placements) > len(best_cells):
                best_cells = placements

        if not best_cells:
            continue

        for cell in best_cells.union(seed_cells):
            r, c = cell
            result[r][c] = color

    return result


p = solve_e12f9a14
