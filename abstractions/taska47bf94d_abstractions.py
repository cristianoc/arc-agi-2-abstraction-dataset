"""Abstraction experiments for ARC task a47bf94d."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Callable, Iterable, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from arc2_samples.a47bf94d import (
    _apply_plus,
    _detect_patterns,
    _detect_squares,
    solve_a47bf94d,
)

DATA_PATH = Path(__file__).resolve().parents[1] / "arc2_samples" / "a47bf94d.json"

Grid = List[List[int]]


def load_split() -> dict:
    with DATA_PATH.open() as fh:
        return json.load(fh)


def abstraction_square_to_plus(grid: Grid) -> Grid:
    """Convert each detected 3x3 square into a plus-cross; no X placement."""
    out = [row[:] for row in grid]
    squares = _detect_squares(grid)
    for color, centers in squares.items():
        for r, c in centers:
            _apply_plus(out, r, c, color)
    return out


def abstraction_final_solver(grid: Grid) -> Grid:
    """The final paired plus/X abstraction."""
    return solve_a47bf94d(grid)


ABSTRACTIONS: dict[str, Callable[[Grid], Grid]] = {
    "square_to_plus": abstraction_square_to_plus,
    "paired_plus_x": abstraction_final_solver,
}


def evaluate_split(name: str, grids: Iterable[Grid], targets: Iterable[Grid] | None) -> dict[str, dict[str, object]]:
    results = {}
    for ab_name, fn in ABSTRACTIONS.items():
        matches = 0
        total = 0
        first_fail = None
        outputs: List[Grid] = []
        for idx, grid in enumerate(grids):
            pred = fn(grid)
            outputs.append(pred)
            if targets is not None:
                total += 1
                if pred == targets[idx]:
                    matches += 1
                elif first_fail is None:
                    first_fail = idx
        results[ab_name] = {
            "split": name,
            "total": total,
            "matches": matches,
            "first_fail": first_fail,
            "outputs": outputs,
        }
    return results


def main() -> None:
    data = load_split()
    summaries = {}
    train_in = [case["input"] for case in data["train"]]
    train_out = [case["output"] for case in data["train"]]
    summaries["train"] = evaluate_split("train", train_in, train_out)

    test_in = [case["input"] for case in data.get("test", [])]
    summaries["test"] = evaluate_split("test", test_in, None)

    # Dump summary to stdout
    for split, split_data in summaries.items():
        print(f"=== Split: {split} ===")
        for name, meta in split_data.items():
            total = meta["total"]
            matches = meta["matches"]
            fail = meta["first_fail"]
            if total:
                print(f"- {name}: {matches}/{total} exact; first fail index={fail}")
            else:
                print(f"- {name}: generated {len(meta['outputs'])} outputs (no targets)")
        print()


if __name__ == "__main__":
    main()
