"""Abstraction experiments for ARC task 5dbc8537."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.append(str(_REPO_ROOT))

task_module = importlib.import_module("analysis.arc2_samples.5dbc8537")

Grid = List[List[int]]


_TASK_ID = "5dbc8537"
_DATA_DIR = Path(__file__).resolve().parent / "arc2_samples"
_DATA_PATH = _DATA_DIR / f"{_TASK_ID}.json"


def _load_split(split: str) -> Optional[Sequence[Dict[str, Grid]]]:
    if not _DATA_PATH.exists():
        return None
    with _DATA_PATH.open() as f:
        data = json.load(f)
    return data.get(split)


def _background_for_bbox(grid: Grid, bbox: Tuple[int, int, int, int], fill: int) -> int:
    min_r, max_r, min_c, max_c = bbox
    for r in range(min_r, max_r + 1):
        for c in range(min_c, max_c + 1):
            val = grid[r][c]
            if val != fill:
                return val
    raise ValueError("Bounding box lacks a background colour")


def horizontal_projection(grid: Grid) -> Grid:
    fill, bbox, (height, _) = task_module._find_target_component(grid)
    min_r, max_r, min_c, max_c = bbox
    if max_r - min_r + 1 != height:
        raise ValueError("Grid is not in the horizontal configuration")
    background = _background_for_bbox(grid, bbox, fill)
    return task_module._solve_horizontal(grid, bbox, fill, background)


def vertical_projection(grid: Grid) -> Grid:
    fill, bbox, (_, width) = task_module._find_target_component(grid)
    min_r, max_r, min_c, max_c = bbox
    if max_c - min_c + 1 != width:
        raise ValueError("Grid is not in the vertical configuration")
    background = _background_for_bbox(grid, bbox, fill)
    return task_module._solve_vertical(grid, bbox, fill, background)


def full_solver(grid: Grid) -> Grid:
    return task_module.solve_5dbc8537(grid)


ABSTRACTIONS: Sequence[Tuple[str, Callable[[Grid], Grid]]] = (
    ("horizontal-only", horizontal_projection),
    ("vertical-only", vertical_projection),
    ("hybrid", full_solver),
)


def _evaluate_on_split(
    name: str, split: Optional[Sequence[Dict[str, Grid]]], abstraction: Callable[[Grid], Grid]
) -> Tuple[int, int, Optional[Tuple[str, int]]]:
    """Return (#matches, total, first_failure) for the requested abstraction."""

    if not split:
        return 0, 0, None

    matches = 0
    first_failure: Optional[Tuple[str, int]] = None
    for idx, entry in enumerate(split):
        grid_in = entry["input"]
        expected = entry.get("output")

        try:
            result = abstraction(grid_in)
        except Exception:  # pragma: no cover - diagnostic hook
            if first_failure is None:
                first_failure = (name, idx)
            continue

        if expected is None:
            continue

        if result == expected:
            matches += 1
        elif first_failure is None:
            first_failure = (name, idx)

    return matches, len(split), first_failure


def main() -> None:
    train_split = _load_split("train")
    test_split = _load_split("test")
    arcgen_path = _DATA_DIR / f"{_TASK_ID}_arcgen.json"
    arcgen_split = None
    if arcgen_path.exists():
        with arcgen_path.open() as f:
            arcgen_split = json.load(f).get("arcgen")

    for name, abstraction in ABSTRACTIONS:
        train_matches, train_total, train_failure = _evaluate_on_split("train", train_split, abstraction)
        test_matches, test_total, test_failure = _evaluate_on_split("test", test_split, abstraction)
        arcgen_matches, arcgen_total, arcgen_failure = _evaluate_on_split("arc-gen", arcgen_split, abstraction)

        print(f"[{name}] train {train_matches}/{train_total}")
        if train_failure:
            split, idx = train_failure
            print(f"  first failure: {split}[{idx}]")

        if test_total:
            print(f"  test produced {test_total} candidate outputs")
        if test_failure:
            split, idx = test_failure
            print(f"  test failure: {split}[{idx}]")

        if arcgen_total:
            print(f"  arc-gen {arcgen_matches}/{arcgen_total}")
            if arcgen_failure:
                split, idx = arcgen_failure
                print(f"  first arc-gen failure: {split}[{idx}]")


if __name__ == "__main__":
    main()
