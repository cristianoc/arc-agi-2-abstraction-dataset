"""Solver for ARC task e376de54.

The transformation aligns families of coloured lines so that every member
shares the same footprint as the middle line in that family.  A "line" here
means a row, column, or diagonal (either slope) containing non-background
cells.  We detect the dominant orientation by scoring how well the coloured
cells cluster along each of the four candidate directions.  The direction that
produces the strongest clustering supplies the line family for the task.

Once the orientation is fixed, we identify the median line (by index within the
family) and treat its coloured footprint as the canonical pattern.  Every other
line is then rebuilt so that it matches this pattern after translating it onto
the line.  Cells that fall outside the pattern are cleared back to background.
This behaviour matches the three training demonstrations (diagonal, row, and
column alignment) and captures the intended regularisation for the evaluation
grid.
"""

from collections import Counter, defaultdict


def _deep_copy(grid):
    return [row[:] for row in grid]


def _flatten(grid):
    for row in grid:
        for value in row:
            yield value


def _orientation_key(name, r, c):
    if name == "row":
        return r
    if name == "col":
        return c
    if name == "diag1":  # main diagonal (slope +1)
        return r - c
    if name == "diag2":  # anti-diagonal (slope -1)
        return r + c
    raise ValueError(name)


def solve_e376de54(grid):
    """Regularise coloured lines so they share a canonical footprint."""

    height, width = len(grid), len(grid[0])
    background = Counter(_flatten(grid)).most_common(1)[0][0]

    cells = [(r, c, grid[r][c])
             for r in range(height)
             for c in range(width)
             if grid[r][c] != background]

    if not cells:
        return _deep_copy(grid)

    orientations = ("row", "col", "diag1", "diag2")
    scored_lines = {}
    lines_by_orientation = {}

    for name in orientations:
        lines = defaultdict(list)
        for r, c, val in cells:
            lines[_orientation_key(name, r, c)].append((r, c, val))
        score = sum(len(group) - 1 for group in lines.values() if len(group) > 1)
        max_len = max((len(group) for group in lines.values()), default=0)
        scored_lines[name] = (score, max_len)
        lines_by_orientation[name] = lines

    orientation = max(orientations, key=lambda name: scored_lines[name])
    lines = lines_by_orientation[orientation]
    if not lines:
        return _deep_copy(grid)

    keys = sorted(lines)
    base_key = keys[len(keys) // 2]
    base_cells = lines[base_key]

    if orientation == "row":
        base_pattern = [c for _, c, _ in sorted(base_cells, key=lambda item: item[1])]
    elif orientation == "col":
        base_pattern = [r for r, _, _ in sorted(base_cells, key=lambda item: item[0])]
    else:  # diagonal orientations keep full coordinate pairs for translation
        base_pattern = [(r, c) for r, c, _ in sorted(base_cells, key=lambda item: item[0])]

    result = _deep_copy(grid)

    for key in keys:
        group = lines[key]
        if not group:
            continue

        colour = Counter(value for _, _, value in group).most_common(1)[0][0]
        existing = {(r, c) for r, c, _ in group}

        if orientation == "row":
            r = key
            target = {(r, c) for c in base_pattern}
        elif orientation == "col":
            c = key
            target = {(r, c) for r in base_pattern}
        elif orientation == "diag1":
            delta = key - base_key
            if delta % 2:
                delta -= (1 if delta > 0 else -1)
            shift = delta // 2
            target = {(r + shift, c - shift) for r, c in base_pattern}
        else:  # diag2
            delta = key - base_key
            if delta % 2:
                delta -= (1 if delta > 0 else -1)
            shift = delta // 2
            target = {(r + shift, c + shift) for r, c in base_pattern}

        target = {(r, c) for r, c in target if 0 <= r < height and 0 <= c < width}

        for r, c in existing - target:
            result[r][c] = background
        for r, c in target:
            result[r][c] = colour

    return result


p = solve_e376de54
