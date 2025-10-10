"""Abstraction experiments for ARC task 7b3084d4."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence

sys.path.append(str(Path(__file__).resolve().parents[1]))

task_module = importlib.import_module("arc2_samples.7b3084d4")


Grid = List[List[int]]
MaybeInt = Optional[int]

DATA_PATH = Path(__file__).resolve().parents[1] / "arc2_samples" / "7b3084d4.json"
_DATA = json.loads(DATA_PATH.read_text())


def load_pairs(split: str) -> List[dict]:
    if split == "arc_gen":
        return list(_DATA.get("arc_gen", []) or _DATA.get("arc-gen", []) or [])
    return list(_DATA.get(split, []))


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def abstraction_identity(grid: Grid) -> Grid:
    """Baseline: return the grid unchanged."""

    return copy_grid(grid)


def abstraction_first_fit(grid: Grid) -> Grid:
    """Pack components greedily without backtracking (fails on train[1])."""

    comps = task_module._extract_components(grid)
    total = sum(len(cells) for _, cells in comps)
    side = int(total ** 0.5)
    if side == 0 or side * side != total:
        return copy_grid(grid)

    comps_sorted = sorted(comps, key=lambda item: (-len(item[1]), item[0]))
    board: List[List[MaybeInt]] = [[None] * side for _ in range(side)]

    def can_place(variant: Sequence[tuple[int, int]], top: int, left: int) -> bool:
        for dr, dc in variant:
            r, c = top + dr, left + dc
            if r < 0 or c < 0 or r >= side or c >= side:
                return False
            if board[r][c] is not None:
                return False
        return True

    def place(variant: Sequence[tuple[int, int]], top: int, left: int, color: int) -> None:
        for dr, dc in variant:
            r, c = top + dr, left + dc
            board[r][c] = color

    for color, cells in comps_sorted:
        variants = task_module._generate_variants(cells)
        placed = False
        for variant in variants:
            height = max(r for r, _ in variant) + 1
            width = max(c for _, c in variant) + 1
            for top in range(side - height + 1):
                for left in range(side - width + 1):
                    if can_place(variant, top, left):
                        place(variant, top, left, color)
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break
        if not placed:
            return copy_grid(grid)

    return [[cell if cell is not None else 0 for cell in row] for row in board]


def abstraction_perimeter_dfs(grid: Grid) -> Grid:
    """Invoke the final perimeter-guided search from the solver."""

    return task_module.solve_7b3084d4(grid)


ABSTRACTIONS: Sequence[tuple[str, Callable[[Grid], Grid]]] = (
    ("identity", abstraction_identity),
    ("first_fit", abstraction_first_fit),
    ("perimeter_dfs", abstraction_perimeter_dfs),
)


def evaluate(split: str, pairs: Iterable[dict]) -> dict:
    stats = {}
    for name, fn in ABSTRACTIONS:
        total = 0
        ok = 0
        first_fail: Optional[int] = None
        for idx, pair in enumerate(pairs):
            inp = pair["input"]
            out = pair.get("output")
            pred = fn(inp)
            if out is None:
                continue
            total += 1
            if pred == out:
                ok += 1
            elif first_fail is None:
                first_fail = idx
        stats[name] = {
            "total": total,
            "ok": ok,
            "first_fail": first_fail,
        }
    return stats


def main() -> None:
    for split in ("train", "test", "arc_gen"):
        pairs = load_pairs(split)
        if not pairs:
            print(f"[{split}] no pairs available")
            continue
        stats = evaluate(split, pairs)
        print(f"[{split}]")
        for name, info in stats.items():
            total = info["total"]
            ok = info["ok"]
            first = info["first_fail"]
            if total:
                ratio = ok / total
                print(f"  {name:15s} {ok:2d}/{total:<2d} match {ratio:.2f} first_fail={first}")
            else:
                print(f"  {name:15s} no labelled comparison")

        if split == "test":
            best_name, best_fn = ABSTRACTIONS[-1]
            sample = pairs[0]
            print(f"  sample prediction via {best_name}:")
            for row in best_fn(sample["input"]):
                print("   ", row)


if __name__ == "__main__":
    main()
