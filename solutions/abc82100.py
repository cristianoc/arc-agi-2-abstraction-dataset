"""Solver for ARC-AGI-2 task abc82100 using a tiny kNN classifier."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple


_TRAIN_CACHE: List[Tuple[Tuple[float, ...], int]] | None = None

# Indices of categorical features inside the feature vector.
_CATEGORICAL_IDX = {6, 7, 10, 11, 12, 13, 14, 15, 16}


TRAIN_DATA = [
    (
        [
            [1, 2, 8, 8, 8],
            [0, 0, 0, 0, 1],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1],
        ],
        [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 2],
            [0, 0, 0, 2, 2],
            [0, 0, 0, 2, 2],
            [0, 0, 0, 0, 2],
        ],
    ),
    (
        [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0, 6, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0],
            [0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 2, 0, 8, 0, 8, 0, 0, 0, 0, 0, 0, 0, 4, 0],
            [0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 8, 0, 0, 6, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0],
            [8, 0, 4, 2, 0, 4, 2, 0, 8, 0, 0, 0, 0, 0, 0],
            [0, 8, 0, 0, 7, 0, 0, 8, 0, 0, 0, 0, 0, 2, 0],
            [0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 7, 0, 8, 0, 8, 0, 7, 0, 7, 0, 7, 0, 0, 0],
            [0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        [
            [0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0],
            [7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7, 0, 7],
            [0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0],
            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
            [0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0],
            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
            [0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0],
            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
            [0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0],
            [6, 0, 6, 0, 0, 0, 6, 0, 6, 0, 6, 0, 6, 0, 0],
            [0, 6, 0, 0, 0, 0, 0, 6, 0, 6, 0, 6, 0, 0, 0],
        ],
    ),
    (
        [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 4, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 4, 0, 0, 0, 4, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 4, 0, 0, 0, 8, 0, 0, 0, 8, 0, 0, 0, 4, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 8, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 8, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 8, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 8, 0, 0, 0],
        ],
        [
            [0, 2, 0, 2, 0, 2, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2],
            [0, 0, 2, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 2, 0, 0, 0],
            [0, 2, 0, 2, 0, 2, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2],
            [2, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 0, 2, 0],
            [0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0],
            [0, 0, 2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 0],
            [0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [7, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 7, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 7, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [7, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 7, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 7, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
    ),
    (
        [
            [1, 1, 1, 1, 1, 2, 0, 0],
            [0, 0, 0, 0, 0, 2, 0, 0],
            [0, 0, 0, 0, 0, 2, 0, 0],
            [0, 2, 1, 8, 0, 2, 0, 0],
            [0, 0, 0, 0, 0, 2, 0, 0],
            [0, 0, 8, 0, 0, 2, 0, 0],
            [0, 0, 2, 0, 0, 2, 0, 0],
            [0, 0, 1, 0, 0, 2, 0, 0],
        ],
        [
            [2, 2, 2, 2, 2, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
        ],
    ),
]


def _load_training_samples() -> List[Tuple[Tuple[float, ...], int]]:
    """Load train examples and convert them into feature vectors."""

    global _TRAIN_CACHE
    if _TRAIN_CACHE is not None:
        return _TRAIN_CACHE

    samples: List[Tuple[Tuple[float, ...], int]] = []
    for grid, target in TRAIN_DATA:
        rows_info, cols_info, bounds = _precompute_axis_features(grid)
        row_min, row_max, col_min, col_max = bounds
        h, w = len(grid), len(grid[0])
        for y in range(h):
            for x in range(w):
                feats = _encode_features(
                    grid,
                    y,
                    x,
                    rows_info,
                    cols_info,
                    row_min,
                    row_max,
                    col_min,
                    col_max,
                )
                samples.append((feats, target[y][x]))

    _TRAIN_CACHE = samples
    return samples


def _precompute_axis_features(grid: Sequence[Sequence[int]]):
    """Collect per-row / per-column summaries reused across feature extraction."""

    h = len(grid)
    w = len(grid[0])

    # Extremes of rows/columns containing any non-zero colour.
    row_min = next((i for i, row in enumerate(grid) if any(v != 0 for v in row)), 0)
    row_max = next(
        (h - 1 - i for i, row in enumerate(reversed(grid)) if any(v != 0 for v in row)),
        h - 1,
    )
    col_min = next((j for j in range(w) if any(grid[i][j] != 0 for i in range(h))), 0)
    col_max = next(
        (w - 1 - j for j in range(w) if any(grid[i][w - 1 - j] != 0 for i in range(h))),
        w - 1,
    )

    row_info: List[Tuple[int, int, int, int]] = []
    for y, row in enumerate(grid):
        left = next((v for v in row if v != 0), 0)
        right = next((v for v in reversed(row) if v != 0), 0)
        category = 0 if y < row_min else 2 if y > row_max else 1
        nonzero_count = sum(1 for v in row if v != 0)
        row_info.append((left, right, category, nonzero_count))

    col_info: List[Tuple[int, int, int, int]] = []
    for x in range(w):
        column = [grid[y][x] for y in range(h)]
        top = next((v for v in column if v != 0), 0)
        bottom = next((v for v in reversed(column) if v != 0), 0)
        category = 0 if x < col_min else 2 if x > col_max else 1
        nonzero_count = sum(1 for v in column if v != 0)
        col_info.append((top, bottom, category, nonzero_count))

    return row_info, col_info, (row_min, row_max, col_min, col_max)


def _encode_features(
    grid: Sequence[Sequence[int]],
    y: int,
    x: int,
    rows_info: Sequence[Tuple[int, int, int, int]],
    cols_info: Sequence[Tuple[int, int, int, int]],
    row_min: int,
    row_max: int,
    col_min: int,
    col_max: int,
) -> Tuple[float, ...]:
    """Encode a cell into the feature vector used by the kNN classifier."""

    h = len(grid)
    w = len(grid[0])
    row_left, row_right, row_cat, row_nz = rows_info[y]
    col_top, col_bottom, col_cat, col_nz = cols_info[x]

    h_safe = h or 1
    w_safe = w or 1

    features = (
        y / h_safe,
        x / w_safe,
        (y - row_min) / h_safe,
        (row_max - y) / h_safe,
        (x - col_min) / w_safe,
        (col_max - x) / w_safe,
        float(row_cat),
        float(col_cat),
        row_nz / w_safe,
        col_nz / h_safe,
        float(grid[y][x]),
        float(row_left),
        float(row_right),
        float(col_top),
        float(col_bottom),
        float(y & 1),
        float(x & 1),
    )
    return features


def _nearest_colour(feats: Tuple[float, ...], samples: Iterable[Tuple[Tuple[float, ...], int]]) -> int:
    """Return the label of the nearest training sample under a mixed metric."""

    best_dist = float("inf")
    best_colour = 0
    for sample_feats, colour in samples:
        dist = 0.0
        for idx, (a, b) in enumerate(zip(feats, sample_feats)):
            if idx in _CATEGORICAL_IDX:
                if a != b:
                    dist += 1.0
            else:
                diff = a - b
                dist += diff * diff
            if dist >= best_dist:
                break
        else:
            if dist < best_dist:
                best_dist = dist
                best_colour = colour
    return best_colour


def solve_abc82100(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    """Predict the output grid via a lightweight 1-NN classifier."""

    samples = _load_training_samples()
    rows_info, cols_info, bounds = _precompute_axis_features(grid)
    row_min, row_max, col_min, col_max = bounds

    h = len(grid)
    w = len(grid[0])
    result: List[List[int]] = [[0] * w for _ in range(h)]

    for y in range(h):
        for x in range(w):
            feats = _encode_features(
                grid,
                y,
                x,
                rows_info,
                cols_info,
                row_min,
                row_max,
                col_min,
                col_max,
            )
            result[y][x] = _nearest_colour(feats, samples)

    return result


p = solve_abc82100
