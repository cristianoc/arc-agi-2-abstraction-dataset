"""Abstractions explored while solving ARC task 221dfab4."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

Grid = List[List[int]]
Sample = Dict[str, Grid]


def infer_palette(grid: Grid) -> Tuple[int, Tuple[int, ...], Tuple[int, ...]]:
    """Infer background, stripe columns (color 4), and non-background colors."""
    counts = Counter(value for row in grid for value in row)
    background = counts.most_common(1)[0][0]
    stripe_columns = tuple(
        c
        for c in range(len(grid[0]))
        if any(row[c] == 4 for row in grid)
    )
    object_colors = tuple(color for color in counts if color not in (background, 4))
    return background, stripe_columns, object_colors


def apply_stripe_projection(grid: Grid) -> Grid:
    """First abstraction: project the observed 3/4 stripe pattern onto 4-columns."""
    background, stripe_columns, _ = infer_palette(grid)
    result = [row[:] for row in grid]
    for c in stripe_columns:
        for r in range(len(grid)):
            phase = r % 6
            if phase == 0:
                result[r][c] = 3
            elif phase in (2, 4):
                result[r][c] = 4
            else:
                result[r][c] = background
    return result


def overlay_mod0_objects(grid: Grid) -> Grid:
    """Second abstraction: overwrite every 0 mod 6 row object cell with color 3."""
    _, stripe_columns, object_colors = infer_palette(grid)
    result = apply_stripe_projection(grid)
    height = len(grid)
    width = len(grid[0])
    stripe_set = set(stripe_columns)
    for r in range(0, height, 6):
        for c in range(width):
            if c in stripe_set:
                continue
            if grid[r][c] in object_colors:
                result[r][c] = 3
    return result


ABSTRACTIONS: Sequence[Tuple[str, Callable[[Grid], Grid]]] = (
    ("stripe_projection", apply_stripe_projection),
    ("stripe_plus_mod0_objects", overlay_mod0_objects),
)


def load_samples(kind: str) -> List[Sample]:
    """Load train/test data from disk."""
    repo_root = Path(__file__).resolve().parents[1]
    task_path = repo_root / "arc2_samples" / "221dfab4.json"
    data = json.loads(task_path.read_text())
    if kind == "arc_gen":
        arc_gen_path = repo_root / "arc2_samples" / "221dfab4_arcgen.json"
        if not arc_gen_path.exists():
            return []
        data = json.loads(arc_gen_path.read_text())
        return data.get("train", [])
    return data.get(kind, [])


def evaluate_split(
    name: str,
    samples: Iterable[Sample],
    transform: Callable[[Grid], Grid],
) -> Tuple[int, int, Optional[int]]:
    """Return (matches, total, first_failure_index) for the given split."""
    matches = 0
    total = 0
    first_failure = None
    for idx, sample in enumerate(samples):
        total += 1
        output = transform(sample["input"])
        expected = sample.get("output")
        if expected is None:
            continue
        if output == expected:
            matches += 1
        elif first_failure is None:
            first_failure = idx
    return matches, total, first_failure


def run_evaluation() -> None:
    train_samples = load_samples("train")
    test_samples = load_samples("test")
    arc_gen_samples = load_samples("arc_gen")

    for name, transform in ABSTRACTIONS:
        print(f"Abstraction: {name}")
        for split_name, samples in (
            ("train", train_samples),
            ("test", test_samples),
            ("arc-gen", arc_gen_samples),
        ):
            matches, total, first_failure = evaluate_split(split_name, samples, transform)
            if not samples:
                print(f"  {split_name}: no cases")
                continue
            if split_name == "test":
                print(f"  {split_name}: produced {total} predictions (no ground truth)")
            else:
                status = f"{matches}/{total} matches"
                if matches == total:
                    print(f"  {split_name}: {status}")
                else:
                    print(
                        f"  {split_name}: {status} (first failure at index {first_failure})"
                    )
        print()


if __name__ == "__main__":
    run_evaluation()
