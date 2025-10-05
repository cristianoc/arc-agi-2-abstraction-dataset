"""Abstraction experiments for ARC task 136b0064."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Callable, List


DATA_PATH = Path(__file__).resolve().parent / "arc2_samples" / "136b0064.json"
SOLVER_PATH = Path(__file__).resolve().parent / "arc2_samples" / "136b0064.py"


def load_solver():
    spec = importlib.util.spec_from_file_location("task136b0064", SOLVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.solve_136b0064


SOLVE = load_solver()


def abstraction_identity(grid: List[List[int]]) -> List[List[int]]:
    """Copy the right partition without further interpretation."""
    return [row[8:] for row in grid]


def abstraction_digit_bars(grid: List[List[int]]) -> List[List[int]]:
    """Final bar-based digit abstraction implemented in the solver."""
    return SOLVE(grid)


ABSTRACTIONS: List[tuple[str, Callable[[List[List[int]]], List[List[int]]]]] = [
    ("identity_right", abstraction_identity),
    ("digit_bars", abstraction_digit_bars),
]


def evaluate():
    with DATA_PATH.open() as f:
        data = json.load(f)

    for name, fn in ABSTRACTIONS:
        train_matches = []
        for idx, case in enumerate(data["train"]):
            pred = fn(case["input"])
            ok = pred == case["output"]
            train_matches.append(ok)
            if not ok:
                first_failure = idx
                break
        else:
            first_failure = None

        test_matches = []
        for idx, case in enumerate(data.get("test", [])):
            pred = fn(case["input"])
            expected = case.get("output")
            test_matches.append(expected is not None and pred == expected)

        total = len(train_matches)
        passed = sum(train_matches)
        print(f"Abstraction: {name}")
        print(f"  train: {passed}/{total}")
        if first_failure is not None:
            print(f"  first failing train index: {first_failure}")
        if test_matches:
            print(f"  test outputs known: {sum(test_matches)}/{len(test_matches)}")
        print()


if __name__ == "__main__":
    evaluate()
