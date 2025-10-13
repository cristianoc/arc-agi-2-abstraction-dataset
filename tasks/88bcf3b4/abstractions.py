"""Abstraction experiments for ARC task 88bcf3b4."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Sequence

import importlib.util

def _load_solver_module():
    solver_path = Path(__file__).with_name("arc2_samples") / "88bcf3b4.py"
    spec = importlib.util.spec_from_file_location("solver_88bcf3b4", solver_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load solver module from {solver_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


solver_mod = _load_solver_module()

Grid = List[List[int]]


def identity_abstraction(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def path_projection_abstraction(grid: Grid) -> Grid:
    return solver_mod.solve_88bcf3b4(grid)


ABSTRACTIONS: dict[str, Callable[[Grid], Grid]] = {
    "identity": identity_abstraction,
    "path_projection": path_projection_abstraction,
}


@dataclass
class EvalResult:
    name: str
    split: str
    total: int
    exact_matches: int
    first_failure: Optional[int]
    avg_pixel_accuracy: float


def pixel_accuracy(a: Grid, b: Grid) -> float:
    total = 0
    matches = 0
    for row_a, row_b in zip(a, b):
        for cell_a, cell_b in zip(row_a, row_b):
            total += 1
            if cell_a == cell_b:
                matches += 1
    return matches / total if total else 1.0


def evaluate_split(name: str, samples: Sequence[dict], fn: Callable[[Grid], Grid]) -> EvalResult:
    exact = 0
    first_failure = None
    pixel_scores: List[float] = []

    for idx, sample in enumerate(samples):
        prediction = fn(sample["input"])
        if "output" not in sample:
            # Test split lacks references.
            continue
        target = sample["output"]
        if prediction == target:
            exact += 1
        else:
            if first_failure is None:
                first_failure = idx
        pixel_scores.append(pixel_accuracy(prediction, target))

    total = sum(1 for sample in samples if "output" in sample)
    avg_pixel = sum(pixel_scores) / len(pixel_scores) if pixel_scores else 1.0
    return EvalResult(name, split=name.split(":")[-1], total=total, exact_matches=exact,
                      first_failure=first_failure, avg_pixel_accuracy=avg_pixel)


def load_dataset() -> dict:
    path = Path(__file__).with_name("arc2_samples").joinpath("88bcf3b4.json")
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text())


def describe_predictions(split: str, samples: Sequence[dict], fn: Callable[[Grid], Grid]) -> None:
    for idx, sample in enumerate(samples):
        pred = fn(sample["input"])
        dims = (len(pred), len(pred[0]))
        print(f"  {split}[{idx}] -> dims={dims}")


def main() -> None:
    data = load_dataset()
    for name, fn in ABSTRACTIONS.items():
        print(f"=== Abstraction: {name} ===")
        train_result = evaluate_split("train", data["train"], fn)
        print(
            f"  train: exact={train_result.exact_matches}/{train_result.total}, "
            f"pixel={train_result.avg_pixel_accuracy:.3f}, first_fail={train_result.first_failure}"
        )
        if data.get("test"):
            print("  test predictions:")
            describe_predictions("test", data["test"], fn)
        print()


if __name__ == "__main__":
    main()
