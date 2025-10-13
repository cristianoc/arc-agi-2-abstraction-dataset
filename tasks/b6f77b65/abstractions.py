"""Abstractions explored for ARC task b6f77b65.

Each abstraction is implemented as a pure function and wired into a lightweight
evaluation harness that reports match rates across the available dataset splits
(train/test/arc-gen) together with the first failing index when ground-truth
outputs are provided.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple


Grid = List[List[int]]

TASK_PATH = Path(__file__).with_name("arc2_samples") / "b6f77b65.json"
SOLVER_PATH = Path(__file__).with_name("arc2_samples") / "b6f77b65.py"


def _load_solver_module():
    spec = importlib.util.spec_from_file_location("taskb6f77b65_solver", SOLVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_solver_module = _load_solver_module()
COLOR_TO_SEGMENT = _solver_module.COLOR_TO_SEGMENT
CURRENT_MAPPING = _solver_module.MAPPING
FINAL_SOLVER = _solver_module.solve_b6f77b65


OLD_PATTERN_OFFSET = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0],
    [5, 5, 5],
    [0, 0, 0],
    [0, 0, 0],
    [7, 0, 2],
    [7, 0, 2],
    [7, 0, 2],
    [7, 7, 7],
]


def load_task() -> dict:
    """Load the ARC task description from disk."""

    return json.loads(TASK_PATH.read_text())


def identity_abstraction(grid: Grid) -> Grid:
    """Return the grid unchanged (baseline sanity check)."""

    return [row[:] for row in grid]


def _digit_segment_key(grid: Grid, digit_idx: int) -> str:
    start = digit_idx * 3
    letters = {
        COLOR_TO_SEGMENT[val]
        for row in grid
        for val in row[start:start + 3]
        if val in COLOR_TO_SEGMENT
    }
    return ''.join(sorted(letters))


def _digit_block(grid: Grid, digit_idx: int) -> List[List[int]]:
    start = digit_idx * 3
    return [row[start:start + 3] for row in grid]


def _apply_mapping(grid: Grid, mapping: Dict[Tuple[int, str, Optional[str]], List[List[int]]]) -> Grid:
    key_letter = COLOR_TO_SEGMENT.get(grid[0][0])
    height = len(grid)
    width = len(grid[0]) if height else 0
    result = [[0] * width for _ in range(height)]

    digit_count = width // 3
    for idx in range(digit_count):
        start = idx * 3
        seg_key = _digit_segment_key(grid, idx)
        pattern = mapping.get((idx, seg_key, key_letter))
        if pattern is None and key_letter is None:
            pattern = mapping.get((idx, seg_key, None))
        if pattern is None:
            pattern = _digit_block(grid, idx)
        for r in range(height):
            result[r][start:start + 3] = pattern[r][:]

    return result


def segment_template_lookup_v0(grid: Grid) -> Grid:
    """First attempt: template lookup with the misaligned (2,'adf','e') pattern."""

    mapping = {key: [row[:] for row in value] for key, value in CURRENT_MAPPING.items()}
    mapping[(2, 'adf', 'e')] = [row[:] for row in OLD_PATTERN_OFFSET]
    return _apply_mapping(grid, mapping)


def segment_template_lookup_v1(grid: Grid) -> Grid:
    """Corrected template lookup that matches the final solver."""

    return _apply_mapping(grid, CURRENT_MAPPING)


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": identity_abstraction,
    "segment_lookup_v0": segment_template_lookup_v0,
    "segment_lookup_v1": segment_template_lookup_v1,
    "solver": FINAL_SOLVER,
}


def render(grid: Grid) -> str:
    palette = "0123456789abcdef"
    return '\n'.join(''.join(palette[val] for val in row) for row in grid)


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
                        print(f"  {split}: no ground truth; sample 0 prediction:\n{render(prediction)}")
                    continue

                total_with_gt += 1
                if prediction == expected:
                    matches += 1
                elif first_failure is None:
                    first_failure = idx

            if total_with_gt:
                rate = matches / total_with_gt * 100.0
                print(
                    f"  {split}: {matches}/{total_with_gt} matched "
                    f"({rate:.1f}%), first failure: {first_failure}"
                )
        print()


if __name__ == "__main__":
    evaluate_abstractions()
