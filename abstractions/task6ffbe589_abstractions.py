"""Abstraction playground for ARC task 6ffbe589."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, List, Sequence, Tuple

ARTHUR_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ARTHUR_ROOT / "arc2_samples" / "6ffbe589.json"

Grid = List[List[int]]


def _load_samples() -> Tuple[List[dict], List[dict]]:
    data = json.loads(DATA_PATH.read_text())
    return data["train"], data.get("test", [])


# ---------------------------------------------------------------------------
# Shared helpers


def _extract_main_square(grid: Grid) -> Grid:
    row_counts = [sum(val != 0 for val in row) for row in grid]
    top, bottom = _longest_nonzero_run(row_counts)
    rows = grid[top : bottom + 1]

    col_counts = [sum(row[col] != 0 for row in rows) for col in range(len(rows[0]))]
    left, right = _longest_nonzero_run(col_counts)

    return [row[left : right + 1] for row in rows]


def _longest_nonzero_run(counts: Sequence[int]) -> Tuple[int, int]:
    values = list(counts)
    best_len = -1
    best = (0, len(values) - 1)
    start = None
    for idx, count in enumerate(values + [0]):
        if count > 0:
            if start is None:
                start = idx
        elif start is not None:
            length = idx - start
            if length > best_len:
                best_len = length
                best = (start, idx - 1)
            start = None
    return best


def _rotate_cw(block: Grid) -> Grid:
    size = len(block)
    return [[block[size - 1 - r][c] for r in range(size)] for c in range(size)]


def _rotate_ccw(block: Grid) -> Grid:
    size = len(block)
    return [[block[c][size - 1 - r] for c in range(size)] for r in range(size)]


def _rotate_180(block: Grid) -> Grid:
    size = len(block)
    return [[block[size - 1 - r][size - 1 - c] for c in range(size)] for r in range(size)]


def _mask(block: Grid, color: int) -> Grid:
    return [[1 if cell == color else 0 for cell in row] for row in block]


def _apply_mask(target: Grid, mask: Grid, color: int, *, overwrite: bool = True) -> None:
    for r, row in enumerate(mask):
        for c, flag in enumerate(row):
            if flag and (overwrite or target[r][c] == 0):
                target[r][c] = color


# ---------------------------------------------------------------------------
# Candidate abstractions


def abstraction_crop(grid: Grid) -> Grid:
    return _extract_main_square(grid)


def abstraction_rotate_ccw(grid: Grid) -> Grid:
    block = _extract_main_square(grid)
    return _rotate_ccw(block)


def abstraction_rotate_cw_with_edges(grid: Grid) -> Grid:
    block = _extract_main_square(grid)
    rotated = _rotate_cw(block)
    rotated[0] = block[0][:]
    rotated[-1] = block[-1][:]
    for r in range(len(block)):
        rotated[r][0] = block[r][0]
        rotated[r][-1] = block[r][-1]
    return rotated


def abstraction_color_masks(grid: Grid) -> Grid:
    block = _extract_main_square(grid)
    size = len(block)
    result = [[0] * size for _ in range(size)]

    mask3 = _mask(block, 3)
    mask8 = _mask(block, 8)
    mask6 = _mask(block, 6)

    mask3_rot = _rotate_cw(mask3)
    mask8_rot = _rotate_180(mask8)

    _apply_mask(result, mask3_rot, 3)
    _apply_mask(result, mask8_rot, 8, overwrite=False)
    _apply_mask(result, mask6, 6, overwrite=False)

    return result


def abstraction_final(grid: Grid) -> Grid:
    module = __import__('arc2_samples.6ffbe589', fromlist=['solve_6ffbe589'])
    return module.solve_6ffbe589(grid)


ABSTRACTIONS: List[Tuple[str, Callable[[Grid], Grid]]] = [
    ("crop_only", abstraction_crop),
    ("rotate_ccw", abstraction_rotate_ccw),
    ("rotate_cw_with_edges", abstraction_rotate_cw_with_edges),
    ("color_masks", abstraction_color_masks),
    ("final_hybrid", abstraction_final),
]


def _evaluate(split: List[dict], func: Callable[[Grid], Grid]) -> Tuple[int, int, int]:
    hits = 0
    first_fail = -1
    for idx, sample in enumerate(split):
        predicted = func(sample["input"])
        if predicted == sample["output"]:
            hits += 1
        elif first_fail == -1:
            first_fail = idx
    return hits, len(split), first_fail


def main() -> None:
    train, test = _load_samples()
    for name, func in ABSTRACTIONS:
        train_hits, train_total, train_fail = _evaluate(train, func)
        test_hits, test_total, test_fail = _evaluate(test, func) if test else (0, 0, -1)

        parts = [
            f"train {train_hits}/{train_total}",
            f"test {test_hits}/{test_total}" if test_total else "test n/a",
        ]
        summary = ", ".join(parts)
        detail = []
        if train_hits != train_total and train_fail != -1:
            detail.append(f"first train miss @ {train_fail}")
        if test_total and test_hits != test_total and test_fail != -1:
            detail.append(f"first test miss @ {test_fail}")
        tail = f" ({'; '.join(detail)})" if detail else ""
        print(f"{name:>20}: {summary}{tail}")


if __name__ == "__main__":
    main()
