"""Solver for ARC-AGI-2 task 409aa875."""

from collections import Counter, deque
from typing import Dict, List, Tuple, TypedDict


Grid = List[List[int]]


class Component(TypedDict):
    cells: List[Tuple[int, int]]
    color: int
    r_min: int
    c_min: int
    width: int


class Band(TypedDict):
    dest_r: int
    comps: List[Component]


class BandEntries(TypedDict):
    dest_r: int
    entries: List[Tuple[int, Component]]

SHIFT_ROWS = 5


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _background_color(grid: Grid) -> int:
    flat = [cell for row in grid for cell in row]
    return Counter(flat).most_common(1)[0][0]


def _connected_components(grid: Grid, background: int) -> List[Component]:
    height = len(grid)
    width = len(grid[0])
    seen = [[False] * width for _ in range(height)]
    components: List[Component] = []

    for r in range(height):
        for c in range(width):
            value = grid[r][c]
            if value == background or seen[r][c]:
                continue

            stack = [(r, c)]
            seen[r][c] = True
            cells: List[Tuple[int, int]] = []
            r_min = r_max = r
            c_min = c_max = c

            while stack:
                y, x = stack.pop()
                cells.append((y, x))
                r_min = min(r_min, y)
                r_max = max(r_max, y)
                c_min = min(c_min, x)
                c_max = max(c_max, x)

                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = y + dy, x + dx
                        if (
                            0 <= ny < height
                            and 0 <= nx < width
                            and not seen[ny][nx]
                            and grid[ny][nx] == value
                        ):
                            seen[ny][nx] = True
                            stack.append((ny, nx))

            comp: Component = {
                "cells": cells,
                "color": int(value),
                "r_min": r_min,
                "c_min": c_min,
                "width": c_max - c_min + 1,
            }
            components.append(comp)

    return components


def _recolor_from(original: Grid, out: Grid, start: Tuple[int, int], new_color: int) -> None:
    height = len(original)
    width = len(original[0])
    target = original[start[0]][start[1]]
    queue = deque([start])
    visited = {start}

    while queue:
        y, x = queue.popleft()
        out[y][x] = new_color
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if (
                0 <= ny < height
                and 0 <= nx < width
                and (ny, nx) not in visited
                and original[ny][nx] == target
            ):
                visited.add((ny, nx))
                queue.append((ny, nx))


def _project_components(grid: Grid) -> Grid:
    background = _background_color(grid)
    components = [
        comp
        for comp in _connected_components(grid, background)
        if comp["r_min"] >= SHIFT_ROWS
    ]

    if not components:
        return _copy_grid(grid)

    height = len(grid)
    width = len(grid[0])
    base_col = min(comp["c_min"] for comp in components)
    out = _copy_grid(grid)
    per_row: Dict[int, List[Tuple[int, Component]]] = {}

    for comp in components:
        dest_r = int(comp["r_min"]) - SHIFT_ROWS
        offset = int(comp["c_min"]) - base_col
        width_comp = int(comp["width"])
        dest_c = offset + (width_comp - 1) // 2
        if 0 <= dest_r < height and 0 <= dest_c < width:
            per_row.setdefault(dest_r, []).append((dest_c, comp))

    for dest_r, entries in per_row.items():
        entries.sort(key=lambda item: item[0])
        group_size = len(entries)
        middle_index = group_size // 2 if group_size >= 3 and group_size % 2 == 1 else -1
        for idx, (dest_c, comp) in enumerate(entries):
            marker = 1 if idx == middle_index else 9
            original_value = grid[dest_r][dest_c]
            out[dest_r][dest_c] = marker
            if original_value != background and original_value != marker:
                _recolor_from(grid, out, (dest_r, dest_c), marker)

    return out


def groupByBand(grid: Grid) -> List[Band]:
    """Group components by their destination row band after lifting.

    A band is a dict with keys:
      - "dest_r": int, the lifted row index
      - "comps": List[Component], components in this band
    """
    background = _background_color(grid)
    components: List[Component] = [
        comp
        for comp in _connected_components(grid, background)
        if comp["r_min"] >= SHIFT_ROWS
    ]

    per_row: Dict[int, List[Component]] = {}
    for comp in components:
        dest_r = comp["r_min"] - SHIFT_ROWS
        per_row.setdefault(dest_r, []).append(comp)

    # Preserve insertion order of bands as discovered
    return [{"dest_r": r, "comps": comps} for r, comps in per_row.items()]


def liftBands(bands: List[Band]) -> List[Band]:
    """Pass-through: components are already implicitly lifted by dest_r.

    This keeps the same structure while making the stage explicit.
    """
    return bands


def normaliseBandColumns(bands: List[Band]) -> List[BandEntries]:
    """Compute marker destination columns using a global base column.

    For each component, compute dest_c as (c_min - base_col) + (width-1)//2,
    where base_col is the minimum c_min across all components (global).
    Returns bands with an added key "entries": List[(dest_c:int, comp:Component)].
    """
    # Flatten to find global base column (matches committed solver semantics)
    all_comps: List[Component] = [comp for band in bands for comp in band["comps"]]
    if not all_comps:
        return []
    base_col = min(comp["c_min"] for comp in all_comps)

    out: List[BandEntries] = []
    for band in bands:
        comps: List[Component] = band["comps"]
        entries: List[Tuple[int, Component]] = []
        for comp in comps:
            offset = comp["c_min"] - base_col
            width_comp = comp["width"]
            dest_c = offset + (width_comp - 1) // 2
            entries.append((dest_c, comp))
        out.append({"dest_r": band["dest_r"], "entries": entries})
    return out


def markBandCentroids(grid: Grid, bands: List[BandEntries]) -> Grid:
    """Render markers for each band, highlighting the middle one when odd-sized.

    - Places color 1 at the middle marker of odd-sized bands (size >= 3)
    - Places color 9 at other marker positions
    - If the marker lands on a non-background color different from marker,
      recolor that original 4-connected component to the marker color.
    """
    background = _background_color(grid)
    height = len(grid)
    width = len(grid[0])
    out = _copy_grid(grid)

    for band in bands:
        dest_r = band["dest_r"]
        entries: List[Tuple[int, Component]] = band["entries"]
        if not (0 <= dest_r < height) or not entries:
            continue
        entries_sorted = sorted(entries, key=lambda item: item[0])
        group_size = len(entries_sorted)
        middle_index = group_size // 2 if group_size >= 3 and group_size % 2 == 1 else -1
        for idx, (dest_c, _comp) in enumerate(entries_sorted):
            if not (0 <= dest_c < width):
                continue
            marker = 1 if idx == middle_index else 9
            original_value = grid[dest_r][dest_c]
            out[dest_r][dest_c] = marker
            if original_value != background and original_value != marker:
                _recolor_from(grid, out, (dest_r, dest_c), marker)

    return out


def solve_409aa875(grid: Grid) -> Grid:
    bands = groupByBand(grid)
    lifted = liftBands(bands)
    normalised = normaliseBandColumns(lifted)
    return markBandCentroids(grid, normalised)


p = solve_409aa875
