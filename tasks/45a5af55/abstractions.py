"""Abstractions explored for ARC-AGI-2 task 45a5af55."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

Grid = List[List[int]]
Example = Dict[str, Grid]
Abstraction = Callable[[Grid], Grid]

_TASK_PATH = Path(__file__).resolve().parent / "arc2_samples" / "45a5af55.json"


def _load_task() -> Dict[str, Sequence[Example]]:
    with _TASK_PATH.open() as fh:
        return json.load(fh)


def identity_baseline(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _primary_axis_colors(grid: Grid, *, drop_last: bool) -> List[int]:
    if not grid or not grid[0]:
        return []
    height = len(grid)
    width = len(grid[0])
    use_rows = height >= width
    axis_length = height if use_rows else width
    limit = axis_length - (1 if drop_last else 0)
    if limit <= 0:
        return []
    if use_rows:
        return [grid[r][0] for r in range(limit)]
    return [grid[0][c] for c in range(limit)]


def _make_rings(colors: Iterable[int]) -> Grid:
    colors = list(colors)
    size = 2 * len(colors)
    if size == 0:
        return []
    out = [[0] * size for _ in range(size)]
    for depth, color in enumerate(colors):
        top = depth
        bottom = size - 1 - depth
        left = depth
        right = size - 1 - depth
        for x in range(left, right + 1):
            out[top][x] = color
            out[bottom][x] = color
        for y in range(top, bottom + 1):
            out[y][left] = color
            out[y][right] = color
    return out


def rings_with_full_axis(grid: Grid) -> Grid:
    colors = _primary_axis_colors(grid, drop_last=False)
    if not colors:
        return [row[:] for row in grid]
    return _make_rings(colors)


def rings_drop_last_axis_color(grid: Grid) -> Grid:
    colors = _primary_axis_colors(grid, drop_last=True)
    if not colors:
        return [row[:] for row in grid]
    return _make_rings(colors)


def _score_split(name: str, examples: Sequence[Example], fn: Abstraction) -> str:
    scored = [(idx, ex) for idx, ex in enumerate(examples) if "output" in ex]
    if not scored:
        return f"  {name}: no labeled cases"
    matches = 0
    first_fail = None
    for idx, ex in scored:
        pred = fn(ex["input"])
        if pred == ex["output"]:
            matches += 1
        elif first_fail is None:
            first_fail = idx
    total = len(scored)
    if matches == total:
        return f"  {name}: {matches}/{total} correct"
    return f"  {name}: {matches}/{total} correct, first failure at {first_fail}"


def evaluate_abstractions(abstractions: Sequence[Tuple[str, Abstraction]]) -> None:
    data = _load_task()
    splits = ["train", "test", "arc_gen"]
    for name, fn in abstractions:
        print(f"ABSTRACTION {name}")
        for split in splits:
            examples = data.get(split, [])
            if not examples:
                print(f"  {split}: no cases")
                continue
            print(_score_split(split, examples, fn))
        print()


if __name__ == "__main__":
    evaluate_abstractions([
        ("identity_baseline", identity_baseline),
        ("rings_with_full_axis", rings_with_full_axis),
        ("rings_drop_last_axis_color", rings_drop_last_axis_color),
    ])
