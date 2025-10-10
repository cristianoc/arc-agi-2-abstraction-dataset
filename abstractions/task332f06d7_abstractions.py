"""Abstraction experiments for ARC task 332f06d7."""

from __future__ import annotations

import json
import importlib.util
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "arc2_samples" / "332f06d7.json"

DIRECTIONS = ((-1, 0, "up"), (1, 0, "down"), (0, -1, "left"), (0, 1, "right"))


Grid = List[List[int]]
Example = dict
Solver = Callable[[Grid], Grid]


def load_examples(path: Path) -> dict:
    return json.loads(path.read_text())


def bbox(cells: Sequence[Tuple[int, int]]) -> Tuple[int, int, int, int]:
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    return min(rows), min(cols), max(rows), max(cols)


def centre(box: Tuple[int, int, int, int]) -> Tuple[float, float]:
    r0, c0, r1, c1 = box
    return (r0 + r1) / 2.0, (c0 + c1) / 2.0


def adjacency(grid: Grid, cells: Iterable[Tuple[int, int]], target: int = 3) -> set[str]:
    h, w = len(grid), len(grid[0])
    adj: set[str] = set()
    for r, c in cells:
        for dr, dc, name in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w:
                if grid[nr][nc] == target:
                    adj.add(name)
            else:
                adj.add(name)
    return adj


def materialise_box(box: Tuple[int, int, int, int]) -> set[Tuple[int, int]]:
    r0, c0, r1, c1 = box
    return {(r, c) for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)}


def collect(grid: Grid, colour: int) -> List[Tuple[int, int]]:
    return [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == colour]


def identity_solver(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def always_swap_to_color2(grid: Grid) -> Grid:
    """Move the zero block directly to the colour-2 component."""

    zeros = collect(grid, 0)
    twos = collect(grid, 2)
    if not zeros or not twos:
        return [row[:] for row in grid]

    zero_box = bbox(zeros)
    two_box = bbox(twos)
    out = [row[:] for row in grid]

    for r, c in materialise_box(zero_box):
        out[r][c] = 1

    for r, c in materialise_box(two_box):
        out[r][c] = 0

    return out


def threshold_solver(grid: Grid, *, threshold: float) -> Grid:
    """Relocate the zero block when a good 1-block candidate is sufficiently central."""

    zeros = collect(grid, 0)
    ones = collect(grid, 1)
    twos = collect(grid, 2)
    if not zeros or not ones or not twos:
        return [row[:] for row in grid]

    zero_box = bbox(zeros)
    one_box = bbox(ones)
    two_box = bbox(twos)
    zero_h = zero_box[2] - zero_box[0] + 1
    zero_w = zero_box[3] - zero_box[1] + 1
    one_center = centre(one_box)
    two_center = centre(two_box)
    color2_cells = materialise_box(two_box)
    color2_adj = adjacency(grid, color2_cells)
    missing = {name for _, _, name in DIRECTIONS} - color2_adj
    color2_dist_one = abs(two_center[0] - one_center[0]) + abs(two_center[1] - one_center[1])

    h, w = len(grid), len(grid[0])
    best_candidate: Optional[Tuple[float, float, Tuple[int, int]]] = None

    for top in range(h - zero_h + 1):
        for left in range(w - zero_w + 1):
            block = [grid[r][c] for r in range(top, top + zero_h) for c in range(left, left + zero_w)]
            if len(set(block)) != 1 or block[0] != 1:
                continue
            cells = materialise_box((top, left, top + zero_h - 1, left + zero_w - 1))
            adj = adjacency(grid, cells)
            if missing and not missing <= adj:
                continue
            if len(adj) != len(color2_adj):
                continue
            centre_row = top + (zero_h - 1) / 2.0
            centre_col = left + (zero_w - 1) / 2.0
            dist_one = abs(centre_row - one_center[0]) + abs(centre_col - one_center[1])
            dist_two = abs(centre_row - two_center[0]) + abs(centre_col - two_center[1])
            candidate = (dist_one, dist_two, (top, left))
            if best_candidate is None or candidate < best_candidate:
                best_candidate = candidate

    zero_cells = materialise_box(zero_box)
    target_box = two_box

    if best_candidate is not None:
        dist_one, _, pos = best_candidate
        if color2_dist_one - dist_one >= threshold:
            top, left = pos
            target_box = (top, left, top + zero_h - 1, left + zero_w - 1)

    out = [row[:] for row in grid]
    for r, c in zero_cells:
        out[r][c] = 1
    for r, c in materialise_box(target_box):
        out[r][c] = 0
    return out


def final_solver(grid: Grid) -> Grid:
    return threshold_solver(grid, threshold=5.0)


def evaluate(fn: Solver, examples: Sequence[Example]) -> Tuple[int, int, Optional[int]]:
    correct = 0
    first_fail: Optional[int] = None
    for idx, pair in enumerate(examples):
        pred = fn(pair["input"])
        if "output" not in pair:
            continue
        if pred == pair["output"]:
            correct += 1
        elif first_fail is None:
            first_fail = idx
    total = sum(1 for pair in examples if "output" in pair)
    return correct, total, first_fail


def main() -> None:
    task = load_examples(TASK_PATH)
    splits = {
        "train": task["train"],
        "test": task["test"],
    }

    arc_gen_path = ROOT / "analysis" / "arc_gen" / "332f06d7.json"
    if arc_gen_path.exists():
        splits["arc-gen"] = load_examples(arc_gen_path)["test"]

    abstractions = {
        "identity": identity_solver,
        "swap_to_color2": always_swap_to_color2,
        "threshold_5": lambda g: threshold_solver(g, threshold=5.0),
    }

    for name, solver in abstractions.items():
        print(f"\n{name}")
        for split, examples in splits.items():
            correct, total, first_fail = evaluate(solver, examples)
            if total == 0:
                print(f"  {split:<7}: no reference outputs")
            else:
                rate = correct / total if total else 0.0
                fail_repr = first_fail if first_fail is not None else "-"
                print(f"  {split:<7}: {correct}/{total} ({rate:.1%}), first fail: {fail_repr}")


if __name__ == "__main__":
    main()

