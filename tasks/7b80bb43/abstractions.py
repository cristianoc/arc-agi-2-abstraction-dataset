"""Abstraction experiments for ARC task 7b80bb43."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple

Grid = List[List[int]]

DATA_PATH = Path(__file__).resolve().parents[1] / "arc2_samples" / "7b80bb43.json"
SOLVER_PATH = DATA_PATH.with_suffix(".py")


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _color_counter(grid: Grid) -> Dict[int, int]:
    counter: Dict[int, int] = {}
    for row in grid:
        for value in row:
            counter[value] = counter.get(value, 0) + 1
    return counter


def _load_samples() -> Tuple[List[dict], List[dict], List[dict]]:
    with DATA_PATH.open() as fh:
        data = json.load(fh)
    return data["train"], data.get("test", []), data.get("arc_gen", [])


def identity_abstraction(grid: Grid) -> Grid:
    return _copy_grid(grid)


def column_snap_v0(grid: Grid) -> Grid:
    """Earlier attempt that straightens dominant columns without gap checks."""

    height = len(grid)
    width = len(grid[0]) if height else 0
    if not height or not width:
        return _copy_grid(grid)

    counts = _color_counter(grid)
    background = max(counts, key=counts.get)
    candidates = [color for color in counts if color != background]
    if not candidates:
        return _copy_grid(grid)

    foreground = max(candidates, key=lambda color: counts[color])
    mask = [[cell == foreground for cell in row] for row in grid]

    col_counts = [sum(mask[r][c] for r in range(height)) for c in range(width)]
    col_threshold = max(2, (height + 3) // 4)
    key_cols = [c for c, cnt in enumerate(col_counts) if cnt >= col_threshold]
    if not key_cols:
        key_cols = [c for c, _ in sorted(enumerate(col_counts), key=lambda item: item[1], reverse=True)[:1]]
    key_cols.sort()

    col_masks: Dict[int, List[bool]] = {}
    for col in key_cols:
        rows = [r for r in range(height) if mask[r][col]]
        if not rows:
            continue
        column_mask = [False] * height
        for r in range(rows[0], rows[-1] + 1):
            column_mask[r] = True
        col_masks[col] = column_mask

    result = [[background for _ in range(width)] for _ in range(height)]
    for col, column_mask in col_masks.items():
        for row in range(height):
            if column_mask[row]:
                result[row][col] = foreground

    row_counts = [sum(row) for row in mask]
    pivot_row = max(range(height), key=lambda r: row_counts[r])

    for row in range(height):
        segments: List[Tuple[int, int]] = []
        col = 0
        while col < width:
            if mask[row][col]:
                start = col
                while col + 1 < width and mask[row][col + 1]:
                    col += 1
                segments.append((start, col))
            col += 1

        if not segments:
            continue

        for start, end in segments:
            for col in range(start, end + 1):
                result[row][col] = foreground

        for (s1, e1), (s2, e2) in zip(segments, segments[1:]):
            gap = s2 - e1 - 1
            if gap <= 0 or gap > 3:
                continue
            if row != pivot_row:
                continue
            for col in range(e1 + 1, s2):
                result[row][col] = foreground

    return result


_solver_module = None


def _load_solver():
    global _solver_module
    if _solver_module is None:
        spec = importlib.util.spec_from_file_location("task7b80bb43", SOLVER_PATH)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        _solver_module = module
    return _solver_module


def column_snap_refined(grid: Grid) -> Grid:
    module = _load_solver()
    return module.solve_7b80bb43(grid)  # type: ignore[attr-defined]


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": identity_abstraction,
    "column_snap_v0": column_snap_v0,
    "column_snap_refined": column_snap_refined,
}


def _evaluate_split(split: Iterable[dict], fn: Callable[[Grid], Grid]) -> Tuple[int, int, int | None]:
    matches = 0
    total = 0
    first_failure: int | None = None

    for idx, sample in enumerate(split):
        pred = fn(sample["input"])
        expected = sample.get("output")
        if expected is None:
            continue
        total += 1
        if pred == expected:
            matches += 1
        elif first_failure is None:
            first_failure = idx

    return matches, total, first_failure


def _format_result(matches: int, total: int, first_failure: int | None) -> str:
    if total == 0:
        return "matches=n/a first_fail=-"
    fail_txt = "-" if first_failure is None else str(first_failure)
    return f"matches={matches}/{total} first_fail={fail_txt}"


def main() -> None:
    train, test, arc_gen = _load_samples()
    splits = {"train": train, "test": test, "arc_gen": arc_gen}

    for name, fn in ABSTRACTIONS.items():
        print(f"{name}:")
        for split_name, split in splits.items():
            matches, total, failure = _evaluate_split(split, fn)
            summary = _format_result(matches, total, failure)
            print(f"  {split_name:<7} {summary}")


if __name__ == "__main__":
    main()
