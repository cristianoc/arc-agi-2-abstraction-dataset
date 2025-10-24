"""Solver for ARC task e376de54 (typed DSL wrapper).

This refactor preserves the original behaviour while exposing a small, typed
pipeline compatible with the dataset’s DSL subset. The main `solve_e376de54`
function matches the Lambda Representation in `abstractions.md` exactly.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Literal, Sequence, Tuple, Union

Grid = List[List[int]]
Color = int
Cell = Tuple[int, int, int]  # (row, col, color)
Orientation = Literal["row", "col", "diag1", "diag2"]
LineGroups = Dict[int, List[Cell]]

# Pattern encodes the median footprint; diagonals also carry the base key for translation.
RowPattern = Tuple[Literal["row"], List[int]]
ColPattern = Tuple[Literal["col"], List[int]]
Diag1Pattern = Tuple[Literal["diag1"], List[Tuple[int, int]], int]
Diag2Pattern = Tuple[Literal["diag2"], List[Tuple[int, int]], int]
Pattern = Union[RowPattern, ColPattern, Diag1Pattern, Diag2Pattern]


def _deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _flatten(grid: Grid) -> Iterable[int]:
    for row in grid:
        for value in row:
            yield value


def _orientation_key(name: Orientation, r: int, c: int) -> int:
    if name == "row":
        return r
    if name == "col":
        return c
    if name == "diag1":  # main diagonal (slope +1)
        return r - c
    if name == "diag2":  # anti-diagonal (slope -1)
        return r + c
    raise ValueError(name)


# === DSL helper operations ===

def collectColoredCells(grid: Grid) -> Tuple[Color, List[Cell]]:
    background = Counter(_flatten(grid)).most_common(1)[0][0]
    h, w = len(grid), len(grid[0])
    cells = [
        (r, c, grid[r][c])
        for r in range(h)
        for c in range(w)
        if grid[r][c] != background
    ]
    return background, cells


def scoreOrientations(coloured_cells: List[Cell]) -> Tuple[Orientation, LineGroups]:
    orientations: Sequence[Orientation] = ("row", "col", "diag1", "diag2")
    scored: Dict[Orientation, Tuple[int, int]] = {}
    grouped: Dict[Orientation, LineGroups] = {}

    for name in orientations:
        lines: LineGroups = defaultdict(list)
        for r, c, val in coloured_cells:
            lines[_orientation_key(name, r, c)].append((r, c, val))
        score = sum(len(group) - 1 for group in lines.values() if len(group) > 1)
        max_len = max((len(group) for group in lines.values()), default=0)
        scored[name] = (score, max_len)
        grouped[name] = lines

    best: Orientation = max(orientations, key=lambda nm: scored[nm])
    return best, grouped[best]


def extractMedianPattern(orientation: Orientation, line_groups: LineGroups) -> Pattern:
    if not line_groups:
        # Degenerate; return empty pattern per orientation.
        if orientation == "row":
            return ("row", [])
        if orientation == "col":
            return ("col", [])
        if orientation == "diag1":
            return ("diag1", [], 0)
        return ("diag2", [], 0)

    keys = sorted(line_groups)
    base_key = keys[len(keys) // 2]
    base_cells = line_groups[base_key]

    if orientation == "row":
        pattern: RowPattern = (
            "row",
            [c for _, c, _ in sorted(base_cells, key=lambda x: x[1])],
        )
        return pattern
    if orientation == "col":
        pattern2: ColPattern = (
            "col",
            [r for r, _, _ in sorted(base_cells, key=lambda x: x[0])],
        )
        return pattern2

    # For diagonals keep absolute coordinates plus the base key for translation.
    coords = [(r, c) for r, c, _ in sorted(base_cells, key=lambda x: x[0])]
    if orientation == "diag1":
        pattern3: Diag1Pattern = ("diag1", coords, base_key)
        return pattern3
    pattern4: Diag2Pattern = ("diag2", coords, base_key)
    return pattern4


def realignLines(grid: Grid, orientation: Orientation, pattern: Pattern) -> Grid:
    h, w = len(grid), len(grid[0])
    background = Counter(_flatten(grid)).most_common(1)[0][0]

    # Rebuild line groups from the current grid to obtain colours per line.
    _, coloured_cells = collectColoredCells(grid)
    _, line_groups = scoreOrientations(coloured_cells)
    keys = sorted(line_groups)

    result = _deep_copy(grid)

    for key in keys:
        group = line_groups[key]
        if not group:
            continue

        colour = Counter(v for _, _, v in group).most_common(1)[0][0]
        existing = {(r, c) for r, c, _ in group}

        if pattern[0] == "row":
            _, cols = pattern
            r = key
            target = {(r, c) for c in cols}
        elif pattern[0] == "col":
            _, rows = pattern
            c = key
            target = {(r, c) for r in rows}
        elif pattern[0] == "diag1":
            _, coords, base_key = pattern
            delta = key - base_key
            if delta % 2:
                delta -= (1 if delta > 0 else -1)
            shift = delta // 2
            target = {(r + shift, c - shift) for r, c in coords}
        else:  # diag2
            _, coords, base_key = pattern  # type: ignore[assignment]
            delta = key - base_key
            if delta % 2:
                delta -= (1 if delta > 0 else -1)
            shift = delta // 2
            target = {(r + shift, c + shift) for r, c in coords}

        target = {(r, c) for r, c in target if 0 <= r < h and 0 <= c < w}

        for r, c in existing - target:
            result[r][c] = background
        for r, c in target:
            result[r][c] = colour

    return result


# === Lambda Representation (must match abstractions.md) ===
def solve_e376de54(grid: Grid) -> Grid:
    _, coloured_cells = collectColoredCells(grid)
    orientation, line_groups = scoreOrientations(coloured_cells)
    pattern = extractMedianPattern(orientation, line_groups)
    return realignLines(grid, orientation, pattern)


p = solve_e376de54
