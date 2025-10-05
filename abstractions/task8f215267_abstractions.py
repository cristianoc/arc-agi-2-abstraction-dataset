"""Abstractions explored for ARC task 8f215267."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple


Grid = List[List[int]]
Block = Tuple[int, int, int, int, int]

TASK_PATH = Path(__file__).with_name("arc2_samples") / "8f215267.json"
SOLVER_PATH = Path(__file__).with_name("arc2_samples") / "8f215267.py"


def _load_solver_module():
    spec = importlib.util.spec_from_file_location("task8f215267_solver", SOLVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_solver = _load_solver_module()
PATCH_STRIPES = _solver.PATCH_STRIPES


def load_task() -> dict:
    """Load the ARC task description from disk."""

    return json.loads(TASK_PATH.read_text())


def identity(grid: Grid) -> Grid:
    """Return the grid unchanged (baseline sanity check)."""

    return [row[:] for row in grid]


def _run_pipeline(
    grid: Grid, infer_stripes: Callable[[Grid, Tuple[int, int, int, int, int, int]], int]
) -> Grid:
    background = _solver._most_common_color(grid)
    blocks = list(_solver._find_blocks(grid, background))
    height = len(grid)
    width = len(grid[0]) if height else 0
    work = [row[:] for row in grid]
    inside = [[False] * width for _ in range(height)]

    for color, rmin, rmax, cmin, cmax in blocks:
        inner_cols = range(cmin + 1, cmax)
        inner_rows = range(rmin + 1, rmax)
        for r in inner_rows:
            for c in inner_cols:
                work[r][c] = background

        block = (color, rmin, rmax, cmin, cmax, background)
        stripe_count = infer_stripes(grid, block)
        _solver._paint_stripes(work, color, rmin, rmax, cmin, cmax, stripe_count)

    if blocks:
        right_limit = max(cmax for _color, _rmin, _rmax, _cmin, cmax in blocks)
        for r in range(height):
            for c in range(right_limit + 1, width):
                work[r][c] = background

    for color, rmin, rmax, cmin, cmax in blocks:
        for r in range(rmin, rmax + 1):
            for c in range(cmin, cmax + 1):
                inside[r][c] = True

    for r in range(height):
        for c in range(width):
            if not inside[r][c] and work[r][c] != background:
                work[r][c] = background

    return work


def _infer_v0(grid: Grid, block: Tuple[int, int, int, int, int, int]) -> int:
    color, _rmin, _rmax, cmin, cmax, background = block
    inner_width = cmax - cmin - 1
    candidates = _solver._candidate_positions(inner_width)
    if not candidates:
        return 0

    patch = _solver._extract_patch(grid, block)
    unique = {
        value
        for row in patch
        for value in row
        if value not in (background, color)
    }
    row_hits = sum(
        any(value not in (background, color) for value in row) for row in patch
    )
    estimate = max(len(unique), row_hits // 2)
    return min(len(candidates), estimate)


def _infer_v1(grid: Grid, block: Tuple[int, int, int, int, int, int]) -> int:
    color, _rmin, _rmax, cmin, cmax, background = block
    inner_width = cmax - cmin - 1
    candidates = _solver._candidate_positions(inner_width)
    if not candidates:
        return 0

    patch = _solver._extract_patch(grid, block)
    canon = _solver._canonical_patch(patch, color, background)
    if canon in PATCH_STRIPES:
        return min(len(candidates), PATCH_STRIPES[canon])
    return _infer_v0(grid, block)


def striped_frames_v0(grid: Grid) -> Grid:
    """First attempt: rely on colour diversity in the noisy patch."""

    return _run_pipeline(grid, _infer_v0)


def striped_frames_v1(grid: Grid) -> Grid:
    """Final abstraction: canonical patch lookup with fitted templates."""

    return _run_pipeline(grid, _infer_v1)


FINAL_SOLVER = _solver.solve_8f215267

ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": identity,
    "striped_frames_v0": striped_frames_v0,
    "striped_frames_v1": striped_frames_v1,
    "solver": FINAL_SOLVER,
}


def render(grid: Grid) -> str:
    palette = "0123456789abcdef"
    return "\n".join("".join(palette[val] for val in row) for row in grid)


def evaluate_abstractions() -> None:
    data = load_task()
    splits: Sequence[str] = ("train", "test", "arc_gen")

    for name, abstraction in ABSTRACTIONS.items():
        print(f"[{name}]")
        for split in splits:
            samples = data.get(split)
            if not samples:
                continue

            matches = 0
            total_with_gt = 0
            first_failure: Optional[int] = None

            for idx, sample in enumerate(samples):
                prediction = abstraction(sample["input"])
                expected = sample.get("output")
                if expected is None:
                    if idx == 0:
                        print(
                            f"  {split}: no ground truth; sample 0 prediction:\n{render(prediction)}"
                        )
                    continue

                total_with_gt += 1
                if prediction == expected:
                    matches += 1
                elif first_failure is None:
                    first_failure = idx

            if total_with_gt:
                rate = matches / total_with_gt * 100.0
                failure_text = (
                    f" first failure at index {first_failure}"
                    if first_failure is not None
                    else ""
                )
                print(f"  {split}: {rate:.2f}% ({matches}/{total_with_gt}){failure_text}")


if __name__ == "__main__":
    evaluate_abstractions()

