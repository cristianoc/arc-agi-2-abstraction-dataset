"""Abstractions explored while solving ARC task 3e6067c3."""

from pathlib import Path
from typing import Callable, Dict, List, Optional
import importlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

solve_3e6067c3 = importlib.import_module("arc2_samples.3e6067c3").solve_3e6067c3

Grid = List[List[int]]


def load_task() -> Dict[str, List[Dict[str, Grid]]]:
    task_path = Path("arc2_samples/3e6067c3.json")
    return json.loads(task_path.read_text())


def deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def identity_abstraction(grid: Grid) -> Grid:
    """Baseline that leaves the grid unchanged."""
    return deep_copy(grid)


def hint_path_abstraction(grid: Grid) -> Grid:
    """Propagate colors along corridors following the hint-row sequence."""
    return solve_3e6067c3(grid)


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": identity_abstraction,
    "hint_path": hint_path_abstraction,
}


def evaluate() -> None:
    task = load_task()
    for name, fn in ABSTRACTIONS.items():
        print(f"Abstraction: {name}")
        for split in ("train", "test", "arc-gen"):
            pairs = task.get(split, [])
            if not pairs:
                print(f"  {split}: no examples")
                continue
            matches = 0
            first_fail: Optional[int] = None
            for idx, example in enumerate(pairs):
                predicted = fn(example["input"])
                expected = example.get("output")
                if expected is None:
                    if idx == 0:
                        print(f"    sample prediction (idx=0): {predicted}")
                    continue
                if predicted == expected:
                    matches += 1
                elif first_fail is None:
                    first_fail = idx
            total_known = sum(1 for ex in pairs if "output" in ex)
            if total_known:
                status = f"  {split}: {matches}/{total_known} matches"
                if matches != total_known:
                    status += f" (first fail idx={first_fail})"
                print(status)
            else:
                print(f"  {split}: predictions generated (no references)")
        print()


def main() -> None:
    evaluate()


if __name__ == "__main__":
    main()
