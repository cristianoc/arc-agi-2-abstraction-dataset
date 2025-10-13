"""Abstractions explored for ARC task 2b83f449."""

from __future__ import annotations

import json
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

Grid = List[List[int]]


def _deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def identity_abstraction(grid: Grid) -> Grid:
    return _deep_copy(grid)


def cross_paint_abstraction(grid: Grid) -> Grid:
    res = _deep_copy(grid)
    h = len(grid)
    w = len(grid[0])
    for r, row in enumerate(grid):
        c = 0
        while c < w:
            if row[c] == 7:
                start = c
                while c < w and row[c] == 7:
                    c += 1
                if c - start == 3:
                    center = start + 1
                    res[r][start] = 8
                    res[r][center] = 6
                    res[r][start + 2] = 8
                    for dr in (-1, 1):
                        rr = r + dr
                        if 0 <= rr < h and grid[rr][center] == 8:
                            res[rr][center] = 6
                continue
            c += 1
    return res


_SOLVER_SPEC = importlib.util.spec_from_file_location(
    "arc_task_2b83f449_solver",
    Path(__file__).resolve().parent / "arc2_samples" / "2b83f449.py",
)
if _SOLVER_SPEC is None or _SOLVER_SPEC.loader is None:
    raise RuntimeError("Unable to load solver module")
_solver_module = importlib.util.module_from_spec(_SOLVER_SPEC)
_SOLVER_SPEC.loader.exec_module(_solver_module)
solve_refined: Callable[[Grid], Grid] = getattr(_solver_module, "solve_2b83f449")


@dataclass
class EvalResult:
    matched: int
    total: int
    first_failure: Optional[int]


def _evaluate(pairs: Sequence[Grid], expected: Sequence[Grid], fn: Callable[[Grid], Grid]) -> EvalResult:
    first_failure = None
    matched = 0
    for idx, (inp, exp) in enumerate(zip(pairs, expected)):
        if fn(inp) == exp:
            matched += 1
        elif first_failure is None:
            first_failure = idx
    return EvalResult(matched, len(pairs), first_failure)


def _load_task() -> dict:
    data_path = Path(__file__).resolve().parent / "arc2_samples" / "2b83f449.json"
    with data_path.open() as f:
        return json.load(f)


def main() -> None:
    task = _load_task()
    abstractions: Iterable[Tuple[str, Callable[[Grid], Grid]]] = (
        ("identity", identity_abstraction),
        ("cross_paint", cross_paint_abstraction),
        ("refined", solve_refined),
    )

    train_pairs = [(item["input"], item["output"]) for item in task["train"]]
    test_pairs = [(item["input"], item.get("output")) for item in task.get("test", [])]
    gen_pairs = [(item["input"], item.get("output")) for item in task.get("generated", [])]

    print("Evaluating abstractions for 2b83f449")
    for name, fn in abstractions:
        train_inputs = [inp for inp, _ in train_pairs]
        train_outputs = [out for _, out in train_pairs]
        train_eval = _evaluate(train_inputs, train_outputs, fn)
        print(f"- {name:10s} train {train_eval.matched}/{train_eval.total} first_fail={train_eval.first_failure}")

        if test_pairs and test_pairs[0][1] is not None:
            test_inputs = [inp for inp, _ in test_pairs]
            test_outputs = [out for _, out in test_pairs]
            test_eval = _evaluate(test_inputs, test_outputs, fn)
            print(f"  {''.ljust(10)} test  {test_eval.matched}/{test_eval.total} first_fail={test_eval.first_failure}")
        else:
            print(f"  {''.ljust(10)} test  (ground truth unavailable)")

        if gen_pairs and gen_pairs[0][1] is not None:
            gen_inputs = [inp for inp, _ in gen_pairs]
            gen_outputs = [out for _, out in gen_pairs]
            gen_eval = _evaluate(gen_inputs, gen_outputs, fn)
            print(f"  {''.ljust(10)} arc-gen {gen_eval.matched}/{gen_eval.total} first_fail={gen_eval.first_failure}")


if __name__ == "__main__":
    main()
