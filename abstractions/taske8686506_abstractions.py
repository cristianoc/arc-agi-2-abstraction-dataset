"""Abstraction experiments for ARC task e8686506.

We log a few lightweight transformations that were explored while looking
for a consistent rule.  The harness compares each abstraction against
all known grids (train + evaluation test) and prints the match rate and
first failure index for quick inspection.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable, List, Sequence, Tuple

# Ensure the project root is importable when executing this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from analysis.arc2_samples.e8686506 import solve_e8686506

Grid = List[List[int]]
Dataset = Sequence[Tuple[Grid, Grid]]

DATA_PATH = Path("../data/arc_agi_2/evaluation/e8686506.json")


def load_dataset() -> Dataset:
    data = json.loads(DATA_PATH.read_text())
    samples: list[Tuple[Grid, Grid]] = []
    for split in ("train", "test"):
        for sample in data.get(split, []):
            samples.append((sample["input"], sample["output"]))
    return samples


def bounding_box(grid: Grid) -> Tuple[int, int, int, int, int]:
    h, w = len(grid), len(grid[0])
    counts = Counter()
    for row in grid:
        counts.update(row)
    background = counts.most_common(1)[0][0]
    coords = [(r, c) for r in range(h) for c in range(w) if grid[r][c] != background]
    if not coords:
        return background, 0, h - 1, 0, w - 1
    min_r = min(r for r, _ in coords)
    max_r = max(r for r, _ in coords)
    min_c = min(c for _, c in coords)
    max_c = max(c for _, c in coords)
    return background, min_r, max_r, min_c, max_c


def dedup_row_signature(grid: Grid) -> Tuple[Tuple[int, ...], ...]:
    background, min_r, max_r, min_c, max_c = bounding_box(grid)
    sequences: List[Tuple[int, ...]] = []
    for r in range(min_r, max_r + 1):
        row = grid[r]
        seq: List[int] = []
        last = None
        for c in range(min_c, max_c + 1):
            colour = row[c]
            if colour == background:
                continue
            if colour != last:
                seq.append(colour)
                last = colour
        if seq:
            tup = tuple(seq)
            if not sequences or sequences[-1] != tup:
                sequences.append(tup)
    return tuple(sequences)


def quantile_projection(grid: Grid, width: int = 5) -> Grid:
    """Compress the bbox into *width* vertical stripes using majority colour."""

    background, min_r, max_r, min_c, max_c = bounding_box(grid)
    width_span = max_c - min_c + 1
    if width_span <= 0:
        return [[background] * width]
    boundaries = [min_c + round(i * width_span / width) for i in range(width + 1)]
    boundaries[0] = min_c
    boundaries[-1] = max_c + 1
    result: List[List[int]] = []
    for r in range(min_r, max_r + 1):
        row_out: List[int] = []
        has_foreground = False
        for b0, b1 in zip(boundaries, boundaries[1:]):
            colours = [grid[r][c] for c in range(b0, b1) if grid[r][c] != background]
            if colours:
                colour = Counter(colours).most_common(1)[0][0]
                has_foreground = True
            else:
                colour = background
            row_out.append(colour)
        if has_foreground:
            result.append(row_out)
    return result or [[background] * width]


def stripe_profile(grid: Grid) -> Grid:
    """Profile that keeps only the leftmost/rightmost colours per row."""

    background, min_r, max_r, min_c, max_c = bounding_box(grid)
    rows: List[List[int]] = []
    for r in range(min_r, max_r + 1):
        row = grid[r]
        colours = [row[c] for c in range(min_c, max_c + 1) if row[c] != background]
        if not colours:
            continue
        profile = [colours[0], colours[len(colours) // 2], colours[-1]]
        rows.append([profile[2], profile[0], profile[1], profile[0], profile[2]])
    # deduplicate consecutive rows
    result: List[List[int]] = []
    for row in rows:
        if not result or result[-1] != row:
            result.append(row)
    return result


ABSTRACTIONS: dict[str, Callable[[Grid], Grid]] = {
    "quantile_projection": quantile_projection,
    "stripe_profile": stripe_profile,
    "signature_lookup": solve_e8686506,
}


def score_solver(name: str, fn: Callable[[Grid], Grid], dataset: Dataset) -> Tuple[int, int, int]:
    matches = 0
    first_failure = None
    for idx, (inp, expected) in enumerate(dataset):
        pred = fn(inp)
        if pred == expected:
            matches += 1
        elif first_failure is None:
            first_failure = idx
    return matches, len(dataset), -1 if first_failure is None else first_failure


def main() -> None:
    dataset = load_dataset()
    print(f"Loaded {len(dataset)} grids from {DATA_PATH}")
    for name, solver in ABSTRACTIONS.items():
        matches, total, first_failure = score_solver(name, solver, dataset)
        pct = matches / total * 100
        failure_str = "all-match" if first_failure == -1 else f"first-fail={first_failure}"
        print(f"{name:20s} : {pct:6.2f}% ({matches}/{total}) {failure_str}")


if __name__ == "__main__":
    main()
