"""Abstractions explored for ARC task 4c416de3."""

from __future__ import annotations

import json
import sys
from importlib import import_module
from pathlib import Path
from typing import Callable, Iterable, List, Sequence


TASK_PATH = Path(__file__).resolve().parent / "arc2_samples" / "4c416de3.json"
sys.path.append(str(Path(__file__).resolve().parent.parent))
SOLVER = import_module("analysis.arc2_samples.4c416de3")


def _load_samples() -> dict:
    with TASK_PATH.open() as fh:
        return json.load(fh)


def identity(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    return [list(row) for row in grid]


def corner_hooks(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    return SOLVER.solve_4c416de3(grid)


ABSTRACTIONS: dict[str, Callable[[Sequence[Sequence[int]]], List[List[int]]]] = {
    "identity": identity,
    "corner_hooks": corner_hooks,
}


def _first_failure(preds: Iterable[List[List[int]]], targets: Iterable[Sequence[Sequence[int]]]) -> int | None:
    for idx, (pred, target) in enumerate(zip(preds, targets)):
        if pred != [list(row) for row in target]:
            return idx
    return None


def _match_ratio(preds: Iterable[List[List[int]]], targets: Iterable[Sequence[Sequence[int]]]) -> float:
    total = correct = 0
    for pred, target in zip(preds, targets):
        total += 1
        if pred == [list(row) for row in target]:
            correct += 1
    return correct / total if total else 0.0


def evaluate() -> None:
    samples = _load_samples()
    train = samples.get("train", [])
    test = samples.get("test", [])

    for name, func in ABSTRACTIONS.items():
        train_preds = [func(case["input"]) for case in train]
        train_targets = [case["output"] for case in train]
        test_preds = [func(case["input"]) for case in test]
        ratio = _match_ratio(train_preds, train_targets)
        failure = _first_failure(train_preds, train_targets)

        print(f"[{name}] train accuracy: {ratio:.2%}")
        if failure is None:
            print("  first failure: none")
        else:
            print(f"  first failure at train[{failure}]")

        if test:
            shape_set = {(len(pred), len(pred[0])) for pred in test_preds}
            print(f"  test predictions available (shapes: {sorted(shape_set)})")
        print()


if __name__ == "__main__":
    evaluate()
