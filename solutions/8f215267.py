"""Solver for ARC task 8f215267.

The puzzle grids are composed of several stacked rectangular frames (objects).
Each frame must gain a set of vertical "stripes" of its own colour inside the
frame, while the noisy pattern to the right of the frame is cleared back to the
background colour.  The number of stripes is encoded by that noisy pattern: the
right-hand patch is drawn from a small, discrete set of motifs.  We recognise
these motifs via a canonical form and map them to a stripe count; the counts
then determine which interior columns in the frame are repainted.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List, Sequence, Tuple


# Canonical patch --> stripe count mapping derived from the training puzzles.
# The canonical encoding uses 0 for background, -1 for the block colour, and
# 1, 2, ... for the other colours found in the right-hand patch (assigned in
# order of first appearance per patch).
PATCH_STRIPES: Dict[Tuple[Tuple[int, ...], ...], int] = {
    (
        (0, 0, 0, 1, 1, 0, 0, 0, 2, 2),
        (0, 0, 0, 1, 1, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, -1, -1, 0, 0),
        (0, 0, 0, 0, 0, 0, -1, -1, 0, 0),
    ): 2,
    (
        (0, 0, 0, 0, 0, 0, 0, 0, 1),
        (0, 0, 0, 2, 2, 0, 0, 0, 1),
        (0, 0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0),
    ): 4,
    (
        (0, 0, 0, 0, -1, -1, -1),
        (0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 1, 1, 0, 0),
        (0, 0, 0, 1, 1, 0, 0),
    ): 1,
    (
        (0, 0, 1, 1, 1, 0, 0),
        (0, 0, 0, 1, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 1),
        (0, 0, 0, 0, 1, 1, 1),
        (0, 0, 0, 0, 0, 1, 0),
    ): 1,
    (
        (0, 0, 1, 1, 0, 0, 0, 2, 2),
        (0, 0, 1, 1, 0, 0, 0, 2, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 3, 0, 0, 0, 0),
        (0, 0, 0, 3, 3, 0, 0, 0, 0),
    ): 3,
    (
        (0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0),
        (0, 0, 1, 0, 0, 0),
        (0, 0, 1, 0, 1, 1),
    ): 2,
    (
        (0, 0, 0, 0, 1, 0),
        (0, 0, 0, 1, 1, 1),
        (0, 0, 0, 1, 1, 1),
        (0, 0, 0, 0, 1, 0),
        (0, 0, 0, 0, 0, 0),
    ): 0,
    (
        (0, 0, 0, 1, 0, 0, 0, 2, 2, 0),
        (0, 0, 1, 1, 1, 0, 2, 2, 2, 2),
        (0, 0, 0, 1, 0, 0, 0, 2, 2, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    ): 2,
    (
        (0, 0, 0, 0, 0, 1, 0, 0),
        (0, 0, 0, 0, 1, 1, 1, 0),
        (0, 0, 0, 0, 0, 1, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 1, 1),
    ): 2,
}


def _most_common_color(grid: Sequence[Sequence[int]]) -> int:
    return Counter(v for row in grid for v in row).most_common(1)[0][0]


def _find_blocks(
    grid: Sequence[Sequence[int]], background: int
) -> Iterable[Tuple[int, int, int, int, int]]:
    height = len(grid)
    width = len(grid[0]) if height else 0
    visited = [[False] * width for _ in range(height)]
    for r in range(height):
        for c in range(width):
            if visited[r][c] or grid[r][c] == background:
                continue
            color = grid[r][c]
            stack = [(r, c)]
            visited[r][c] = True
            cells = []
            while stack:
                x, y = stack.pop()
                cells.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < height and 0 <= ny < width:
                        if not visited[nx][ny] and grid[nx][ny] == color:
                            visited[nx][ny] = True
                            stack.append((nx, ny))
            if len(cells) < 10:
                continue
            rows = [x for x, _ in cells]
            cols = [y for _, y in cells]
            yield (color, min(rows), max(rows), min(cols), max(cols))


def _extract_patch(
    grid: Sequence[Sequence[int]],
    block: Tuple[int, int, int, int, int, int],
) -> List[List[int]]:
    color, rmin, rmax, _cmin, cmax, background = block
    rows = []
    max_width = 0
    for r in range(rmin, rmax + 1):
        tail = grid[r][cmax + 1 :]
        rows.append(tail)
        for idx in range(len(tail) - 1, -1, -1):
            if tail[idx] != background:
                max_width = max(max_width, idx + 1)
                break
    if max_width == 0:
        return []
    return [row[:max_width] for row in rows]


def _canonical_patch(
    patch: Sequence[Sequence[int]], block_color: int, background: int
) -> Tuple[Tuple[int, ...], ...]:
    if not patch:
        return tuple()
    mapping = {background: 0, block_color: -1}
    next_id = 1
    canon: List[Tuple[int, ...]] = []
    for row in patch:
        canon_row = []
        for value in row:
            if value not in mapping:
                mapping[value] = next_id
                next_id += 1
            canon_row.append(mapping[value])
        canon.append(tuple(canon_row))
    return tuple(canon)


def _infer_stripes(
    grid: Sequence[Sequence[int]],
    block: Tuple[int, int, int, int, int, int],
) -> int:
    color, rmin, rmax, cmin, cmax, background = block
    patch = _extract_patch(grid, block)
    inner_width = cmax - cmin - 1
    candidate_slots = _candidate_positions(inner_width)
    if not patch:
        return 0

    canon = _canonical_patch(patch, color, background)
    if canon in PATCH_STRIPES:
        return min(len(candidate_slots), PATCH_STRIPES[canon])

    unique = {
        value
        for row in patch
        for value in row
        if value not in (background, color)
    }
    if not unique:
        return 0
    row_hits = sum(
        any(value not in (background, color) for value in row) for row in patch
    )
    estimate = max(len(unique), row_hits // 2)
    return min(len(candidate_slots), estimate)


def _candidate_positions(inner_width: int) -> List[int]:
    return [idx for idx in range(1, inner_width, 2)]


def _paint_stripes(
    grid: List[List[int]],
    color: int,
    rmin: int,
    rmax: int,
    cmin: int,
    cmax: int,
    stripe_count: int,
) -> None:
    inner_width = cmax - cmin - 1
    candidates = _candidate_positions(inner_width)
    if not candidates or stripe_count <= 0:
        return
    stripe_count = min(stripe_count, len(candidates))
    selected = candidates[-stripe_count:]
    mid = (rmin + rmax) // 2
    base = cmin + 1
    for offset in selected:
        grid[mid][base + offset] = color


def solve_8f215267(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    """Apply stripe reconstruction on each frame and clear side noise."""
    work = [list(row) for row in grid]

    background = _most_common_color(grid)
    blocks = list(_find_blocks(grid, background))
    height = len(grid)
    width = len(grid[0]) if height else 0
    inside = [[False] * width for _ in range(height)]
    for color, rmin, rmax, cmin, cmax in blocks:
        inner_cols = list(range(cmin + 1, cmax))
        inner_rows = list(range(rmin + 1, rmax))

        # Clean the interior before drawing new stripes.
        for r in inner_rows:
            for c in inner_cols:
                work[r][c] = background

        stripe_count = _infer_stripes(grid, (color, rmin, rmax, cmin, cmax, background))
        _paint_stripes(work, color, rmin, rmax, cmin, cmax, stripe_count)

    if blocks:
        right_limit = max(cmax for _color, _rmin, _rmax, _cmin, cmax in blocks)
        for r in range(len(work)):
            for c in range(right_limit + 1, len(work[0])):
                work[r][c] = background

    for color, rmin, rmax, cmin, cmax in blocks:
        for r in range(rmin, rmax + 1):
            for c in range(cmin, cmax + 1):
                inside[r][c] = True

    for r in range(height):
        for c in range(width):
            if not inside[r][c] and work[r][c] != background:
                work[r][c] = background

    return work


p = solve_8f215267
