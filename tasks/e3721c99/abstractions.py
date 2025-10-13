"""Abstraction experiments for ARC task e3721c99."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, List

import importlib.util


SOLVER_PATH = Path(__file__).resolve().parent / "arc2_samples" / "e3721c99.py"
_spec = importlib.util.spec_from_file_location("e3721c99", SOLVER_PATH)
_module = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_module)
solve_e3721c99 = _module.solve_e3721c99


def load_dataset() -> dict:
    path = Path(__file__).resolve().parent / "arc2_samples" / "e3721c99.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def identity_solver(grid: List[List[int]]) -> List[List[int]]:
    return [row[:] for row in grid]


def holes_classifier_solver(grid: List[List[int]]) -> List[List[int]]:
    return solve_e3721c99(grid)


def evaluate_solver(name: str, solver: Callable[[List[List[int]]], List[List[int]]], data: dict) -> None:
    train = data.get("train", [])
    total = len(train)
    correct = 0
    first_fail = None
    total_pixels = 0
    matched_pixels = 0
    for idx, sample in enumerate(train):
        prediction = solver(sample["input"])
        target = sample["output"]
        is_match = prediction == target
        if is_match:
            correct += 1
        elif first_fail is None:
            first_fail = idx
        for row_pred, row_gold in zip(prediction, target):
            for cell_pred, cell_gold in zip(row_pred, row_gold):
                total_pixels += 1
                if cell_pred == cell_gold:
                    matched_pixels += 1
    pixel_acc = matched_pixels / total_pixels if total_pixels else 1.0
    print(f"{name:>24}: train {correct}/{total} | pixel_acc={pixel_acc:.3f} | first_fail={first_fail}")


def main() -> None:
    data = load_dataset()
    solvers = {
        "identity": identity_solver,
        "holes_classifier": holes_classifier_solver,
    }
    for name, solver in solvers.items():
        evaluate_solver(name, solver, data)


if __name__ == "__main__":
    main()
