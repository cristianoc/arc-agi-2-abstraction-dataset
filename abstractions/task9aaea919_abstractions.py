"""Abstraction experiments for ARC task 9aaea919."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "arc2_samples" / "9aaea919.json"


Grid = List[List[int]]
Example = Dict[str, Grid]
Split = Sequence[Example]
Abstraction = Callable[[Grid], Grid]


def _load_cases() -> Dict[str, Split]:
    with DATA_PATH.open() as fh:
        raw = json.load(fh)
    return {
        "train": raw.get("train", []),
        "test": raw.get("test", []),
        "arc_gen": raw.get("generated", raw.get("arc_gen", [])),
    }


def _identity(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _load_solver() -> Callable[[Grid], Grid]:
    module_path = ROOT / "arc2_samples" / "9aaea919.py"
    spec = importlib.util.spec_from_file_location("task9aaea919_solver", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to import task solver module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module.solve_9aaea919  # type: ignore[attr-defined]


_solver = _load_solver()


def _instruction_driven(grid: Grid) -> Grid:
    return _solver(grid)


ABSTRACTIONS: Dict[str, Abstraction] = {
    "identity": _identity,
    "instruction_driven": _instruction_driven,
}


def _evaluate_split(abstraction: Abstraction, split: Split, key: str) -> Tuple[int, int, Optional[int]]:
    if not split:
        return 0, 0, None

    matches = 0
    first_failure: Optional[int] = None

    for idx, example in enumerate(split):
        inp = example["input"]
        expected = example.get("output")
        if expected is None:
            continue
        predicted = abstraction(inp)
        if predicted == expected:
            matches += 1
        elif first_failure is None:
            first_failure = idx

    total = sum(1 for ex in split if "output" in ex)
    return matches, total, first_failure


def run_abstractions() -> None:
    cases = _load_cases()
    for name, abstraction in ABSTRACTIONS.items():
        print(f"=== {name} ===")
        for split_name in ("train", "test", "arc_gen"):
            split = cases.get(split_name, [])
            if not split:
                print(f"  {split_name}: no cases")
                continue
            matches, total, first_failure = _evaluate_split(abstraction, split, split_name)
            if total == 0:
                print(f"  {split_name}: no ground truth (skipped)")
                continue
            summary = f"{matches}/{total}"
            failure = "nan" if first_failure is None else str(first_failure)
            print(f"  {split_name}: {summary} first_fail={failure}")
        print()


if __name__ == "__main__":
    run_abstractions()

