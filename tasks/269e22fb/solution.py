"""Solver for ARC-AGI-2 task 269e22fb.

Refactored to expose a DSL-style main that composes pure helpers while
preserving the original solver semantics.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, NamedTuple


BASE_PATTERN = [
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1],
    [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1],
    [1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1],
    [1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1],
    [0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0],
    [1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1],
    [0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1],
]


Grid = List[List[int]]
Mapping = Dict[int, int]


class Alignment(NamedTuple):
    transform: str
    mapping: Mapping  # original color -> binary {0,1}
    position: Tuple[int, int]
    pattern: Grid  # transformed binary grid (0/1)


def deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def identity(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def rot90(grid: Grid) -> Grid:
    return [list(row) for row in zip(*grid[::-1])]


def rot180(grid: Grid) -> Grid:
    return rot90(rot90(grid))


def rot270(grid: Grid) -> Grid:
    return rot90(rot180(grid))


def flip_h(grid: Grid) -> Grid:
    return [row[::-1] for row in grid]


def flip_v(grid: Grid) -> Grid:
    return grid[::-1]


def flip_main(grid: Grid) -> Grid:
    return [list(row) for row in zip(*grid)]


def flip_anti(grid: Grid) -> Grid:
    h = len(grid)
    w = len(grid[0])
    return [[grid[h - 1 - c][w - 1 - r] for c in range(h)] for r in range(w)]


TRANSFORMS = [
    ("identity", identity),
    ("rot90", rot90),
    ("rot180", rot180),
    ("rot270", rot270),
    ("flip_h", flip_h),
    ("flip_v", flip_v),
    ("flip_main", flip_main),
    ("flip_anti", flip_anti),
]


INVERSE: Dict[str, str] = {
    "identity": "identity",
    "rot90": "rot270",
    "rot180": "rot180",
    "rot270": "rot90",
    "flip_h": "flip_h",
    "flip_v": "flip_v",
    "flip_main": "flip_main",
    "flip_anti": "flip_anti",
}


def apply_named_transform(grid: Grid, name: str) -> Grid:
    for candidate_name, fn in TRANSFORMS:
        if candidate_name == name:
            return fn(grid)
    raise KeyError(name)

def _map_colors(grid: Grid, mapping: Mapping) -> Grid:
    return [[mapping[v] for v in row] for row in grid]


def findAlignment(grid: Grid) -> Alignment:
    """Find dihedral transform, color mapping, and placement into BASE_PATTERN.

    Returns an Alignment that captures:
      - transform: name of the dihedral transform that aligns the input
      - mapping: original->binary color mapping (to {0,1})
      - position: top-left insertion coordinates within BASE_PATTERN
      - pattern: transformed binary grid
    """
    colors = sorted({value for row in grid for value in row})
    if len(colors) != 2:
        raise ValueError("expected exactly two colors")

    for color_order in (colors, colors[::-1]):
        mapping: Mapping = {color_order[0]: 0, color_order[1]: 1}
        grid_bin = _map_colors(grid, mapping)
        for name, fn in TRANSFORMS:
            transformed = fn(grid_bin)
            h, w = len(transformed), len(transformed[0])
            max_r = len(BASE_PATTERN) - h + 1
            max_c = len(BASE_PATTERN[0]) - w + 1
            for r in range(max_r):
                for c in range(max_c):
                    if all(transformed[i] == BASE_PATTERN[r + i][c : c + w] for i in range(h)):
                        return Alignment(
                            transform=name,
                            mapping=mapping,
                            position=(r, c),
                            pattern=transformed,
                        )
    raise ValueError("no placement found")


def writeTemplate(alignment: Alignment) -> Grid:
    base = deep_copy(BASE_PATTERN)
    r, c = alignment.position
    pattern = alignment.pattern
    h, w = len(pattern), len(pattern[0])
    for i in range(h):
        base[r + i][c : c + w] = pattern[i][:]
    return base


def invertTransform(alignment: Alignment, template: Grid) -> Grid:
    inverse_name = INVERSE[alignment.transform]
    return apply_named_transform(template, inverse_name)


def remapColors(inverted: Grid, mapping: Mapping) -> Grid:
    reverse_map: Mapping = {b: a for a, b in mapping.items()}
    return [[reverse_map[v] for v in row] for row in inverted]


def solve_269e22fb(grid: Grid) -> Grid:
    alignment = findAlignment(grid)
    template = writeTemplate(alignment)
    inverted = invertTransform(alignment, template)
    return remapColors(inverted, alignment.mapping)


p = solve_269e22fb
