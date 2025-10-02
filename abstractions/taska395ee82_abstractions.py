"""Abstraction experiments for ARC-AGI-2 task a395ee82."""

from __future__ import annotations

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Callable, Iterable, List


TASK_PATH = Path(__file__).with_name("arc2_samples") / "a395ee82.json"
SOLVER_PATH = TASK_PATH.with_suffix(".py")


Grid = List[List[int]]


spec = spec_from_file_location("task_a395ee82_solver", SOLVER_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f"Unable to load solver module from {SOLVER_PATH}")
solver_module = module_from_spec(spec)
spec.loader.exec_module(solver_module)
solve_a395ee82 = solver_module.solve_a395ee82


def load_task() -> dict:
    with TASK_PATH.open() as fp:
        return json.load(fp)


def abstraction_identity(grid: Grid) -> Grid:
    """Baseline that leaves the grid unchanged."""
    return [row[:] for row in grid]


def abstraction_template_transfer(grid: Grid) -> Grid:
    """Final abstraction that copies the learned template onto the marker grid."""
    return solve_a395ee82(grid)


ABSTRACTIONS: Iterable[tuple[str, Callable[[Grid], Grid]]] = (
    ("identity", abstraction_identity),
    ("template_transfer", abstraction_template_transfer),
)


def evaluate() -> None:
    data = load_task()
    splits = (
        ("train", data.get("train", [])),
        ("test", data.get("test", [])),
        ("arc-gen", data.get("arc_gen", [])),
    )

    for name, fn in ABSTRACTIONS:
        print(f"== {name} ==")
        for split_name, examples in splits:
            if not examples:
                continue
            has_output = "output" in examples[0]
            if has_output:
                mismatches: List[int] = []
                for idx, ex in enumerate(examples):
                    pred = fn(ex["input"])
                    if pred != ex["output"]:
                        mismatches.append(idx)
                solved = len(examples) - len(mismatches)
                accuracy = solved / len(examples) * 100
                if mismatches:
                    first_failure = mismatches[0]
                    print(f" {split_name}: {accuracy:.2f}% match, first failure at index {first_failure}")
                else:
                    print(f" {split_name}: 100.00% match, all cases solved")
            else:
                sample = fn(examples[0]["input"])
                print(
                    f" {split_name}: no targets provided; sample prediction has shape "
                    f"{len(sample)}x{len(sample[0])}"
                )
        print()


if __name__ == "__main__":
    evaluate()
