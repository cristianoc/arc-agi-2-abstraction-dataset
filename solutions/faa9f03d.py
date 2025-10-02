"""Nearest-neighbour classifier for ARC-AGI-2 task faa9f03d."""

from __future__ import annotations

import json
import os
from collections import deque
from typing import Iterable, List, Sequence, Tuple


# Colours that should inherit the closest non-special hue.
SPECIAL_COLORS = {2, 4}
# We only need detailed statistics for the dominant non-background colours.
FOCUS_COLORS = (1, 3, 6, 7)


def _load_training_samples() -> Tuple[List[Tuple[int, ...]], List[int]]:
    """Parse the JSON description and cache feature/label pairs."""

    json_path = os.path.join(os.getcwd(), "analysis", "arc2_samples", "faa9f03d.json")
    with open(json_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    features: List[Tuple[int, ...]] = []
    labels: List[int] = []

    for sample in payload["train"]:
        base = _preprocess_grid(sample["input"])
        target = sample["output"]
        h = len(base)
        w = len(base[0])
        for r in range(h):
            for c in range(w):
                features.append(_feature_vector(base, r, c))
                labels.append(target[r][c])

    return features, labels


def _preprocess_grid(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    """Return a mutable copy where special colours inherit the closest hue."""

    h = len(grid)
    w = len(grid[0])
    out = [list(row) for row in grid]

    for r in range(h):
        for c in range(w):
            if out[r][c] in SPECIAL_COLORS:
                out[r][c] = _nearest_replacement(grid, r, c)

    return out


def _nearest_replacement(grid: Sequence[Sequence[int]], sr: int, sc: int) -> int:
    """Breadth-first search for the closest non-special, non-zero colour."""

    h = len(grid)
    w = len(grid[0])
    seen = {(sr, sc)}
    queue: deque[Tuple[int, int]] = deque([(sr, sc)])

    while queue:
        r, c = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if not (0 <= nr < h and 0 <= nc < w) or (nr, nc) in seen:
                continue
            seen.add((nr, nc))
            value = grid[nr][nc]
            if value != 0 and value not in SPECIAL_COLORS:
                return value
            queue.append((nr, nc))

    # Fallback: nothing useful nearby.
    return 0


def _feature_vector(grid: Sequence[Sequence[int]], r: int, c: int) -> Tuple[int, ...]:
    """Compute a compact descriptor for (r, c)."""

    h = len(grid)
    w = len(grid[0])
    value = grid[r][c]

    row = grid[r]
    column = [grid[i][c] for i in range(h)]

    features = [r, c, value]

    for colour in FOCUS_COLORS:
        features.append(row.count(colour))
    for colour in FOCUS_COLORS:
        features.append(column.count(colour))

    left = grid[r][c - 1] if c > 0 else -1
    right = grid[r][c + 1] if c < w - 1 else -1
    up = grid[r - 1][c] if r > 0 else -1
    down = grid[r + 1][c] if r < h - 1 else -1
    features.extend((left, right, up, down))

    return tuple(features)


def _predict_colour(feature: Tuple[int, ...]) -> int:
    """1-NN classifier in the pre-computed feature space."""

    best_label = 0
    best_distance = None
    for train_feature, train_label in zip(TRAIN_FEATURES, TRAIN_LABELS):
        distance = sum(abs(a - b) for a, b in zip(feature, train_feature))
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_label = train_label
    return best_label


def solve_faa9f03d(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    """Use a nearest-neighbour model trained on the provided examples."""

    processed = _preprocess_grid(grid)
    h = len(processed)
    w = len(processed[0])

    result = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            feature = _feature_vector(processed, r, c)
            result[r][c] = _predict_colour(feature)
    return result


# Lazily initialise the training cache once per interpreter.
TRAIN_FEATURES, TRAIN_LABELS = _load_training_samples()


p = solve_faa9f03d
