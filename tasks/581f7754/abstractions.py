"""Abstraction experiments for ARC task 581f7754."""

from __future__ import annotations

import json
from collections.abc import Callable
from importlib import util
from pathlib import Path
from typing import Any

Grid = list[list[int]]

_REPO_ROOT = Path(__file__).resolve().parent
_DATA_PATH = _REPO_ROOT / "arc2_samples" / "581f7754.json"
_SOLVER_PATH = _REPO_ROOT / "arc2_samples" / "581f7754.py"

_spec = util.spec_from_file_location("solver581f7754", _SOLVER_PATH)
_solver = util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_solver)  # type: ignore[assignment]


def _deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def identity_abstraction(grid: Grid) -> Grid:
    """Baseline that returns the grid unchanged."""
    return _deep_copy(grid)


def column_anchor_alignment(grid: Grid) -> Grid:
    """Align components using anchor-driven column/row targets (no refinement)."""
    background = _solver.most_common_color(grid)
    components = _solver.extract_components(grid, background)
    color_targets, _ = _solver.determine_color_targets(grid, components, background)
    shifts = _solver.compute_shifts(components, color_targets)
    return _solver.apply_transforms(grid, components, shifts, background)


def full_alignment(grid: Grid) -> Grid:
    """Final solver with row refinement heuristics."""
    background = _solver.most_common_color(grid)
    components = _solver.extract_components(grid, background)
    color_targets, anchor_coords = _solver.determine_color_targets(grid, components, background)
    shifts = _solver.compute_shifts(components, color_targets)
    _solver.refine_row_targets(components, shifts, color_targets, anchor_coords, len(grid[0]))
    return _solver.apply_transforms(grid, components, shifts, background)


ABSTRACTIONS: list[tuple[str, Callable[[Grid], Grid]]] = [
    ("identity", identity_abstraction),
    ("column_anchor", column_anchor_alignment),
    ("full_alignment", full_alignment),
]


def _load_data() -> dict[str, list[dict[str, Any]]]:
    with _DATA_PATH.open() as f:
        return json.load(f)


def _format_grid(grid: Grid) -> str:
    return "\n".join("".join(str(v) for v in row) for row in grid)


def evaluate_abstraction(func: Callable[[Grid], Grid], data: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for split in ("train", "test"):
        cases = data.get(split, [])
        correct = 0
        failure_index: int | None = None
        outputs: list[Grid] = []
        for idx, case in enumerate(cases):
            pred = func(case["input"])
            outputs.append(pred)
            if "output" in case:
                if pred == case["output"]:
                    correct += 1
                elif failure_index is None:
                    failure_index = idx
        if cases and "output" in cases[0]:
            summary[split] = {
                "total": len(cases),
                "correct": correct,
                "failure": failure_index,
                "outputs": outputs,
            }
        else:
            summary[split] = {"total": len(cases), "correct": None, "failure": None, "outputs": outputs}
    return summary


if __name__ == "__main__":
    data = _load_data()
    for name, func in ABSTRACTIONS:
        print(f"== {name} ==")
        results = evaluate_abstraction(func, data)
        train_res = results["train"]
        if train_res["correct"] is not None:
            total = train_res["total"]
            correct = train_res["correct"]
            failure = train_res["failure"] if train_res["failure"] is not None else "-"
            acc = correct / total if total else 0.0
            print(f"  train: {correct}/{total} ({acc:.2%}) first failure: {failure}")
        else:
            print("  train: no ground truth")
        test_res = results["test"]
        if test_res["correct"] is not None:
            total = test_res["total"]
            correct = test_res["correct"]
            failure = test_res["failure"] if test_res["failure"] is not None else "-"
            acc = correct / total if total else 0.0
            print(f"  test:  {correct}/{total} ({acc:.2%}) first failure: {failure}")
        else:
            print("  test:  outputs only (no ground truth)")
        failure_idx = train_res.get("failure")
        if failure_idx is not None:
            case = data["train"][failure_idx]
            pred = train_res["outputs"][failure_idx]
            print(f"    first failure example train[{failure_idx}]:")
            print("    expected:\n" + _format_grid(case["output"]))
            print("    predicted:\n" + _format_grid(pred))
    # Print test outputs for the final abstraction to aid manual inspection.
    final_outputs = evaluate_abstraction(full_alignment, data)["test"]["outputs"]
    for idx, grid in enumerate(final_outputs):
        print(f"-- final test output #{idx} --")
        print(_format_grid(grid))
