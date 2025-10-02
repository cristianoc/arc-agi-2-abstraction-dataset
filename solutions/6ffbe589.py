"""Solver for ARC-AGI-2 task 6ffbe589."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


Grid = List[List[int]]
Feature = Tuple[int, int, int, int, int, float, float, int, int]

try:
    TASK_PATH = Path(__file__).with_suffix(".json")
except NameError:  # pragma: no cover - evaluation harness sets __file__ absent
    TASK_PATH = Path("analysis/arc2_samples/6ffbe589.json")
_TRAIN_CACHE: List[Tuple[Feature, int]] | None = None


def _dominant_color(grid: Grid) -> int:
    counts = [0] * 10
    for row in grid:
        for value in row:
            if value:
                counts[value] += 1
    return max(range(10), key=counts.__getitem__)


def _best_border_rect(grid: Grid, color: int) -> Tuple[int, int, int, int]:
    height = len(grid)
    width = len(grid[0])
    best = None
    for r0 in range(height):
        for r1 in range(r0 + 2, height):
            for c0 in range(width):
                for c1 in range(c0 + 2, width):
                    count = 0
                    for c in range(c0, c1 + 1):
                        if grid[r0][c] == color:
                            count += 1
                        if grid[r1][c] == color:
                            count += 1
                    for r in range(r0 + 1, r1):
                        if grid[r][c0] == color:
                            count += 1
                        if grid[r][c1] == color:
                            count += 1
                    area = (r1 - r0 + 1) * (c1 - c0 + 1)
                    key = (count, area)
                    if best is None or key > best[0]:
                        best = (key, r0, r1, c0, c1)
    assert best is not None
    _, r0, r1, c0, c1 = best
    return r0, r1, c0, c1


def _expand_if_needed(grid: Grid, r0: int, r1: int, c0: int, c1: int) -> Tuple[int, int, int, int]:
    height = len(grid)
    width = len(grid[0])
    expanded = True
    while expanded:
        expanded = False
        if r0 > 0 and any(grid[r0 - 1][c] != 0 for c in range(c0, c1 + 1)):
            r0 -= 1
            expanded = True
        if r1 < height - 1 and any(grid[r1 + 1][c] != 0 for c in range(c0, c1 + 1)):
            r1 += 1
            expanded = True
        if c0 > 0 and any(grid[r][c0 - 1] != 0 for r in range(r0, r1 + 1)):
            c0 -= 1
            expanded = True
        if c1 < width - 1 and any(grid[r][c1 + 1] != 0 for r in range(r0, r1 + 1)):
            c1 += 1
            expanded = True
    return r0, r1, c0, c1


def _iter_features(grid: Grid, r0: int, r1: int, c0: int, c1: int) -> Iterable[Tuple[Feature, Tuple[int, int]]]:
    height_region = r1 - r0 + 1
    width_region = c1 - c0 + 1
    total_height = len(grid)
    total_width = len(grid[0])

    def get(r: int, c: int) -> int:
        if 0 <= r < total_height and 0 <= c < total_width:
            return grid[r][c]
        return 0

    for i in range(height_region):
        rr = r0 + i
        for j in range(width_region):
            cc = c0 + j
            self_col = grid[rr][cc]
            up = get(rr - 1, cc)
            down = get(rr + 1, cc)
            left = get(rr, cc - 1)
            right = get(rr, cc + 1)
            row_norm = i / height_region
            col_norm = j / width_region
            feature: Feature = (self_col, up, down, left, right, row_norm, col_norm, height_region, width_region)
            yield feature, (i, j)


def _feature_distance(a: Feature, b: Feature) -> float:
    cat = sum(1.0 for x, y in zip(a[:5], b[:5]) if x != y)
    row_diff = abs(a[5] - b[5])
    col_diff = abs(a[6] - b[6])
    size_diff = abs(a[7] - b[7]) / 20.0 + abs(a[8] - b[8]) / 20.0
    return cat + row_diff + col_diff + size_diff


def _load_training_samples() -> List[Tuple[Feature, int]]:
    global _TRAIN_CACHE
    if _TRAIN_CACHE is not None:
        return _TRAIN_CACHE

    with TASK_PATH.open() as fh:
        data = json.load(fh)

    samples: List[Tuple[Feature, int]] = []
    for entry in data.get("train", []):
        grid: Grid = entry["input"]
        output: Grid = entry["output"]
        color = _dominant_color(grid)
        rect = _expand_if_needed(grid, *_best_border_rect(grid, color))
        for feature, (i, j) in _iter_features(grid, *rect):
            samples.append((feature, output[i][j]))

    _TRAIN_CACHE = samples
    return samples


def _nearest_color(feature: Feature, samples: Sequence[Tuple[Feature, int]]) -> int:
    best_color = 0
    best_distance = float("inf")
    for candidate, color in samples:
        dist = _feature_distance(feature, candidate)
        if dist < best_distance:
            best_distance = dist
            best_color = color
    return best_color


def solve_6ffbe589(grid: Grid) -> Grid:
    samples = _load_training_samples()
    color = _dominant_color(grid)
    rect = _expand_if_needed(grid, *_best_border_rect(grid, color))
    r0, r1, c0, c1 = rect
    height = r1 - r0 + 1
    width = c1 - c0 + 1
    result = [[0] * width for _ in range(height)]
    for feature, (i, j) in _iter_features(grid, *rect):
        result[i][j] = _nearest_color(feature, samples)
    return result


p = solve_6ffbe589
