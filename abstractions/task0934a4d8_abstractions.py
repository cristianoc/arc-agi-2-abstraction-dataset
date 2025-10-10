"""Abstractions explored for ARC task 0934a4d8."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable, List, Optional


Grid = List[List[int]]


DATA_PATH = Path(__file__).resolve().parents[1] / "arc2_samples" / "0934a4d8.json"


def load_dataset() -> dict:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def bounding_box(grid: Grid, target: int) -> tuple[int, int, int, int]:
    row_min = len(grid)
    row_max = -1
    col_min = len(grid[0])
    col_max = -1

    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value == target:
                if r < row_min:
                    row_min = r
                if r > row_max:
                    row_max = r
                if c < col_min:
                    col_min = c
                if c > col_max:
                    col_max = c

    if row_max == -1:
        raise ValueError("target value not found in grid")

    return row_min, row_max + 1, col_min, col_max + 1


def extract_block(grid: Grid, r_start: int, c_start: int, height: int, width: int) -> Grid:
    return [row[c_start : c_start + width] for row in grid[r_start : r_start + height]]


def flip_lr(block: Grid) -> Grid:
    return [list(reversed(row)) for row in block]


def flip_ud(block: Grid) -> Grid:
    return [row[:] for row in block[::-1]]


def horizontal_mirror(grid: Grid, offset: int = 2) -> Optional[Grid]:
    r0, r1, c0, c1 = bounding_box(grid, 8)
    height = r1 - r0
    width = c1 - c0
    total_cols = len(grid[0])

    start = total_cols - width - c0 + offset
    if not (0 <= start <= total_cols - width):
        return None

    block = extract_block(grid, r0, start, height, width)
    return flip_lr(block)


def vertical_mirror(grid: Grid, offset: int = 2) -> Optional[Grid]:
    r0, r1, c0, c1 = bounding_box(grid, 8)
    height = r1 - r0
    width = c1 - c0
    total_rows = len(grid)

    start = total_rows - height - r0 + offset
    if not (0 <= start <= total_rows - height):
        return None

    block = extract_block(grid, start, c0, height, width)
    return flip_ud(block)


def hybrid_offset_two(grid: Grid) -> Grid:
    r0, r1, c0, c1 = bounding_box(grid, 8)
    height = r1 - r0
    width = c1 - c0

    total_rows = len(grid)
    total_cols = len(grid[0])
    offset = 2

    horiz_start = total_cols - width - c0 + offset
    vert_start = total_rows - height - r0 + offset

    block_h = None
    dist_h = -1
    if 0 <= horiz_start <= total_cols - width:
        block_h = extract_block(grid, r0, horiz_start, height, width)
        dist_h = abs(c0 - horiz_start)

    block_v = None
    dist_v = -1
    if 0 <= vert_start <= total_rows - height:
        block_v = extract_block(grid, vert_start, c0, height, width)
        dist_v = abs(r0 - vert_start)

    if dist_h > dist_v and block_h is not None:
        return flip_lr(block_h)
    if dist_v > dist_h and block_v is not None:
        return flip_ud(block_v)

    if block_h is None:
        return flip_ud(block_v)
    if block_v is None:
        return flip_lr(block_h)

    count8_h = sum(value == 8 for row in block_h for value in row)
    count8_v = sum(value == 8 for row in block_v for value in row)

    if count8_v < count8_h:
        return flip_ud(block_v)
    if count8_h < count8_v:
        return flip_lr(block_h)

    return flip_lr(block_h)


ABSTRACTIONS: dict[str, Callable[[Grid], Optional[Grid]]] = {
    "horizontal_mirror_offset2": horizontal_mirror,
    "vertical_mirror_offset2": vertical_mirror,
    "hybrid_offset2": hybrid_offset_two,
}


def evaluate_abstraction(name: str, fn: Callable[[Grid], Optional[Grid]], dataset: dict) -> None:
    print(f"== {name} ==")
    for split in ("train", "test", "generated", "arc_gen"):
        cases = dataset.get(split)
        if not cases:
            continue

        matches = 0
        first_fail = None
        predictions: List[Optional[Grid]] = []

        for idx, case in enumerate(cases):
            pred = fn(case["input"])
            predictions.append(pred)
            expected = case.get("output")
            if expected is None or pred is None:
                if first_fail is None and expected is not None:
                    first_fail = idx
                continue
            if pred == expected:
                matches += 1
            elif first_fail is None:
                first_fail = idx

        total = len(cases)
        has_refs = cases[0].get("output") is not None

        if has_refs:
            info = f"{matches}/{total} correct"
            if first_fail is not None and matches != total:
                info += f"; first fail at index {first_fail}"
        else:
            sample = predictions[0]
            if sample is None:
                info = "no prediction produced"
            else:
                info = f"sample output shape {len(sample)}x{len(sample[0]) if sample else 0}"
        print(f"  {split}: {info}")


def main() -> None:
    dataset = load_dataset()
    for name, fn in ABSTRACTIONS.items():
        evaluate_abstraction(name, fn, dataset)


if __name__ == "__main__":
    main()
