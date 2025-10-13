"""Abstraction experiments for ARC task a32d8b75."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from arc2_samples.a32d8b75 import (
    BLOCK_TO_OUTPUT,
    TAIL_BLOCK_TO_OUTPUT,
    solve_a32d8b75,
)

Grid = List[List[int]]


def _trim_right(grid: Grid, offset: int = 6) -> Grid:
    return [row[offset:] for row in grid]


def abstraction_identity(grid: Grid) -> Grid:
    """Naïve baseline: drop the instruction columns and keep the rest."""
    return _trim_right(grid)


def abstraction_block_map_no_tail(grid: Grid) -> Grid:
    """Apply the 3-row instruction mapping but ignore leftover tail rows."""
    if not grid:
        return []

    trim_offset = 6
    macro_height = 3
    total_rows = len(grid)
    usable_rows = (total_rows // macro_height) * macro_height

    result = [list(row[trim_offset:]) for row in grid]

    for start in range(0, usable_rows, macro_height):
        key = tuple(tuple(grid[r][:trim_offset]) for r in range(start, start + macro_height))
        repl = BLOCK_TO_OUTPUT.get(key)
        if repl is None:
            continue
        for offset, repl_row in enumerate(repl):
            result[start + offset] = list(repl_row)

    return result


def abstraction_block_map_full(grid: Grid) -> Grid:
    """Final hybrid that also handles the leftover tail rows."""
    if not grid:
        return []

    trim_offset = 6
    macro_height = 3
    total_rows = len(grid)
    usable_rows = (total_rows // macro_height) * macro_height

    result = [list(row[trim_offset:]) for row in grid]

    for start in range(0, usable_rows, macro_height):
        key = tuple(tuple(grid[r][:trim_offset]) for r in range(start, start + macro_height))
        repl = BLOCK_TO_OUTPUT.get(key)
        if repl is None:
            continue
        for offset, repl_row in enumerate(repl):
            result[start + offset] = list(repl_row)

    if usable_rows < total_rows:
        tail_key = tuple(tuple(grid[r][:trim_offset]) for r in range(usable_rows, total_rows))
        tail_repl = TAIL_BLOCK_TO_OUTPUT.get(tail_key)
        if tail_repl is not None:
            for offset, repl_row in enumerate(tail_repl):
                result[usable_rows + offset] = list(repl_row)

    return result


def _load_dataset() -> dict:
    dataset_path = Path(__file__).resolve().parents[1] / "arc2_samples" / "a32d8b75.json"
    with dataset_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_optional(split_name: str) -> Iterable[dict]:
    base = Path(__file__).resolve().parents[1] / "arc2_samples"
    candidate = base / f"a32d8b75_{split_name}.json"
    if candidate.exists():
        with candidate.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    return []


def _compare(grida: Grid, gridb: Grid) -> bool:
    return grida == gridb


def _evaluate_split(name: str, samples: Iterable[dict], solver: Callable[[Grid], Grid]) -> tuple[int, int, int | None]:
    solved = 0
    total = 0
    first_fail: int | None = None
    for idx, sample in enumerate(samples):
        output = solver(sample["input"])
        if "output" not in sample:
            continue
        total += 1
        if _compare(output, sample["output"]):
            solved += 1
        elif first_fail is None:
            first_fail = idx
    return solved, total, first_fail


def run_evaluations() -> None:
    data = _load_dataset()
    extra = {"arcgen": _load_optional("arcgen")}

    abstractions: list[tuple[str, Callable[[Grid], Grid]]] = [
        ("identity", abstraction_identity),
        ("block_map_no_tail", abstraction_block_map_no_tail),
        ("block_map_full", abstraction_block_map_full),
        ("solver_module", solve_a32d8b75),
    ]

    for name, fn in abstractions:
        print(f"=== {name} ===")
        for split in ("train", "test"):
            samples = data.get(split, [])
            if not samples:
                continue
            solved, total, first_fail = _evaluate_split(split, samples, fn)
            if total == 0:
                print(f"{split:>5}: no labels (produced {len(samples)} outputs)")
            else:
                fail_display = "none" if first_fail is None else first_fail
                print(f"{split:>5}: {solved}/{total} exact; first_fail={fail_display}")
        for split, samples in extra.items():
            if not samples:
                continue
            solved, total, first_fail = _evaluate_split(split, samples, fn)
            if total == 0:
                print(f"{split:>5}: no labels (produced {len(samples)} outputs)")
            else:
                fail_display = "none" if first_fail is None else first_fail
                print(f"{split:>5}: {solved}/{total} exact; first_fail={fail_display}")
        print()


if __name__ == "__main__":
    run_evaluations()
