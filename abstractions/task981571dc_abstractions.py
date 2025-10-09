"""Abstraction experiments for ARC task 981571dc."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple

import numpy as np


DATA_PATH = Path(__file__).resolve().parents[1] / "arc2_samples" / "981571dc.json"


def _load_samples() -> Tuple[List[dict], List[dict], List[dict]]:
    with DATA_PATH.open() as fh:
        data = json.load(fh)
    return data["train"], data.get("test", []), data.get("arc_gen", [])


def identity_abstraction(grid: List[List[int]]) -> List[List[int]]:
    return [row[:] for row in grid]


def mirror_nonzero_abstraction(grid: List[List[int]]) -> List[List[int]]:
    arr = np.array(grid, dtype=int)
    n = arr.shape[0]
    arr = arr.copy()
    for i in range(n):
        for j in range(n):
            if arr[i, j] == 0 and arr[j, i] != 0:
                arr[i, j] = arr[j, i]
    return arr.tolist()


def _complete_rows(arr: np.ndarray, allow_columns: bool) -> Tuple[np.ndarray, bool]:
    n = arr.shape[0]
    arr = arr.copy()
    changed = False

    for i in range(n):
        row = arr[i]
        mask = row != 0
        if mask.all():
            continue

        candidates: List[Tuple[int, int, int, np.ndarray]] = []

        for j in range(n):
            if j == i:
                continue
            other = arr[j]
            if np.all(other[mask] == row[mask]):
                zero_count = int(np.sum(other == 0))
                candidates.append((zero_count, 0, j, other.copy()))

        if allow_columns:
            for j in range(n):
                col = arr[:, j]
                if np.all(col[mask] == row[mask]):
                    zero_count = int(np.sum(col == 0))
                    candidates.append((zero_count, 1, j, col.copy()))

        if not candidates:
            continue

        _, _, _, source = min(candidates, key=lambda item: (item[0], item[1], item[2]))
        before = row.copy()
        row[~mask] = source[~mask]
        if not np.array_equal(before, row):
            changed = True

    return arr, changed


def _iterative_completion(arr: np.ndarray, allow_columns: bool) -> np.ndarray:
    arr = arr.copy()
    while True:
        arr, ch1 = _complete_rows(arr, allow_columns)
        arr_t, ch2 = _complete_rows(arr.T, allow_columns)
        arr = arr_t.T
        if not (ch1 or ch2):
            break
    return arr


def _enforce_symmetry(arr: np.ndarray) -> np.ndarray:
    n = arr.shape[0]
    arr = arr.copy()
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i, j] == 0 and arr[j, i] != 0:
                arr[i, j] = arr[j, i]
            elif arr[j, i] == 0 and arr[i, j] != 0:
                arr[j, i] = arr[i, j]
    return arr


def row_match_abstraction(grid: List[List[int]]) -> List[List[int]]:
    arr = np.array(grid, dtype=int)
    arr = _iterative_completion(arr, allow_columns=False)
    arr = _enforce_symmetry(arr)
    return arr.tolist()


def row_col_match_abstraction(grid: List[List[int]]) -> List[List[int]]:
    arr = np.array(grid, dtype=int)
    arr = _iterative_completion(arr, allow_columns=True)
    arr = _enforce_symmetry(arr)
    return arr.tolist()


ABSTRACTIONS: Dict[str, Callable[[List[List[int]]], List[List[int]]]] = {
    "identity": identity_abstraction,
    "mirror_nonzero": mirror_nonzero_abstraction,
    "row_match": row_match_abstraction,
    "row_col_match": row_col_match_abstraction,
}


def _evaluate_split(split: Iterable[dict], fn: Callable[[List[List[int]]], List[List[int]]]) -> Tuple[int, int, int | None]:
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
    splits = {
        "train": train,
        "test": test,
        "arc_gen": arc_gen,
    }

    for name, fn in ABSTRACTIONS.items():
        print(f"{name}:")
        for split_name, split in splits.items():
            matches, total, failure = _evaluate_split(split, fn)
            summary = _format_result(matches, total, failure)
            print(f"  {split_name:<7} {summary}")
        print()


if __name__ == "__main__":
    main()
