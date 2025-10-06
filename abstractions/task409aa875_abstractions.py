"""Abstraction experiments for ARC task 409aa875."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple


Grid = List[List[int]]

DATA_PATH = Path("analysis/arc2_samples/409aa875.json")
SHIFT_ROWS = 5


def load_dataset() -> Dict[str, List[dict]]:
    with DATA_PATH.open() as f:
        data = json.load(f)
    return {
        "train": data.get("train", []),
        "test": data.get("test", []),
        "arc-gen": data.get("arc-gen", []),
    }


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _get_background(grid: Grid) -> int:
    return Counter(cell for row in grid for cell in row).most_common(1)[0][0]


def _get_components(grid: Grid, background: int) -> List[Dict]:
    height = len(grid)
    width = len(grid[0])
    visited = [[False] * width for _ in range(height)]
    components: List[Dict] = []
    for r in range(height):
        for c in range(width):
            value = grid[r][c]
            if value == background or visited[r][c]:
                continue
            stack = [(r, c)]
            visited[r][c] = True
            cells: List[Tuple[int, int]] = []
            while stack:
                x, y = stack.pop()
                cells.append((x, y))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < height
                            and 0 <= ny < width
                            and not visited[nx][ny]
                            and grid[nx][ny] == value
                        ):
                            visited[nx][ny] = True
                            stack.append((nx, ny))
            rows = [row for row, _ in cells]
            cols = [col for _, col in cells]
            components.append(
                {
                    "cells": cells,
                    "color": value,
                    "r_min": min(rows),
                    "c_min": min(cols),
                    "width": max(cols) - min(cols) + 1,
                }
            )
    return components


def _recolor_component(original: Grid, out: Grid, start: Tuple[int, int], new_color: int) -> None:
    height = len(original)
    width = len(original[0])
    target_color = original[start[0]][start[1]]
    stack = [start]
    seen = {start}
    while stack:
        x, y = stack.pop()
        out[x][y] = new_color
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < height
                and 0 <= ny < width
                and (nx, ny) not in seen
                and original[nx][ny] == target_color
            ):
                seen.add((nx, ny))
                stack.append((nx, ny))


def _project_components(
    grid: Grid,
    *,
    normalise_columns: bool,
    highlight_middle: bool = True,
) -> Grid:
    background = _get_background(grid)
    components = [
        comp
        for comp in _get_components(grid, background)
        if comp["r_min"] >= SHIFT_ROWS
    ]
    if not components:
        return copy_grid(grid)

    base_col = min(comp["c_min"] for comp in components) if normalise_columns else 0
    height = len(grid)
    width = len(grid[0])
    out = copy_grid(grid)

    per_row: Dict[int, List[Tuple[int, Dict]]] = {}
    for comp in components:
        dest_r = comp["r_min"] - SHIFT_ROWS
        offset = comp["c_min"] - base_col
        dest_c = offset + (comp["width"] - 1) // 2
        if 0 <= dest_r < height and 0 <= dest_c < width:
            per_row.setdefault(dest_r, []).append((dest_c, comp))

    for dest_r, entries in per_row.items():
        entries.sort(key=lambda item: item[0])
        group_size = len(entries)
        middle_index = group_size // 2 if highlight_middle and group_size >= 3 and group_size % 2 == 1 else -1
        for idx, (dest_c, comp) in enumerate(entries):
            marker_color = 1 if idx == middle_index else 9
            original_value = grid[dest_r][dest_c]
            out[dest_r][dest_c] = marker_color
            if original_value != background and original_value != marker_color:
                _recolor_component(grid, out, (dest_r, dest_c), marker_color)
    return out


def identity_solver(grid: Grid) -> Grid:
    """Baseline abstraction: mirror the input unchanged."""

    return copy_grid(grid)


def centroid_projection_no_normalisation(grid: Grid) -> Grid:
    """Prototype – project component centres without horizontal normalisation.

    This captures the basic idea of lifting components upward but keeps their
    absolute X positions. It succeeds on cases where the bands are already
    anchored near the origin but fails on scenarios such as train[2], where the
    patterns live far to the right and need re-anchoring.
    """

    return _project_components(grid, normalise_columns=False)


def centroid_projection_global_shift(grid: Grid) -> Grid:
    """Refined abstraction – shift components by the band minimum before lifting."""

    return _project_components(grid, normalise_columns=True)


Abstraction = Callable[[Grid], Grid]


def evaluate_abstractions(abstractions: Iterable[Tuple[str, Abstraction]]) -> None:
    dataset = load_dataset()
    for name, solver in abstractions:
        print(f"=== {name} ===")
        for split_name in ("train", "test", "arc-gen"):
            samples = dataset.get(split_name, [])
            if not samples:
                print(f"  {split_name:7s}: no samples")
                continue
            total = 0
            success = 0
            first_fail = None
            for idx, sample in enumerate(samples):
                pred = solver(sample["input"])
                if "output" not in sample:
                    continue
                total += 1
                if pred == sample["output"]:
                    success += 1
                elif first_fail is None:
                    first_fail = idx
            if total == 0:
                print(f"  {split_name:7s}: n/a (no outputs)")
                continue
            rate = 100.0 * success / total
            fail_str = "-" if first_fail is None else str(first_fail)
            print(f"  {split_name:7s}: {success:2d}/{total:2d} ({rate:5.1f}%), first fail: {fail_str}")
        print()


if __name__ == "__main__":
    evaluate_abstractions(
        [
            ("identity", identity_solver),
            ("centroid-no-norm", centroid_projection_no_normalisation),
            ("centroid-global-shift", centroid_projection_global_shift),
        ]
    )
