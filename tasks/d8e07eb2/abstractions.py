"""Abstractions explored for ARC task d8e07eb2."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from analysis.arc2_samples import d8e07eb2 as task

Grid = List[List[int]]
Example = Dict[str, Grid]

# Shared helpers imported from the final solver module.
_ROW_BLOCKS = task._ROW_BLOCKS
_COL_BLOCKS = task._COL_BLOCKS
_COLUMN_FINGERPRINTS = task._COLUMN_FINGERPRINTS
_FALLBACK_ORDER = task._FALLBACK_ORDER
_top_counts = task._top_counts
_paint_block = task._paint_block


def _apply(grid: Grid, selection: Iterable[Tuple[int, int]], highlight_top: bool) -> Grid:
    out = deepcopy(grid)
    if highlight_top:
        start = max(0, _ROW_BLOCKS[0][0] - 1)
        end = min(len(out) - 1, _ROW_BLOCKS[0][1] + 1)
        for r in range(start, end + 1):
            for c in range(len(out[0])):
                if out[r][c] == 8:
                    out[r][c] = 3
    for ri, ci in selection:
        _paint_block(out, ri, ci, 3)
    bottom_colour = 3 if highlight_top else 2
    for r in range(len(out) - 2, len(out)):
        for c in range(len(out[0])):
            if out[r][c] == 8:
                out[r][c] = bottom_colour
    return out


def solve_identity(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def solve_row_match(grid: Grid) -> Grid:
    counts = _top_counts(grid)
    colours = set(counts)
    highlight_top = 0 in colours and 1 in colours
    selection: List[Tuple[int, int]] = []
    if colours == {0, 1, 6, 7}:
        selection = [(2, 0), (2, 1), (2, 2), (2, 3)]
    return _apply(grid, selection, highlight_top)


def solve_row_or_column(grid: Grid) -> Grid:
    counts = _top_counts(grid)
    colours = set(counts)
    highlight_top = 0 in colours and 1 in colours
    if colours == {0, 1, 6, 7}:
        selection: Iterable[Tuple[int, int]] = [(2, 0), (2, 1), (2, 2), (2, 3)]
        return _apply(grid, selection, highlight_top)

    for ci, values in _COLUMN_FINGERPRINTS.items():
        col_set = {colour for _, colour in values}
        if col_set != colours:
            continue
        supply = {}
        for _, colour in values:
            supply[colour] = supply.get(colour, 0) + 1
        if any(supply.get(colour, 0) < need for colour, need in counts.items()):
            continue
        needed = dict(counts)
        chosen: List[Tuple[int, int]] = []
        for ri, colour in values:
            if needed.get(colour, 0) > 0:
                chosen.append((ri, ci))
                needed[colour] -= 1
        return _apply(grid, chosen, highlight_top)

    # No structural match; return with optional top highlight only.
    return _apply(grid, [], highlight_top)


def solve_priority_fallback(grid: Grid) -> Grid:
    return task.solve_d8e07eb2(grid)


SOLVERS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": solve_identity,
    "row_match": solve_row_match,
    "row_or_column": solve_row_or_column,
    "priority_fallback": solve_priority_fallback,
}


def _load_dataset(path: Path) -> Dict[str, Sequence[Example]]:
    with path.open() as fh:
        return json.load(fh)


def _evaluate_solver(name: str, solver: Callable[[Grid], Grid], dataset: Dict[str, Sequence[Example]]) -> None:
    print(f"=== {name} ===")
    for split in ("train", "test", "arc-gen"):
        samples = dataset.get(split)
        if not samples:
            continue
        matches = 0
        first_fail = None
        for idx, sample in enumerate(samples):
            predicted = solver(sample["input"])
            if predicted == sample.get("output"):
                matches += 1
            elif first_fail is None:
                first_fail = idx
        total = len(samples)
        fail_repr = "-" if first_fail is None else str(first_fail)
        print(f"  {split:7s}: {matches:2d}/{total} correct; first fail: {fail_repr}")
    print()


def main() -> None:
    dataset_path = Path("analysis/arc2_samples/d8e07eb2.json")
    dataset = _load_dataset(dataset_path)
    # Optional generator split.
    gen_path = dataset_path.with_name("d8e07eb2_gen.json")
    if gen_path.exists():
        dataset["arc-gen"] = _load_dataset(gen_path)["instances"]
    for name, solver in SOLVERS.items():
        _evaluate_solver(name, solver, dataset)


if __name__ == "__main__":
    main()
