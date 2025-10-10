"""Abstractions explored for ARC task 65b59efc."""

from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple


Grid = List[List[int]]

DATA_PATH = Path(__file__).resolve().parents[1] / "arc2_samples" / "65b59efc.json"
SOLVER_PATH = Path(__file__).resolve().parents[1] / "arc2_samples" / "65b59efc.py"


def load_dataset() -> Dict[str, Sequence[dict]]:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_solver_module():
    spec = importlib.util.spec_from_file_location("solver_65b59efc", SOLVER_PATH)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load solver module for task 65b59efc")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


SOLVER = load_solver_module()
MAPPING = SOLVER.MAPPING
FALLBACK = SOLVER.FALLBACK
ROW_SIZE_OPTIONS = SOLVER.ROW_SIZE_OPTIONS
COL_SIZE_OPTIONS = SOLVER.COL_SIZE_OPTIONS


def tupleify(cell: Grid) -> Tuple[Tuple[int, ...], ...]:
    return tuple(tuple(row) for row in cell)

def dominant_value(cell: Grid) -> int:
    counter = Counter(value for row in cell for value in row if value not in (0, 5))
    return counter.most_common(1)[0][0] if counter else 0


def choose_size(options: Tuple[int, int], cell_dim: int) -> int:
    small, large = options
    return large if cell_dim >= 4 else small


def find_segments(grid: Grid) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    rows = len(grid)
    cols = len(grid[0]) if grid else 0

    row_breaks = [-1]
    for r, row in enumerate(grid):
        if row.count(5) >= cols // 2:
            row_breaks.append(r)
    row_breaks.append(rows)

    row_segs = [
        (row_breaks[i] + 1, row_breaks[i + 1])
        for i in range(len(row_breaks) - 1)
        if row_breaks[i] + 1 < row_breaks[i + 1]
    ]

    col_breaks = [-1]
    for c in range(cols):
        if sum(row[c] == 5 for row in grid) >= rows // 2:
            col_breaks.append(c)
    col_breaks.append(cols)

    col_segs = [
        (col_breaks[i] + 1, col_breaks[i + 1])
        for i in range(len(col_breaks) - 1)
        if col_breaks[i] + 1 < col_breaks[i + 1]
    ]

    return row_segs, col_segs


def fetch_block(
    ri: int,
    ci: int,
    cell: Grid,
    use_mapping: bool,
) -> Grid:
    if use_mapping:
        key_cell = tupleify(cell)
        mapped = MAPPING.get((ri, ci, key_cell))
        if mapped is not None:
            return [list(row) for row in mapped]

    value = dominant_value(cell)
    if use_mapping:
        mapped = FALLBACK.get((ri, ci, value))
        if mapped is not None:
            return [list(row) for row in mapped]

    row_opts = ROW_SIZE_OPTIONS.get(ri, ROW_SIZE_OPTIONS[max(ROW_SIZE_OPTIONS)])
    col_opts = COL_SIZE_OPTIONS.get(ci, COL_SIZE_OPTIONS[max(COL_SIZE_OPTIONS)])

    height = choose_size(row_opts, len(cell))
    width = choose_size(col_opts, len(cell[0]) if cell and cell[0] else 0)

    return [[value for _ in range(width)] for _ in range(height)]


def assemble(grid: Grid, use_mapping: bool) -> Grid:
    row_segs, col_segs = find_segments(grid)
    if not row_segs or not col_segs:
        return [row[:] for row in grid]

    row_blocks: List[List[Grid]] = []
    row_heights: List[int] = []
    col_widths: List[Optional[int]] = [None] * len(col_segs)

    for ri, (r0, r1) in enumerate(row_segs):
        blocks_row: List[Grid] = []
        expected_height: Optional[int] = None
        for ci, (c0, c1) in enumerate(col_segs):
            cell = [row[c0:c1] for row in grid[r0:r1]]
            block = fetch_block(ri, ci, cell, use_mapping)
            blocks_row.append(block)

            height = len(block)
            width = len(block[0]) if block else 0

            if expected_height is None or height > expected_height:
                expected_height = height

            current_width = col_widths[ci]
            if current_width is None or width > current_width:
                col_widths[ci] = width

        row_blocks.append(blocks_row)
        row_heights.append(expected_height or 0)

    total_height = sum(row_heights)
    total_width = sum(width or 0 for width in col_widths)
    output = [[0 for _ in range(total_width)] for _ in range(total_height)]

    r_offset = 0
    for ri, blocks_row in enumerate(row_blocks):
        c_offset = 0
        for ci, block in enumerate(blocks_row):
            block_height = row_heights[ri]
            block_width = col_widths[ci] or 0
            for rr in range(block_height):
                source_row = block[rr] if rr < len(block) else []
                for cc in range(block_width):
                    val = source_row[cc] if cc < len(source_row) else 0
                    output[r_offset + rr][c_offset + cc] = val
            c_offset += block_width
        r_offset += row_heights[ri]

    return output


def dominant_fill_abstraction(grid: Grid) -> Grid:
    return assemble(grid, use_mapping=False)


def mapped_tile_abstraction(grid: Grid) -> Grid:
    return assemble(grid, use_mapping=True)


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "dominant_fill": dominant_fill_abstraction,
    "mapped_tiles": mapped_tile_abstraction,
}


def evaluate_abstraction(name: str, fn: Callable[[Grid], Grid], dataset: Dict[str, Sequence[dict]]) -> None:
    print(f"== {name} ==")
    for split in ("train", "test", "generated", "arc_gen"):
        cases = dataset.get(split)
        if not cases:
            continue

        matches = 0
        first_fail: Optional[int] = None
        total = len(cases)

        predictions: List[Grid] = []
        has_refs = cases[0].get("output") is not None

        for idx, case in enumerate(cases):
            predicted = fn(case["input"])
            predictions.append(predicted)
            expected = case.get("output")
            if expected is None:
                continue
            if predicted == expected:
                matches += 1
            elif first_fail is None:
                first_fail = idx

        if has_refs:
            info = f"{matches}/{total} correct"
            if first_fail is not None and matches != total:
                info += f"; first fail at index {first_fail}"
        else:
            sample = predictions[0] if predictions else []
            if sample:
                info = f"sample output shape {len(sample)}x{len(sample[0]) if sample[0] else 0}"
            else:
                info = "no prediction produced"
        print(f"  {split}: {info}")


def main() -> None:
    dataset = load_dataset()
    for name, fn in ABSTRACTIONS.items():
        evaluate_abstraction(name, fn, dataset)


if __name__ == "__main__":
    main()
