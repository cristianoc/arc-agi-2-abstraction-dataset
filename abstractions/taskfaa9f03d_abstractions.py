"""Abstraction playground for ARC task faa9f03d."""

from __future__ import annotations

import json
import os
import sys
from collections import deque
from typing import Callable, Iterable, List, Sequence, Tuple

sys.path.append(os.getcwd())
from analysis.arc2_samples.faa9f03d import solve_faa9f03d


SPECIAL_COLORS = {2, 4}
FOCUS_COLORS = (1, 3, 6, 7)


def load_dataset() -> dict:
    json_path = os.path.join(os.getcwd(), "analysis", "arc2_samples", "faa9f03d.json")
    with open(json_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def preprocess_grid(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    h = len(grid)
    w = len(grid[0])
    out = [list(row) for row in grid]
    for r in range(h):
        for c in range(w):
            if out[r][c] in SPECIAL_COLORS:
                out[r][c] = nearest_replacement(grid, r, c)
    return out


def nearest_replacement(grid: Sequence[Sequence[int]], sr: int, sc: int) -> int:
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
            val = grid[nr][nc]
            if val != 0 and val not in SPECIAL_COLORS:
                return val
            queue.append((nr, nc))
    return 0


def bridging_solver(grid: Sequence[Sequence[int]], gap: int = 3) -> List[List[int]]:
    """Row/column gap closure with bounded span."""

    base = preprocess_grid(grid)
    out = [row[:] for row in base]
    h = len(base)
    w = len(base[0])

    colors = sorted({cell for row in base for cell in row if cell != 0})

    for color in colors:
        # row-level closure
        for r in range(h):
            cols = [c for c in range(w) if base[r][c] == color]
            for a, b in zip(cols, cols[1:]):
                if b - a - 1 <= gap:
                    for c in range(a, b + 1):
                        out[r][c] = color

        # column-level closure
        for c in range(w):
            rows = [r for r in range(h) if base[r][c] == color]
            for a, b in zip(rows, rows[1:]):
                if b - a - 1 <= gap:
                    for r in range(a, b + 1):
                        out[r][c] = color

    return out


def evaluate_abstractions() -> None:
    dataset = load_dataset()
    cases = {
        "bridge-g3": lambda grid: bridging_solver(grid, gap=3),
        "knn-1": solve_faa9f03d,
    }

    for name, solver in cases.items():
        print(f"=== {name} ===")
        for split in ("train", "test"):
            samples = dataset[split]
            if not samples:
                continue
            total = len(samples)
            successes = 0
            first_fail = None
            for idx, sample in enumerate(samples):
                grid = sample["input"]
                predicted = solver(grid)
                expected = sample.get("output")
                if expected is None:
                    continue
                if predicted == expected:
                    successes += 1
                elif first_fail is None:
                    first_fail = idx
            ratio = successes / total if total else 0.0
            print(f"  {split}: {ratio:.2%} (first fail: {first_fail})")


if __name__ == "__main__":
    evaluate_abstractions()
