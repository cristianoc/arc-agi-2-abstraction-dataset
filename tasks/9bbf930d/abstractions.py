"""Abstraction experiments for ARC task 9bbf930d."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable, List


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "arc2_samples" / "9bbf930d.json"


def load_data():
    with DATA_PATH.open() as fh:
        raw = json.load(fh)
    return raw.get("train", []), raw.get("test", [])


def clone(grid: List[List[int]]) -> List[List[int]]:
    return [row[:] for row in grid]


def dominant_color(sequence: Iterable[int]) -> int | None:
    counts = Counter(val for val in sequence if val not in (6, 7))
    if not counts:
        return None
    ranked = counts.most_common()
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return None
    return ranked[0][0]


def row_non_count(row: Iterable[int]) -> int:
    return sum(1 for val in row if val not in (6, 7))


# --- Abstraction pipelines -------------------------------------------------


def identity_solver(grid: List[List[int]]) -> List[List[int]]:
    return clone(grid)


def row_separator_solver(grid: List[List[int]]) -> List[List[int]]:
    """Only move the left-edge 6 for repeating row bands."""
    result = clone(grid)
    rows = len(grid)
    cols = len(grid[0])
    row_dom = [dominant_color(row) for row in grid]
    row_non = [row_non_count(row) for row in grid]

    for r in range(1, rows - 1):
        if row_non[r] > 4:
            continue
        up_dom = row_dom[r - 1]
        down_dom = row_dom[r + 1]
        if up_dom is None or down_dom is None or up_dom != down_dom:
            continue
        result[r][0] = 7
        if result[r][cols - 1] == 7:
            result[r][cols - 1] = 6
    return result


_FULL_SOLVER = None


def full_solver(grid: List[List[int]]) -> List[List[int]]:
    global _FULL_SOLVER
    if _FULL_SOLVER is None:
        import importlib.util

        solver_path = ROOT / "arc2_samples" / "9bbf930d.py"
        spec = importlib.util.spec_from_file_location("task_9bbf930d", solver_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)  # type: ignore[assignment]
        _FULL_SOLVER = module.solve_9bbf930d
    return _FULL_SOLVER(grid)


# --- Evaluation harness ----------------------------------------------------


def evaluate(solver: Callable[[List[List[int]]], List[List[int]]], train, test):
    train_matches = 0
    first_fail = None
    for idx, pair in enumerate(train):
        pred = solver(pair["input"])
        if pred == pair["output"]:
            train_matches += 1
        elif first_fail is None:
            first_fail = idx
    return train_matches, first_fail


def main():
    train, test = load_data()
    solvers = [
        ("identity", identity_solver),
        ("row_separator", row_separator_solver),
        ("full", full_solver),
    ]

    for name, solver in solvers:
        train_matches, first_fail = evaluate(solver, train, test)
        total = len(train)
        status = "PASS" if train_matches == total else "FAIL"
        print(f"[{name}] {status} train={train_matches}/{total}")
        if first_fail is not None:
            print(f"  first failing train index: {first_fail}")
        else:
            print("  first failing train index: None (all matched)")
        # Run on test grids to ensure solver executes end-to-end
        if test:
            for t_idx, puzzle in enumerate(test):
                _ = solver(puzzle["input"]) if isinstance(puzzle, dict) else solver(puzzle)
        print()


if __name__ == "__main__":
    main()
