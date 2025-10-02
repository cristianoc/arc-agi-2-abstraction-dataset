"""Pattern-based solver for ARC-AGI-2 task 271d71e2."""

from __future__ import annotations

import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

# The transformation on this task appears to be local: the colour of each
# output cell depends on a small neighbourhood in the input grid.  We exploit
# this by memorising all 7x7 input patches from the training set together with
# their target colours, and fall back to a nearest-neighbour lookup (by Hamming
# distance) whenever an unseen patch is encountered at inference time.

PATCH_SIZE = 7
HALF = PATCH_SIZE // 2
DEFAULT_COLOR = 6

try:
    _DATA_PATH = Path(__file__).with_suffix(".json")
except NameError:  # pragma: no cover - fallback when executed via exec without __file__
    _DATA_PATH = Path("analysis/arc2_samples/271d71e2.json")


def _load_training_pairs() -> List[Tuple[List[List[int]], List[List[int]]]]:
    with _DATA_PATH.open() as fh:
        payload = json.load(fh)
    return [(sample["input"], sample["output"]) for sample in payload["train"]]


TRAINING_PAIRS = _load_training_pairs()


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


class _PatchMemory:
    """Memoises training patches and provides nearest-neighbour lookup."""

    def __init__(self) -> None:
        patch_to_colour: Dict[Tuple[int, ...], int] = {}
        patches_by_center: Dict[int, List[Tuple[Tuple[int, ...], int]]] = defaultdict(list)

        for inp, out in TRAINING_PAIRS:
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

    @lru_cache(maxsize=None)
    def infer_colour(self, patch: Tuple[int, ...]) -> int:
        """Return the memorised colour, or fall back to nearest neighbour."""

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


_MEMORY = _PatchMemory()


def solve_271d71e2(grid: List[List[int]]) -> List[List[int]]:
    rows = len(grid)
    cols = len(grid[0])
    result = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            patch = _get_patch(grid, r, c)
            result[r][c] = _MEMORY.infer_colour(patch)
    return result


p = solve_271d71e2
