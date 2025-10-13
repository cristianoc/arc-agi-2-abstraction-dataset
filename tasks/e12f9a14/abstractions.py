"""Abstractions explored for ARC task e12f9a14.

The module collects the successive reasoning pipelines that were tried while
fixing the task and provides a lightweight harness to compare them.
"""

from __future__ import annotations

import json
import runpy
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable, List, Sequence, Tuple

_MODULE = runpy.run_path(str(Path(__file__).parent / "arc2_samples" / "e12f9a14.py"))
DIGIT_TEMPLATE_VARIANTS = _MODULE["DIGIT_TEMPLATE_VARIANTS"]
solve_e12f9a14 = _MODULE["solve_e12f9a14"]

Grid = List[List[int]]
Template = Sequence[Tuple[int, int]]


def _clone(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _dominant_color(grid: Grid) -> int:
    counter = Counter()
    for row in grid:
        counter.update(row)
    return counter.most_common(1)[0][0]


def _components(grid: Grid) -> Iterable[Tuple[int, List[Tuple[int, int]]]]:
    height = len(grid)
    width = len(grid[0])
    seen = [[False] * width for _ in range(height)]
    for r in range(height):
        for c in range(width):
            if seen[r][c]:
                continue
            color = grid[r][c]
            stack = [(r, c)]
            seen[r][c] = True
            cells: List[Tuple[int, int]] = []
            while stack:
                rr, cc = stack.pop()
                cells.append((rr, cc))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not seen[nr][nc] and grid[nr][nc] == color:
                        seen[nr][nc] = True
                        stack.append((nr, nc))
            yield color, cells


UNION_OFFSETS = {
    color: tuple(sorted({offset for variant in variants for offset in variant}))
    for color, variants in DIGIT_TEMPLATE_VARIANTS.items()
}


def identity_abstraction(grid: Grid) -> Grid:
    """Return the grid unchanged (baseline)."""

    return _clone(grid)


def union_template_abstraction(grid: Grid) -> Grid:
    """Apply the union-of-offsets template without variant selection."""

    height = len(grid)
    width = len(grid[0])
    result = _clone(grid)
    background = _dominant_color(grid)

    for color, cells in _components(grid):
        if color == background or len(cells) != 4:
            continue

        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        if max(rows) - min(rows) != 1 or max(cols) - min(cols) != 1:
            continue

        offsets = UNION_OFFSETS.get(color)
        if not offsets:
            continue

        anchor_r, anchor_c = min(rows), min(cols)
        seed_cells = set(cells)
        for dr, dc in offsets:
            target_r = anchor_r + dr
            target_c = anchor_c + dc
            if 0 <= target_r < height and 0 <= target_c < width:
                if (target_r, target_c) in seed_cells or grid[target_r][target_c] == background:
                    result[target_r][target_c] = color

    return result


def variant_selector_abstraction(grid: Grid) -> Grid:
    """Delegate to the final collision-aware variant selection solver."""

    return solve_e12f9a14(grid)


ABSTRACTIONS: Sequence[Tuple[str, Callable[[Grid], Grid]]] = (
    ("identity", identity_abstraction),
    ("union", union_template_abstraction),
    ("variants", variant_selector_abstraction),
)


def _load_dataset() -> dict:
    data_path = Path(__file__).with_name("arc2_samples") / "e12f9a14.json"
    with data_path.open() as handle:
        return json.load(handle)


def evaluate_abstractions() -> None:
    dataset = _load_dataset()
    splits = ("train", "test", "arc_gen")

    for name, func in ABSTRACTIONS:
        print(f"=== {name} ===")
        for split in splits:
            pairs = dataset.get(split, [])
            if not pairs:
                print(f" {split}: no samples")
                continue

            has_ground_truth = all("output" in pair for pair in pairs)
            matches = 0
            first_fail = None

            for idx, pair in enumerate(pairs):
                prediction = func(pair["input"])
                if not has_ground_truth:
                    continue
                if prediction == pair["output"]:
                    matches += 1
                elif first_fail is None:
                    first_fail = idx

            if has_ground_truth:
                status = f"{matches}/{len(pairs)}"
                fail_str = "ok" if first_fail is None else f"{split}[{first_fail}]"
            else:
                status = "n/a"
                fail_str = "n/a"

            print(f" {split}: matches={status} first_fail={fail_str}")
        print()


if __name__ == "__main__":
    evaluate_abstractions()
