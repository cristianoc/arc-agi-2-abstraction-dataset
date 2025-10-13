"""Abstraction experiments for task abc82100."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, List, Sequence, Tuple

from arc2_samples.abc82100 import solve_abc82100

Grid = List[List[int]]
Example = Tuple[Grid, Grid]
Abstraction = Callable[[Grid], Grid]


def load_dataset() -> Tuple[List[Example], List[Example], List[Example]]:
    data = json.loads(Path("arc2_samples/abc82100.json").read_text())
    def section(name: str) -> List[Example]:
        entries = []
        for ex in data.get(name, []):
            if "input" in ex and "output" in ex:
                entries.append((ex["input"], ex["output"]))
        return entries
    return section("train"), section("test"), section("arc-gen")


def identity_abstraction(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def knn_abstraction(grid: Grid) -> Grid:
    return solve_abc82100(grid)


ABSTRACTIONS: List[Tuple[str, Abstraction]] = [
    ("identity", identity_abstraction),
    ("knn", knn_abstraction),
]


def evaluate():
    train, test, arc_gen = load_dataset()
    sections = [("train", train), ("test", test), ("arc-gen", arc_gen)]
    for name, fn in ABSTRACTIONS:
        print(f"== {name} ==")
        for sec_name, examples in sections:
            total = len(examples)
            if total == 0:
                print(f"  {sec_name:7s}: n/a (no examples)")
                continue
            correct = 0
            first_fail = None
            for idx, (inputs, expected) in enumerate(examples):
                prediction = fn(inputs)
                if prediction == expected:
                    correct += 1
                elif first_fail is None:
                    first_fail = idx
            ratio = correct / total
            if first_fail is None:
                print(f"  {sec_name:7s}: {correct}/{total} ({ratio:.2%})")
            else:
                print(
                    f"  {sec_name:7s}: {correct}/{total} ({ratio:.2%}), first failure @ index {first_fail}"
                )
        print()


if __name__ == "__main__":
    evaluate()
