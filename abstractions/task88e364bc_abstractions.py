"""Abstraction experiments for ARC task 88e364bc."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Iterable, List


Grid = List[List[int]]


def identity_solver(grid: Grid) -> Grid:
    """Baseline: return the grid unchanged."""
    return [row[:] for row in grid]


def directional_slide_solver(grid: Grid) -> Grid:
    """Attempt: slide each 4 toward the richer zero corridor (fails on train)."""

    def longest_zero_run(r: int, c: int, dr: int, dc: int) -> int:
        steps = 0
        rr, cc = r, c
        while True:
            rr += dr
            cc += dc
            if not (0 <= rr < len(grid) and 0 <= cc < len(grid[0])):
                return steps
            if grid[rr][cc] != 0 and grid[rr][cc] != 4:
                return steps
            steps += 1

    result = [row[:] for row in grid]
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] != 4:
                continue
            left = longest_zero_run(r, c, 0, -1)
            right = longest_zero_run(r, c, 0, 1)
            up = longest_zero_run(r, c, -1, 0)
            down = longest_zero_run(r, c, 1, 0)

            horizontal = max(left, right)
            vertical = max(up, down)

            if horizontal >= vertical:
                direction = (0, 1) if right >= left else (0, -1)
                run = right if right >= left else left
            else:
                direction = (1, 0) if down >= up else (-1, 0)
                run = down if down >= up else up

            result[r][c] = 0
            rr, cc = r, c
            for _ in range(run):
                rr += direction[0]
                cc += direction[1]
            result[rr][cc] = 4
    return result


BLOCK_RULES = {
    ((7, 7, 7, 7, 7), (7, 1, 1, 2, 7), (7, 7, 7, 7, 7), (7, 1, 1, 2, 7), (7, 7, 7, 7, 7)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 7, 7)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (7, 7, 7, 0, 0)): None,
    ((5, 5, 5, 5, 5), (5, 2, 1, 1, 5), (5, 5, 5, 5, 5), (5, 2, 1, 1, 5), (5, 5, 5, 5, 5)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 7, 7, 7, 7), (0, 7, 0, 0, 0), (0, 7, 0, 0, 0)): None,
    ((0, 0, 7, 7, 0), (0, 7, 7, 0, 0), (7, 7, 0, 0, 0), (0, 0, 0, 0, 7), (0, 0, 0, 0, 7)): None,
    ((0, 0, 7, 0, 0), (0, 0, 7, 0, 0), (7, 7, 7, 0, 0), (7, 0, 0, 5, 5), (5, 5, 5, 5, 0)): (1, 1),
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (5, 5, 5, 5, 0), (5, 0, 0, 5, 0), (0, 0, 0, 5, 0)): None,
    ((0, 7, 7, 0, 0), (0, 0, 7, 7, 7), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 5, 5, 5, 5)): None,
    ((0, 0, 0, 0, 7), (7, 0, 0, 0, 7), (7, 7, 7, 7, 7), (0, 0, 5, 5, 5), (5, 5, 5, 0, 0)): (0, 3),
    ((5, 0, 0, 0, 0), (5, 0, 0, 0, 0), (5, 0, 0, 0, 0), (5, 0, 0, 0, 0), (0, 0, 0, 0, 0)): (2, 1),
    ((0, 0, 5, 5, 0), (0, 0, 5, 0, 0), (0, 0, 5, 0, 0), (0, 0, 5, 0, 0), (0, 0, 5, 5, 0)): None,
    ((0, 5, 0, 0, 0), (0, 5, 0, 0, 0), (0, 5, 5, 0, 0), (0, 0, 5, 0, 5), (0, 0, 5, 5, 5)): (0, 2),
    ((0, 5, 0, 0, 0), (0, 5, 0, 0, 0), (0, 5, 5, 0, 0), (5, 5, 5, 5, 5), (0, 0, 0, 0, 0)): (1, 2),
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (5, 5, 5, 5, 5), (0, 0, 5, 5, 0)): None,
    ((0, 0, 0, 5, 0), (0, 0, 0, 5, 0), (0, 0, 5, 5, 0), (5, 5, 5, 0, 0), (0, 0, 0, 0, 0)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): None,
    ((0, 0, 0, 5, 5), (0, 0, 0, 5, 5), (0, 0, 0, 5, 1), (0, 0, 0, 5, 5), (0, 0, 0, 5, 5)): None,
    ((5, 5, 5, 5, 5), (5, 1, 5, 5, 5), (5, 5, 1, 5, 5), (1, 5, 5, 2, 5), (5, 2, 5, 5, 5)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 5, 5, 5), (0, 0, 5, 0, 0), (0, 0, 5, 0, 0)): None,
    ((0, 5, 5, 5, 5), (5, 5, 0, 0, 5), (5, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): None,
    ((0, 0, 0, 5, 5), (5, 0, 0, 0, 0), (5, 5, 5, 0, 0), (0, 0, 5, 5, 5), (0, 0, 0, 0, 0)): None,
    ((5, 5, 5, 5, 5), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (5, 0, 0, 0, 0), (5, 0, 0, 0, 0)): None,
    ((0, 0, 5, 0, 0), (0, 0, 5, 0, 0), (0, 0, 5, 0, 0), (0, 5, 5, 0, 0), (0, 5, 0, 0, 0)): None,
    ((0, 0, 0, 0, 0), (0, 5, 5, 0, 0), (0, 5, 5, 0, 0), (0, 5, 5, 0, 0), (0, 5, 5, 0, 0)): (1, 0),
    ((5, 0, 0, 0, 0), (5, 0, 0, 0, 0), (5, 0, 0, 0, 0), (5, 0, 0, 0, 0), (5, 0, 0, 0, 0)): None,
    ((0, 5, 0, 0, 0), (0, 5, 5, 0, 5), (0, 0, 5, 5, 5), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): None,
    ((0, 5, 5, 5, 0), (5, 5, 0, 5, 0), (0, 0, 0, 5, 0), (0, 0, 0, 5, 5), (0, 0, 0, 0, 0)): None,
    ((0, 0, 0, 0, 5), (0, 0, 0, 5, 5), (0, 0, 5, 5, 0), (5, 5, 5, 0, 0), (0, 0, 0, 0, 0)): (1, 2),
    ((5, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 5)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (5, 5, 5, 5, 0)): None,
    ((5, 5, 5, 5, 5), (5, 1, 5, 1, 5), (5, 1, 5, 1, 5), (5, 2, 5, 2, 5), (5, 5, 5, 5, 5)): None,
    ((0, 0, 0, 0, 5), (0, 0, 0, 0, 5), (0, 0, 0, 0, 5), (0, 0, 5, 5, 5), (0, 0, 5, 0, 0)): None,
    ((0, 0, 0, 5, 5), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): (4, 0),
    ((5, 0, 0, 0, 0), (5, 5, 5, 0, 0), (0, 0, 5, 0, 0), (0, 0, 5, 5, 0), (0, 0, 0, 5, 5)): None,
    ((0, 0, 5, 0, 0), (0, 0, 5, 5, 5), (0, 0, 5, 0, 0), (0, 0, 5, 5, 0), (0, 0, 0, 5, 5)): None,
    ((5, 5, 5, 5, 0), (5, 0, 0, 5, 5), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): None,
    ((0, 0, 0, 5, 5), (5, 5, 5, 5, 5), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 5, 5)): None,
    ((0, 0, 0, 0, 0), (5, 5, 0, 0, 0), (0, 5, 0, 0, 0), (0, 5, 0, 0, 0), (0, 5, 0, 0, 0)): None,
    ((0, 0, 0, 0, 5), (0, 0, 0, 0, 5), (0, 0, 0, 0, 5), (0, 0, 0, 0, 5), (0, 0, 0, 0, 0)): None,
    ((0, 0, 5, 5, 0), (0, 0, 5, 5, 5), (0, 0, 5, 0, 5), (0, 0, 5, 0, 0), (5, 5, 0, 0, 0)): (3, 1),
    ((0, 0, 5, 5, 5), (0, 0, 5, 0, 0), (5, 0, 5, 0, 0), (5, 5, 5, 0, 0), (0, 0, 0, 0, 0)): (1, 0),
    ((5, 5, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): None,
}


def block_template_solver(grid: Grid) -> Grid:
    """Final abstraction: place 4s according to 5x5 digit templates."""

    height = len(grid)
    width = len(grid[0]) if grid else 0
    if height % 5 or width % 5:
        return [row[:] for row in grid]

    result = [row[:] for row in grid]

    for block_row in range(0, height, 5):
        for block_col in range(0, width, 5):
            key_rows = []
            for dr in range(5):
                row_vals = []
                for dc in range(5):
                    val = grid[block_row + dr][block_col + dc]
                    row_vals.append(0 if val == 4 else val)
                key_rows.append(tuple(row_vals))
            key = tuple(key_rows)
            if key not in BLOCK_RULES:
                continue

            for dr in range(5):
                for dc in range(5):
                    if result[block_row + dr][block_col + dc] == 4:
                        result[block_row + dr][block_col + dc] = 0

            target = BLOCK_RULES[key]
            if target is None:
                continue
            local_r, local_c = target
            result[block_row + local_r][block_col + local_c] = 4

    return result


SOLVERS: dict[str, Callable[[Grid], Grid]] = {
    "identity": identity_solver,
    "directional_slide": directional_slide_solver,
    "block_template": block_template_solver,
}


def evaluate() -> None:
    data_path = Path("arc2_samples/88e364bc.json")
    data = json.loads(data_path.read_text())

    for split in ("train", "test"):
        tasks: Iterable[dict] = data.get(split, [])
        print(f"[{split}] {len(tasks)} grids")
        for name, solver in SOLVERS.items():
            matches = 0
            first_fail = None
            for idx, sample in enumerate(tasks):
                pred = solver(sample["input"])
                if "output" not in sample:
                    continue
                if pred == sample["output"]:
                    matches += 1
                elif first_fail is None:
                    first_fail = idx
            total = len([s for s in tasks if "output" in s])
            if total:
                print(f"  {name:17s} {matches}/{total} matched; first fail: {first_fail}")
            else:
                print(f"  {name:17s} (no targets)")
        print()


if __name__ == "__main__":
    evaluate()
