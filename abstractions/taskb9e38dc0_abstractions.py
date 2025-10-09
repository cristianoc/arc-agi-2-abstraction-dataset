"""Abstraction experiments for ARC task b9e38dc0."""

from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path
from typing import Callable, Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from arc2_samples.b9e38dc0 import solve_b9e38dc0


Grid = List[List[int]]


def load_task() -> dict:
    path = Path("arc2_samples/b9e38dc0.json")
    return json.loads(path.read_text())


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def identity_abstraction(grid: Grid) -> Grid:
    return copy_grid(grid)


def naive_component_fill(grid: Grid) -> Grid:
    counts = {}
    for row in grid:
        for value in row:
            counts[value] = counts.get(value, 0) + 1
    background = max(counts, key=lambda c: counts[c])
    candidates = sorted(((counts[c], c) for c in counts if c != background))
    if not candidates:
        return copy_grid(grid)
    seed_color = candidates[0][1]
    h = len(grid)
    w = len(grid[0])
    visited = [[False] * w for _ in range(h)]
    queue = deque()
    for r in range(h):
        for c in range(w):
            if grid[r][c] == seed_color:
                visited[r][c] = True
                queue.append((r, c))
    while queue:
        r, c = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr = r + dr
            nc = c + dc
            if 0 <= nr < h and 0 <= nc < w and not visited[nr][nc] and grid[nr][nc] == background:
                visited[nr][nc] = True
                queue.append((nr, nc))
    result = copy_grid(grid)
    for r in range(h):
        for c in range(w):
            if grid[r][c] == background and visited[r][c]:
                result[r][c] = seed_color
    return result


def wedge_abstraction(grid: Grid) -> Grid:
    return solve_b9e38dc0(grid)


Abstraction = Callable[[Grid], Grid]


def first_mismatch(samples: Iterable[dict], transform: Abstraction) -> int | None:
    for idx, example in enumerate(samples):
        transform_result = transform(example["input"])
        expected = example.get("output")
        if expected is None:
            continue
        if transform_result != expected:
            return idx
    return None


def evaluate(transform: Abstraction, data: dict) -> dict:
    stats = {}
    for split in ("train", "test"):
        samples = data.get(split, [])
        mismatch = first_mismatch(samples, transform)
        stats[split] = {
            "total": len(samples),
            "first_mismatch": mismatch,
        }
    return stats


def main() -> None:
    data = load_task()
    abstractions = {
        "identity": identity_abstraction,
        "naive_component_fill": naive_component_fill,
        "segmented_wedge": wedge_abstraction,
    }
    for name, fn in abstractions.items():
        stats = evaluate(fn, data)
        print(f"Abstraction: {name}")
        for split, split_stats in stats.items():
            total = split_stats["total"]
            mismatch = split_stats["first_mismatch"]
            status = "ok" if mismatch is None else f"fail@{mismatch}"
            print(f"  {split}: {status} (n={total})")
        print()


if __name__ == "__main__":
    main()
