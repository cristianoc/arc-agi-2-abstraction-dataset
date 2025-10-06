"""Abstraction experiments for ARC task b99e7126."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
import sys
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from analysis.arc2_samples.b99e7126 import solve_b99e7126

Grid = List[List[int]]
Cell = Tuple[Tuple[int, ...], ...]

DATA_PATH = Path(__file__).resolve().with_name('arc2_samples') / 'b99e7126.json'


def deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _split_into_tiles(grid: Grid) -> Tuple[List[List[Cell]], Counter]:
    rows = len(grid)
    cols = len(grid[0])
    cell_rows = (rows - 1) // 4
    cell_cols = (cols - 1) // 4
    tiles: List[List[Cell]] = []
    freq: Counter = Counter()
    for cr in range(cell_rows):
        row_tiles: List[Cell] = []
        rb = 1 + 4 * cr
        for cc in range(cell_cols):
            cb = 1 + 4 * cc
            tile = tuple(tuple(grid[rb + dr][cb:cb + 3]) for dr in range(3))
            row_tiles.append(tile)
            freq[tile] += 1
        tiles.append(row_tiles)
    return tiles, freq


def _minority_tile(freq: Counter) -> Optional[Cell]:
    if not freq:
        return None
    return min(freq.items(), key=lambda item: (item[1], item[0]))[0]


def _tile_mask(tile: Cell, selector) -> Set[Tuple[int, int]]:
    return {(r, c) for r in range(3) for c in range(3) if selector(tile[r][c])}


def _locate_window(coords: Sequence[Tuple[int, int]],
                   allowed_offsets: Set[Tuple[int, int]],
                   cell_rows: int,
                   cell_cols: int) -> Optional[Tuple[int, int]]:
    for r0 in range(cell_rows - 2):
        for c0 in range(cell_cols - 2):
            if all((cr - r0, cc - c0) in allowed_offsets for cr, cc in coords):
                return (r0, c0)
    return None


def _paint_tile(grid: Grid, tile: Cell, cr: int, cc: int) -> None:
    rb = 1 + 4 * cr
    cb = 1 + 4 * cc
    for dr in range(3):
        for dc in range(3):
            grid[rb + dr][cb + dc] = tile[dr][dc]


def identity_abstraction(grid: Grid) -> Grid:
    return deep_copy(grid)


def bounding_square_abstraction(grid: Grid) -> Grid:
    """First attempt: fill the entire 3x3 macro window with the minority tile."""
    result = deep_copy(grid)
    tiles, freq = _split_into_tiles(grid)
    target = _minority_tile(freq)
    if target is None:
        return result

    rows = len(tiles)
    cols = len(tiles[0])
    coords = [(cr, cc) for cr in range(rows) for cc in range(cols) if tiles[cr][cc] == target]
    if not coords:
        return result

    full_mask = {(r, c) for r in range(3) for c in range(3)}
    placement = _locate_window(coords, full_mask, rows, cols)
    if placement is None:
        return result

    r0, c0 = placement
    for dr in range(3):
        for dc in range(3):
            _paint_tile(result, target, r0 + dr, c0 + dc)
    return result


def majority_mask_abstraction(grid: Grid) -> Grid:
    """Final abstraction: honour the majority-colour mask inside the minority tile."""
    result = deep_copy(grid)
    tiles, freq = _split_into_tiles(grid)
    target = _minority_tile(freq)
    if target is None:
        return result

    cell_rows = len(tiles)
    cell_cols = len(tiles[0])
    coords = [(cr, cc) for cr in range(cell_rows) for cc in range(cell_cols) if tiles[cr][cc] == target]
    if not coords:
        return result

    colour_counts = Counter(value for row in target for value in row)
    majority_colour = colour_counts.most_common(1)[0][0]
    mask = _tile_mask(target, lambda value: value == majority_colour)
    placement = _locate_window(coords, mask, cell_rows, cell_cols)
    if placement is None:
        return result

    r0, c0 = placement
    for dr, dc in mask:
        _paint_tile(result, target, r0 + dr, c0 + dc)
    return result


def final_abstraction(grid: Grid) -> Grid:
    return solve_b99e7126(grid)


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    'identity': identity_abstraction,
    'square_fill': bounding_square_abstraction,
    'mask_completion': majority_mask_abstraction,
    'solver': final_abstraction,
}


def evaluate_abstraction(name: str, fn: Callable[[Grid], Grid], data) -> None:
    per_split = {}
    first_fail: Optional[Tuple[str, int]] = None
    for split, cases in data.items():
        correct = 0
        total = 0
        for idx, sample in enumerate(cases):
            expected = sample.get('output')
            if expected is None:
                continue
            total += 1
            predicted = fn(sample['input'])
            if predicted == expected:
                correct += 1
            elif first_fail is None:
                first_fail = (split, idx)
        per_split[split] = (correct, total)
    status = all(correct == total for correct, total in per_split.values())
    summary = ' '.join(f"{split}:{correct}/{total}" for split, (correct, total) in per_split.items())
    if status:
        print(f"{name:14s} PASS [{summary}]")
    else:
        note = f" first_fail={first_fail}" if first_fail else ''
        print(f"{name:14s} FAIL [{summary}]{note}")


def main() -> None:
    data = json.loads(DATA_PATH.read_text())
    for name, fn in ABSTRACTIONS.items():
        evaluate_abstraction(name, fn, data)


if __name__ == '__main__':
    main()
