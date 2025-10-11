"""Abstraction experiments for ARC task faa9f03d."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import Counter
from typing import Callable, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from arc2_samples import faa9f03d as solver

Grid = List[List[int]]
Example = Dict[str, Grid]


def load_task() -> Dict[str, List[Example]]:
    path = Path("arc2_samples/faa9f03d.json")
    return json.loads(path.read_text())


def abstraction_remove_noise(grid: Grid) -> Grid:
    cleaned, _ = solver._remove_noise(grid)  # type: ignore[attr-defined]
    return cleaned


def abstraction_row_col_closure(grid: Grid) -> Grid:
    cleaned, top = solver._remove_noise(grid)  # type: ignore[attr-defined]
    dominant = top[0] if top else None
    stats = solver._analyze_color_stats(grid)  # type: ignore[attr-defined]
    allowed = {3}
    for color, (max_col, _max_row) in stats.items():
        if color != 3 and max_col <= 4:
            allowed.add(color)
    g = solver._close_cols_selective(cleaned, dominant)  # type: ignore[attr-defined]
    g = solver._close_rows_selective(g, allowed)  # type: ignore[attr-defined]
    return g


def abstraction_flanked_and_extend(grid: Grid) -> Grid:
    cleaned, top = solver._remove_noise(grid)  # type: ignore[attr-defined]
    dominant = top[0] if top else None
    stats = solver._analyze_color_stats(grid)  # type: ignore[attr-defined]
    allowed = {3}
    for color, (max_col, _max_row) in stats.items():
        if color != 3 and max_col <= 4:
            allowed.add(color)
    g = solver._close_cols_selective(cleaned, dominant)  # type: ignore[attr-defined]
    g = solver._close_rows_selective(g, allowed)  # type: ignore[attr-defined]
    g = solver._flanked_selective(g, dominant)  # type: ignore[attr-defined]
    h = len(g)
    mid = h // 2
    rows_to_extend = [r for r in range(mid + 1) if Counter(v for v in g[r] if v)[3] >= 6]
    g = solver._extend_rows(g, rows_to_extend)  # type: ignore[attr-defined]
    return g


def abstraction_final(grid: Grid) -> Grid:
    return solver.solve_faa9f03d(grid)


PIPELINES: Dict[str, Callable[[Grid], Grid]] = {
    "noise_only": abstraction_remove_noise,
    "row_col_closure": abstraction_row_col_closure,
    "flanked_extend": abstraction_flanked_and_extend,
    "final_solver": abstraction_final,
}


def evaluate(split: Iterable[Example], pipelines: Dict[str, Callable[[Grid], Grid]], has_target: bool) -> List[Tuple[str, int, int, int]]:
    results = []
    for name, fn in pipelines.items():
        total = 0
        matches = 0
        first_fail = -1
        for idx, example in enumerate(split):
            total += 1
            pred = fn(example["input"])
            if has_target:
                if pred == example["output"]:
                    matches += 1
                elif first_fail == -1:
                    first_fail = idx
        results.append((name, total, matches, first_fail))
    return results


def main() -> None:
    task = load_task()
    train = task.get("train", [])
    test = task.get("test", [])

    print("=== faa9f03d abstraction report ===")
    print("Train split:")
    for name, total, matches, first_fail in evaluate(train, PIPELINES, has_target=True):
        status = "ok" if matches == total else "fail"
        fail_info = "-" if matches == total else str(first_fail)
        print(f"  {name:<16} {status}  matches={matches}/{total}  first_fail={fail_info}")

    if test:
        print("\nTest predictions (no ground truth available):")
        for idx, example in enumerate(test):
            print(f"  test[{idx}]")
            pred = abstraction_final(example["input"])
            for row in pred:
                print("    " + ''.join(str(v) for v in row))


if __name__ == "__main__":
    main()
