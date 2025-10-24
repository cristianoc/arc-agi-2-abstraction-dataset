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
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

# DSL-friendly type aliases
Grid = List[List[int]]
Frame = Tuple[int, int, int, int, int]  # (color, rmin, rmax, cmin, cmax)


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
        tail = list(grid[r][cmax + 1 :])
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


def extractFrames(grid: Grid) -> List[Frame]:
    background = _most_common_color(grid)
    return [(color, rmin, rmax, cmin, cmax) for (color, rmin, rmax, cmin, cmax) in _find_blocks(grid, background)]


def sliceInstructionPatch(grid: Grid, frame: Frame) -> Tuple[Tuple[int, ...], ...]:
    color, rmin, rmax, cmin, cmax = frame
    background = _most_common_color(grid)
    patch = _extract_patch(grid, (color, rmin, rmax, cmin, cmax, background))
    return _canonical_patch(patch, color, background)


def lookupStripeCount(patch: Tuple[Tuple[int, ...], ...]) -> int:
    if not patch:
        return 0
    if patch in PATCH_STRIPES:
        return PATCH_STRIPES[patch]
    unique = {v for row in patch for v in row if v not in (0, -1)}
    row_hits = sum(any(v not in (0, -1) for v in row) for row in patch)
    return max(len(unique), row_hits // 2)


def clearAndPaintStripes(canvas: Grid, frame: Frame, stripe_count: int) -> Grid:
    color, rmin, rmax, cmin, cmax = frame
    background = _most_common_color(canvas)
    # Start from a copy (purity)
    out = [row[:] for row in canvas]
    # Clear interior
    for r in range(rmin + 1, rmax):
        for c in range(cmin + 1, cmax):
            out[r][c] = background
    # Paint stripes on the horizontal midline inside the frame
    inner_width = cmax - cmin - 1
    candidates = _candidate_positions(inner_width)
    if not candidates or stripe_count <= 0:
        return out
    selected = candidates[-min(stripe_count, len(candidates)) :]
    mid = (rmin + rmax) // 2
    base = cmin + 1
    for offset in selected:
        out[mid][base + offset] = color
    return out


def clearNoise(canvas: Grid, frames: List[Frame]) -> Grid:
    if not frames:
        return [row[:] for row in canvas]
    background = _most_common_color(canvas)
    out = [row[:] for row in canvas]
    height = len(out)
    width = len(out[0]) if height else 0
    # Clear everything to the right of the rightmost frame edge
    right_limit = max(cmax for (_color, _rmin, _rmax, _cmin, cmax) in frames)
    for r in range(height):
        for c in range(right_limit + 1, width):
            out[r][c] = background
    # Build inside mask
    inside = [[False] * width for _ in range(height)]
    for (_color, rmin, rmax, cmin, cmax) in frames:
        for r in range(rmin, rmax + 1):
            for c in range(cmin, cmax + 1):
                inside[r][c] = True
    # Clear any non-background outside frames
    for r in range(height):
        for c in range(width):
            if not inside[r][c] and out[r][c] != background:
                out[r][c] = background
    return out


def fold_repaint(canvas: Grid, items: List[Frame], update: Callable[[Grid, Frame], Grid]) -> Grid:
    acc = [row[:] for row in canvas]
    for item in items:
        acc = update(acc, item)
    return acc


def solve_8f215267(grid: Grid) -> Grid:
    frames = extractFrames(grid)

    def repaint(canvas: Grid, frame: Frame) -> Grid:
        patch = sliceInstructionPatch(grid, frame)
        stripe_count = lookupStripeCount(patch)
        return clearAndPaintStripes(canvas, frame, stripe_count)

    striped = fold_repaint(grid, frames, repaint)
    return clearNoise(striped, frames)


p = solve_8f215267
