"""Abstractions explored for ARC task d59b0160."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple

Grid = List[List[int]]
Component = Dict[str, object]


def _deepcopy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _find_nonseven_components(grid: Grid) -> List[Component]:
    height = len(grid)
    width = len(grid[0])
    seen = [[False] * width for _ in range(height)]
    comps: List[Component] = []

    for r in range(height):
        for c in range(width):
            if seen[r][c] or grid[r][c] == 7:
                continue
            stack = deque([(r, c)])
            seen[r][c] = True
            cells: List[Tuple[int, int]] = []
            colors = set()
            r_min = r_max = r
            c_min = c_max = c

            while stack:
                cr, cc = stack.pop()
                cells.append((cr, cc))
                colors.add(grid[cr][cc])
                r_min = min(r_min, cr)
                r_max = max(r_max, cr)
                c_min = min(c_min, cc)
                c_max = max(c_max, cc)
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not seen[nr][nc] and grid[nr][nc] != 7:
                        seen[nr][nc] = True
                        stack.append((nr, nc))

            comps.append({
                "cells": cells,
                "colors": colors,
                "r0": r_min,
                "r1": r_max,
                "c0": c_min,
                "c1": c_max,
                "width": c_max - c_min + 1,
                "height": r_max - r_min + 1,
            })

    return comps


def _apply_rule(grid: Grid, predicate: Callable[[Component, Tuple[int, int]], bool]) -> Grid:
    result = _deepcopy_grid(grid)
    if not result:
        return result
    shape = (len(result), len(result[0]))
    for comp in _find_nonseven_components(result):
        if predicate(comp, shape):
            for r, c in comp["cells"]:
                result[r][c] = 7
    return result


def abstraction_touch_right(grid: Grid) -> Grid:
    """Fill components touching the right edge when sufficiently wide."""

    def predicate(comp: Component, shape: Tuple[int, int]) -> bool:
        width = comp["width"]
        c1 = comp["c1"]
        _, w = shape
        return width > 2 and c1 == w - 1

    return _apply_rule(grid, predicate)


def abstraction_internal_height4(grid: Grid) -> Grid:
    """Fill interior components (no edge contact) with height <= 4."""

    def predicate(comp: Component, shape: Tuple[int, int]) -> bool:
        height = comp["height"]
        r0, r1 = comp["r0"], comp["r1"]
        c0, c1 = comp["c0"], comp["c1"]
        h, w = shape
        touches_edge = r0 == 0 or r1 == h - 1 or c0 == 0 or c1 == w - 1
        return not touches_edge and height <= 4 and comp["width"] > 2

    return _apply_rule(grid, predicate)


def abstraction_full_rule(grid: Grid) -> Grid:
    """Final rule mirrored in the solver."""

    def predicate(comp: Component, shape: Tuple[int, int]) -> bool:
        h, w = shape
        width = comp["width"]
        height = comp["height"]
        r0, r1 = comp["r0"], comp["r1"]
        c0, c1 = comp["c0"], comp["c1"]
        touches_top = r0 == 0
        touches_right = c1 == w - 1
        touches_left = c0 == 0

        if width <= 2 or touches_top:
            return False
        if touches_right:
            return True
        if touches_left:
            return height <= 5
        if height <= 4:
            return True
        if height == 5 and len(comp["colors"]) <= 4:
            return c0 <= 2 or c0 >= w - 4
        return False

    return _apply_rule(grid, predicate)


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": _deepcopy_grid,
    "touch_right": abstraction_touch_right,
    "internal_height4": abstraction_internal_height4,
    "full_rule": abstraction_full_rule,
}


def _evaluate_split(pairs: Iterable[dict], abstraction: Callable[[Grid], Grid]) -> Tuple[int, int]:
    total = 0
    failures = 0
    first_failure = -1
    for idx, pair in enumerate(pairs):
        total += 1
        if "output" not in pair:
            continue
        pred = abstraction(pair["input"])
        if pred != pair["output"]:
            failures += 1
            if first_failure == -1:
                first_failure = idx
    return failures, first_failure


def _maybe_load(path: Path) -> dict | None:
    if path.exists():
        return json.loads(path.read_text())
    return None


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    data_path = base / "arc2_samples" / "d59b0160.json"
    dataset = json.loads(data_path.read_text())
    arcgen_path = base / "arc2_samples" / "d59b0160_arcgen.json"
    arcgen = _maybe_load(arcgen_path)

    splits = [("train", dataset.get("train", []))]
    if dataset.get("test"):
        splits.append(("test", dataset["test"]))
    if arcgen:
        splits.append(("arcgen", arcgen.get("pairs", [])))

    for split_name, pairs in splits:
        print(f"[{split_name}]")
        for name, fn in ABSTRACTIONS.items():
            failures, first_failure = _evaluate_split(pairs, fn)
            total = len([p for p in pairs if "output" in p])
            if total:
                solved = total - failures
                pct = 100.0 * solved / total
                first = first_failure if failures else "-"
                print(f"  {name:16s} solved={solved}/{total} ({pct:5.1f}%) first_fail={first}")
            else:
                print(f"  {name:16s} predictions generated (no ground truth)")
        print()


if __name__ == "__main__":
    main()
