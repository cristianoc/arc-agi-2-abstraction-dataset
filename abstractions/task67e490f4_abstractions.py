"""Abstraction experiments for ARC task 67e490f4."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

Grid = List[List[int]]
Coordinate = Tuple[int, int]
Shape = Tuple[Coordinate, ...]

DATA_ROOT = Path(__file__).with_suffix("")
SAMPLE_PATH = Path("analysis/arc2_samples/67e490f4.json")
ARCGEN_PATH = Path("analysis/arc2_samples/67e490f4_arcgen.json")


def _load_samples() -> Dict[str, List[Dict[str, Grid]]]:
    base = json.loads(SAMPLE_PATH.read_text())
    data = {"train": base.get("train", []), "test": base.get("test", [])}
    if ARCGEN_PATH.exists():
        data["arcgen"] = json.loads(ARCGEN_PATH.read_text()).get("samples", [])
    else:
        data["arcgen"] = []
    return data


def _canonical_shape(cells: Sequence[Coordinate]) -> Shape:
    min_r = min(r for r, _ in cells)
    min_c = min(c for _, c in cells)
    return tuple(sorted((r - min_r, c - min_c) for r, c in cells))


def _collect_components(
    grid: Grid,
    target: int,
    rows: range,
    cols: range,
    skip: Iterable[Coordinate] = (),
) -> List[List[Coordinate]]:
    index = {(r, c): (ri, ci) for ri, r in enumerate(rows) for ci, c in enumerate(cols)}
    seen = [[False] * len(cols) for _ in rows]
    for coord in skip:
        if coord in index:
            ri, ci = index[coord]
            seen[ri][ci] = True
    comps: List[List[Coordinate]] = []
    for ri, r in enumerate(rows):
        for ci, c in enumerate(cols):
            if seen[ri][ci] or grid[r][c] != target:
                continue
            stack = [(ri, ci)]
            seen[ri][ci] = True
            cells: List[Coordinate] = []
            while stack:
                cr, cc = stack.pop()
                cells.append((rows[cr], cols[cc]))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < len(rows) and 0 <= nc < len(cols):
                        if not seen[nr][nc] and grid[rows[nr]][cols[nc]] == target:
                            seen[nr][nc] = True
                            stack.append((nr, nc))
            comps.append(cells)
    return comps


def _collect_shapes_outside(
    grid: Grid,
    r0: int,
    c0: int,
    size: int,
    limit: int,
) -> Dict[Shape, Counter]:
    shape_counts: Dict[Shape, Counter] = defaultdict(Counter)
    visited = [[False] * len(grid[0]) for _ in grid]
    row_end = r0 + size
    col_end = c0 + size
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if r0 <= r < row_end and c0 <= c < col_end:
                continue
            if visited[r][c]:
                continue
            colour = grid[r][c]
            stack = [(r, c)]
            visited[r][c] = True
            cells: List[Coordinate] = []
            while stack:
                cr, cc = stack.pop()
                cells.append((cr, cc))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and not visited[nr][nc]:
                        if r0 <= nr < row_end and c0 <= nc < col_end:
                            continue
                        if grid[nr][nc] == colour:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
            if len(cells) <= limit:
                shape_counts[_canonical_shape(cells)][colour] += 1
    return shape_counts


def _build_solution(
    grid: Grid,
    detector: Callable[[Grid], Optional[Tuple[int, int, int, int, int]]],
) -> Optional[Grid]:
    detected = detector(grid)
    if detected is None:
        return None
    size, r0, c0, bg_colour, pattern_colour = detected
    rows = range(r0, r0 + size)
    cols = range(c0, c0 + size)
    comps = _collect_components(grid, pattern_colour, rows, cols)
    if not comps:
        return None

    centre = (size - 1) / 2
    comp_info = []
    outer_level = 0.0
    for cells in comps:
        local = [(r - r0, c - c0) for r, c in cells]
        shape = _canonical_shape(local)
        avg_r = sum(r for r, _ in local) / len(local)
        avg_c = sum(c for _, c in local) / len(local)
        abs_dr = abs(avg_r - centre)
        abs_dc = abs(avg_c - centre)
        max_abs = max(abs_dr, abs_dc)
        outer_level = max(outer_level, max_abs)
        comp_info.append(
            {
                "cells": local,
                "shape": shape,
                "abs_dr": abs_dr,
                "abs_dc": abs_dc,
                "max_abs": max_abs,
            }
        )

    shape_candidates = _collect_shapes_outside(grid, r0, c0, size, max(9, size))

    for info in comp_info:
        min_abs = min(info["abs_dr"], info["abs_dc"])
        if info["max_abs"] < 0.5:
            category = "center"
        elif min_abs < 0.5:
            category = "edge"
        elif info["max_abs"] > outer_level - 0.5:
            category = "corner"
        else:
            category = "ring"
        info["category"] = category

    palette: Dict[str, int] = {}
    for category in ("corner", "edge", "ring", "center"):
        relevant = [info for info in comp_info if info["category"] == category]
        if not relevant:
            continue
        aggregate = Counter()
        for info in relevant:
            aggregate += shape_candidates.get(info["shape"], Counter())
        for forbidden in (bg_colour, pattern_colour):
            if forbidden in aggregate:
                del aggregate[forbidden]
        chosen = max(aggregate.items(), key=lambda kv: (kv[1], kv[0]))[0] if aggregate else pattern_colour
        palette[category] = chosen

    solution = [[bg_colour] * size for _ in range(size)]
    for info in comp_info:
        colour = palette.get(info["category"], pattern_colour)
        for dr, dc in info["cells"]:
            solution[dr][dc] = colour
    return solution


def _detect_by_colour_bbox(grid: Grid) -> Optional[Tuple[int, int, int, int, int]]:
    bounds: Dict[int, List[int]] = {}
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val not in bounds:
                bounds[val] = [r, r, c, c]
            else:
                lo_r, hi_r, lo_c, hi_c = bounds[val]
                bounds[val] = [min(lo_r, r), max(hi_r, r), min(lo_c, c), max(hi_c, c)]
    candidates: List[Tuple[int, int, int, int, int]] = []
    for colour, (lo_r, hi_r, lo_c, hi_c) in bounds.items():
        size_r = hi_r - lo_r + 1
        size_c = hi_c - lo_c + 1
        if size_r != size_c:
            continue
        rows = range(lo_r, hi_r + 1)
        cols = range(lo_c, hi_c + 1)
        palette = {grid[r][c] for r in rows for c in cols}
        if len(palette) != 2:
            continue
        pattern_colour = next(col for col in palette if col != colour)
        comps = _collect_components(grid, pattern_colour, rows, cols)
        if len(comps) >= 4:
            candidates.append((size_r, lo_r, lo_c, colour, pattern_colour))
    if not candidates:
        return None
    return max(candidates, key=lambda item: (item[0], -item[1], -item[2]))


def _detect_by_two_colour_scan(grid: Grid) -> Optional[Tuple[int, int, int, int, int]]:
    height = len(grid)
    width = len(grid[0])
    for size in range(min(height, width), 4, -1):
        for r0 in range(height - size + 1):
            for c0 in range(width - size + 1):
                rows = range(r0, r0 + size)
                cols = range(c0, c0 + size)
                palette = {grid[r][c] for r in rows for c in cols}
                if len(palette) != 2:
                    continue
                counts = Counter(grid[r][c] for r in rows for c in cols)
                bg_colour = counts.most_common(1)[0][0]
                pattern_colour = next(col for col in palette if col != bg_colour)
                comps = _collect_components(grid, pattern_colour, rows, cols)
                if len(comps) < 4:
                    continue
                largest = max(len(comp) for comp in comps)
                if largest <= size - 1:
                    return size, r0, c0, bg_colour, pattern_colour
    return None


def abstraction_colour_bbox(grid: Grid) -> Optional[Grid]:
    """Initial attempt: rely on colour bounding boxes to locate the motif."""
    return _build_solution(grid, _detect_by_colour_bbox)


def abstraction_two_colour_scan(grid: Grid) -> Optional[Grid]:
    """Refined abstraction: scan for two-colour squares with controlled component sizes."""
    return _build_solution(grid, _detect_by_two_colour_scan)


ABSTRACTIONS: Dict[str, Callable[[Grid], Optional[Grid]]] = {
    "colour_bbox": abstraction_colour_bbox,
    "two_colour_scan": abstraction_two_colour_scan,
}


def _evaluate() -> None:
    samples = _load_samples()
    for name, fn in ABSTRACTIONS.items():
        print(f"[{name}]")
        for split, entries in samples.items():
            matches = 0
            evaluated = 0
            first_failure: Optional[int] = None
            for idx, sample in enumerate(entries):
                expected = sample.get("output")
                pred = fn(sample["input"])
                if expected is None:
                    continue
                evaluated += 1
                if pred == expected:
                    matches += 1
                elif first_failure is None:
                    first_failure = idx
            total = evaluated
            print(f"  {split:7s}: {matches:2d}/{total:2d} matches", end="")
            if total == 0:
                print(" (no targets)")
            elif first_failure is not None:
                print(f" (first failure at {first_failure})")
            else:
                print()
        print()


if __name__ == "__main__":
    _evaluate()
