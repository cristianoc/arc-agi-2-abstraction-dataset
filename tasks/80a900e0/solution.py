"""Solver for ARC-AGI-2 task 80a900e0 (split: evaluation)."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Callable, Dict, Iterable, List, Sequence, Tuple


Grid = List[List[int]]
Color = int
Pos = Tuple[int, int]


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def background_palette(grid: Grid) -> set[int]:
    counts = Counter(pixel for row in grid for pixel in row)
    palette = {c for c in (0, 1) if c in counts}
    if palette:
        return palette
    most_common = counts.most_common(1)
    return {most_common[0][0]} if most_common else {0}


def find_runs(points: Sequence[Pos], step: Pos) -> List[List[Pos]]:
    ordered = sorted(points)
    runs: List[List[Pos]] = []
    current: List[Pos] = []
    for r, c in ordered:
        if not current:
            current = [(r, c)]
            continue
        pr, pc = current[-1]
        if (r - pr, c - pc) == step:
            current.append((r, c))
        else:
            if len(current) >= 3:
                runs.append(current)
            current = [(r, c)]
    if len(current) >= 3:
        runs.append(current)
    return runs


def groupHandlesByColour(grid: Grid) -> List[Tuple[Color, List[Pos]]]:
    """Collect non-background colours and their coordinates in first-encounter order."""
    bg = background_palette(grid)
    order: List[Color] = []
    coords_by_color: Dict[Color, List[Pos]] = {}
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val in bg:
                continue
            if val not in coords_by_color:
                coords_by_color[val] = []
                order.append(val)
            coords_by_color[val].append((r, c))
    return [(col, coords_by_color[col]) for col in order]


def findHandleRuns(handles: List[Tuple[Color, List[Pos]]]):
    """For each colour's points, detect diagonal runs and target diagonals to extend."""
    runs_by_colour: Dict[Color, Dict[str, object]] = {}
    for color, coords in handles:
        sum_groups: Dict[int, List[Pos]] = defaultdict(list)
        diff_groups: Dict[int, List[Pos]] = defaultdict(list)
        for r, c in coords:
            sum_groups[r + c].append((r, c))
            diff_groups[r - c].append((r, c))

        target_sums: set[int] = set()
        target_diffs: set[int] = set()
        has_sum_runs = False
        has_diff_runs = False

        for points in sum_groups.values():
            runs = find_runs(points, (1, -1))
            if runs:
                has_sum_runs = True
                for run in runs:
                    first_r, first_c = run[0]
                    last_r, last_c = run[-1]
                    target_diffs.add(first_r - first_c)
                    target_diffs.add(last_r - last_c)

        for points in diff_groups.values():
            runs = find_runs(points, (1, 1))
            if runs:
                has_diff_runs = True
                for run in runs:
                    first_r, first_c = run[0]
                    last_r, last_c = run[-1]
                    target_sums.add(first_r + first_c)
                    target_sums.add(last_r + last_c)

        runs_by_colour[color] = {
            "has_sum_runs": has_sum_runs,
            "has_diff_runs": has_diff_runs,
            "target_sums": target_sums,
            "target_diffs": target_diffs,
        }
    return runs_by_colour


def extendAlongAxis(canvas: Grid, handle_runs, colour: Color) -> Grid:
    """Extend a colour's diagonal handles along the perpendicular axis with guards."""
    rows = len(canvas)
    cols = len(canvas[0]) if rows else 0
    bg = background_palette(canvas)
    info = handle_runs.get(colour)
    if not info:
        return canvas
    has_sum = bool(info["has_sum_runs"])
    has_diff = bool(info["has_diff_runs"])
    if has_sum and has_diff:
        return canvas

    target_sums: Iterable[int] = info["target_sums"]
    target_diffs: Iterable[int] = info["target_diffs"]

    output = _copy_grid(canvas)

    def should_paint(r: int, c: int) -> bool:
        original = canvas[r][c]
        if original not in bg:
            return False
        current = output[r][c]
        return current in bg or current == colour

    if has_sum:
        for diff in target_diffs:
            for r in range(rows):
                c = r - diff
                if 0 <= c < cols and should_paint(r, c):
                    output[r][c] = colour

    if has_diff:
        for total in target_sums:
            for r in range(rows):
                c = total - r
                if 0 <= c < cols and should_paint(r, c):
                    output[r][c] = colour

    return output


def fold_repaint(canvas: Grid, items: Sequence[Color], update: Callable[[Grid, Color], Grid]) -> Grid:
    result = canvas
    for item in items:
        result = update(result, item)
    return result


def solve_80a900e0(grid: Grid) -> Grid:
    handles = groupHandlesByColour(grid)
    handle_runs = findHandleRuns(handles)
    colours = [colour for colour, _ in handles]

    def extend(canvas: Grid, colour: Color) -> Grid:
        return extendAlongAxis(canvas, handle_runs, colour)

    return fold_repaint(grid, colours, extend)


p = solve_80a900e0
