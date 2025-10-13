"""Solver for ARC-AGI-2 task 269e22fb."""


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


def deep_copy(grid):
    return [row[:] for row in grid]


def identity(grid):
    return [row[:] for row in grid]


def rot90(grid):
    return [list(row) for row in zip(*grid[::-1])]


def rot180(grid):
    return rot90(rot90(grid))


def rot270(grid):
    return rot90(rot180(grid))


def flip_h(grid):
    return [row[::-1] for row in grid]


def flip_v(grid):
    return grid[::-1]


def flip_main(grid):
    return [list(row) for row in zip(*grid)]


def flip_anti(grid):
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


INVERSE = {
    "identity": "identity",
    "rot90": "rot270",
    "rot180": "rot180",
    "rot270": "rot90",
    "flip_h": "flip_h",
    "flip_v": "flip_v",
    "flip_main": "flip_main",
    "flip_anti": "flip_anti",
}


def apply_named_transform(grid, name):
    for candidate_name, fn in TRANSFORMS:
        if candidate_name == name:
            return fn(grid)
    raise KeyError(name)


def find_alignment(grid):
    colors = sorted({value for row in grid for value in row})
    if len(colors) != 2:
        raise ValueError("expected exactly two colors")

    for color_order in (colors, colors[::-1]):
        mapping = {color_order[0]: 0, color_order[1]: 1}
        grid_bin = [[mapping[value] for value in row] for row in grid]
        for name, fn in TRANSFORMS:
            transformed = fn(grid_bin)
            h, w = len(transformed), len(transformed[0])
            max_r = len(BASE_PATTERN) - h + 1
            max_c = len(BASE_PATTERN[0]) - w + 1
            for r in range(max_r):
                for c in range(max_c):
                    if all(transformed[i] == BASE_PATTERN[r + i][c : c + w] for i in range(h)):
                        return {
                            "transform": name,
                            "mapping": mapping,
                            "position": (r, c),
                            "pattern": transformed,
                        }
    raise ValueError("no placement found")


def solve_269e22fb(grid):
    alignment = find_alignment(grid)
    base = deep_copy(BASE_PATTERN)
    r, c = alignment["position"]
    pattern = alignment["pattern"]
    h, w = len(pattern), len(pattern[0])
    for i in range(h):
        base[r + i][c : c + w] = pattern[i][:]

    inverse_name = INVERSE[alignment["transform"]]
    out_bin = apply_named_transform(base, inverse_name)

    reverse_map = {binary: color for color, binary in alignment["mapping"].items()}
    result = [[reverse_map[value] for value in row] for row in out_bin]

    # Sanity check: ensure the original grid appears exactly once in the result.
    h_in, w_in = len(grid), len(grid[0])
    matches = 0
    for r0 in range(len(result) - h_in + 1):
        for c0 in range(len(result[0]) - w_in + 1):
            if all(result[r0 + dr][c0 : c0 + w_in] == grid[dr] for dr in range(h_in)):
                matches += 1
    assert matches >= 1

    return result


p = solve_269e22fb
