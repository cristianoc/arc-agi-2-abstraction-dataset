"""Abstraction experiments for ARC task 271d71e2."""

from __future__ import annotations

import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


TASK_ID = "271d71e2"
try:
    TASK_PATH = Path(__file__).with_name("arc2_samples") / f"{TASK_ID}.json"
except NameError:  # pragma: no cover - defensive fallback when executed without __file__
    TASK_PATH = Path("analysis/arc2_samples") / f"{TASK_ID}.json"


Grid = List[List[int]]

PATCH_SIZE = 7
HALF = PATCH_SIZE // 2
DEFAULT_COLOR = 6


def load_task() -> Dict:
    return json.loads(TASK_PATH.read_text())


def identity(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _get_patch(grid: Sequence[Sequence[int]], r: int, c: int) -> Tuple[int, ...]:
    rows = len(grid)
    cols = len(grid[0])
    patch: List[int] = []
    for dr in range(-HALF, HALF + 1):
        rr = r + dr
        for dc in range(-HALF, HALF + 1):
            cc = c + dc
            if 0 <= rr < rows and 0 <= cc < cols:
                patch.append(grid[rr][cc])
            else:
                patch.append(DEFAULT_COLOR)
    return tuple(patch)


class PatchMemory:
    """Helper that memorises training patches and supports lookups."""

    def __init__(self, samples: Iterable[Tuple[Grid, Grid]]) -> None:
        patch_to_colour: Dict[Tuple[int, ...], int] = {}
        patches_by_center: Dict[int, List[Tuple[Tuple[int, ...], int]]] = defaultdict(list)

        for inp, out in samples:
            rows = len(inp)
            cols = len(inp[0])
            for r in range(rows):
                for c in range(cols):
                    patch = _get_patch(inp, r, c)
                    colour = out[r][c]
                    patch_to_colour[patch] = colour
                    patches_by_center[patch[len(patch) // 2]].append((patch, colour))

        self._patch_to_colour = patch_to_colour
        self._patches_by_center = patches_by_center
        self._all_patches: List[Tuple[Tuple[int, ...], int]] = [
            entry for entries in patches_by_center.values() for entry in entries
        ]

    @staticmethod
    def _hamming(a: Tuple[int, ...], b: Tuple[int, ...]) -> int:
        return sum(x != y for x, y in zip(a, b))

    def infer_exact(self, patch: Tuple[int, ...]) -> int | None:
        return self._patch_to_colour.get(patch)

    @lru_cache(maxsize=None)
    def infer_with_nearest(self, patch: Tuple[int, ...]) -> int:
        direct = self._patch_to_colour.get(patch)
        if direct is not None:
            return direct

        center = patch[len(patch) // 2]
        candidates = self._patches_by_center.get(center, self._all_patches)

        best_dist = None
        best_colour = center
        for cand_patch, cand_colour in candidates:
            dist = self._hamming(patch, cand_patch)
            if dist == 0:
                return cand_colour
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best_colour = cand_colour
                if best_dist == 1:
                    break
        return best_colour


def _load_training_pairs() -> List[Tuple[Grid, Grid]]:
    task = load_task()
    return [(example["input"], example["output"]) for example in task["train"]]


TRAINING_PAIRS = _load_training_pairs()
PATCH_MEMORY = PatchMemory(TRAINING_PAIRS)


def patch_lookup_strict(grid: Grid) -> Grid:
    """Apply the memorised mapping; fall back to the original value."""

    rows = len(grid)
    cols = len(grid[0])
    result = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            patch = _get_patch(grid, r, c)
            colour = PATCH_MEMORY.infer_exact(patch)
            if colour is None:
                colour = grid[r][c]
            result[r][c] = colour
    return result


def patch_lookup_nearest(grid: Grid) -> Grid:
    """Memorised mapping with nearest-neighbour fallback (final solver)."""

    rows = len(grid)
    cols = len(grid[0])
    result = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            patch = _get_patch(grid, r, c)
            result[r][c] = PATCH_MEMORY.infer_with_nearest(patch)
    return result


ABSTRACTIONS = {
    "identity": identity,
    "patch_lookup_strict": patch_lookup_strict,
    "patch_lookup_nearest": patch_lookup_nearest,
}


def evaluate(task: Dict, name: str, fn) -> None:
    print(f"== {name} ==")
    for split in ("train", "test", "arc-gen"):
        examples = task.get(split, [])
        if not examples:
            continue

        total = sum(1 for ex in examples if "output" in ex)
        matches = 0
        first_failure = None

        for idx, example in enumerate(examples):
            prediction = fn(example["input"])
            target = example.get("output")
            if target is None:
                continue
            if prediction == target:
                matches += 1
            elif first_failure is None:
                first_failure = idx

        if total:
            print(
                f"  {split}: {matches}/{total} matches; first failure index: {first_failure}"
            )
        else:
            print(f"  {split}: {len(examples)} examples (no targets)")
    print()


if __name__ == "__main__":
    task = load_task()
    for name, fn in ABSTRACTIONS.items():
        evaluate(task, name, fn)
