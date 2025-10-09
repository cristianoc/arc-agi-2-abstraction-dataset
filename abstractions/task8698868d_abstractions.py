"""Abstraction experiments for ARC task 8698868d."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "arc2_samples" / "8698868d.json"
SOLVER_PATH = ROOT / "arc2_samples" / "8698868d.py"


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


def _load_solver_module():
    spec = importlib.util.spec_from_file_location("task8698868d_solver", SOLVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to import solver module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


_solver_module = _load_solver_module()


def _column_priority_v1(grid: Grid) -> Grid:
    base = _solver_module._most_common_color(grid)
    components = _solver_module._extract_components(grid, ignore=[base])
    backgrounds, shapes = _solver_module._classify_components(components)
    if not backgrounds or len(backgrounds) != len(shapes):
        return [row[:] for row in grid]
    grouped, rows, cols = _solver_module._group_backgrounds(backgrounds)
    assignment = _solver_module._assign_shapes(grouped, shapes, row_weight=1.0, col_weight=5.0)
    return _solver_module._render_solution(grid, grouped, assignment, rows, cols)


def _column_priority_v2(grid: Grid) -> Grid:
    return _solver_module.solve_8698868d(grid)


ABSTRACTIONS: Dict[str, Abstraction] = {
    "identity": _identity,
    "column_priority_v1": _column_priority_v1,
    "column_priority_v2": _column_priority_v2,
}


def _evaluate_split(abstraction: Abstraction, split: Split) -> Tuple[int, int, Optional[int]]:
    if not split:
        return 0, 0, None

    matches = 0
    total = 0
    first_failure: Optional[int] = None

    for idx, example in enumerate(split):
        if "output" not in example:
            continue
        total += 1
        predicted = abstraction(example["input"])
        if predicted == example["output"]:
            matches += 1
        elif first_failure is None:
            first_failure = idx

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
            matches, total, first_failure = _evaluate_split(abstraction, split)
            if total == 0:
                print(f"  {split_name}: no ground truth (skipped)")
                continue
            summary = f"{matches}/{total}"
            failure = "nan" if first_failure is None else str(first_failure)
            print(f"  {split_name}: {summary} first_fail={failure}")
        print()


if __name__ == "__main__":
    run_abstractions()

