"""Abstraction experiments for task da515329."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Callable, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from arc2_samples.da515329 import solve_da515329


Grid = List[List[int]]


def _load() -> Dict[str, List[Dict[str, Grid]]]:
    path = Path("arc2_samples/da515329.json")
    return json.loads(path.read_text())


def _center_and_radius(grid: Grid) -> tuple[float, float, int]:
    coords = [(r, c) for r, row in enumerate(grid) for c, v in enumerate(row) if v == 8]
    if not coords:
        return 0.0, 0.0, 0
    center_r = sum(r for r, _ in coords) / len(coords)
    center_c = sum(c for _, c in coords) / len(coords)
    rows = [r for r, _ in coords]
    cols = [c for _, c in coords]
    radius = max(max(rows) - min(rows), max(cols) - min(cols)) // 2
    return center_r, center_c, radius


def chebyshev_parity(grid: Grid) -> Grid:
    center_r, center_c, _ = _center_and_radius(grid)
    h = len(grid)
    w = len(grid[0])
    out = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            d = int(round(max(abs(r - center_r), abs(c - center_c))))
            out[r][c] = 8 if d % 2 == 0 else 0
    return out


def oriented_toggle(grid: Grid) -> Grid:
    center_r, center_c, radius = _center_and_radius(grid)
    cat = min(radius, 2)
    h = len(grid)
    w = len(grid[0])
    out = [[0] * w for _ in range(h)]

    for r in range(h):
        for c in range(w):
            dr = r - center_r
            dc = c - center_c
            abs_dr = abs(dr)
            abs_dc = abs(dc)
            d = int(round(max(abs_dr, abs_dc)))
            base = 8 if d % 2 == 0 else 0

            if cat == 0:
                val = base
            else:
                diff = int(round(abs(abs_dr - abs_dc)))
                bigger = abs_dr >= abs_dc
                same = (dr >= 0) == (dc >= 0)
                if d == 0:
                    val = 8 - base
                else:
                    cond1 = (int(round(abs_dr)) == d and int(round(abs_dc)) == d - 1 and same)
                    cond2 = (int(round(abs_dr)) == d - 1 and int(round(abs_dc)) == d and not same)
                    val = 8 - base if (diff == 1 and (cond1 or cond2)) else base
            out[r][c] = val
    return out


def mapping_solution(grid: Grid) -> Grid:
    return solve_da515329(grid)


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "chebyshev_parity": chebyshev_parity,
    "oriented_toggle": oriented_toggle,
    "mapping_solution": mapping_solution,
}


def _matches(a: Grid, b: Grid) -> bool:
    return a == b


def evaluate() -> None:
    data = _load()
    sections = {"train": data["train"], "test": data.get("test", [])}

    for name, fn in ABSTRACTIONS.items():
        print(f"Abstraction: {name}")
        total_train = len(sections["train"])
        solved_train = 0
        first_fail = None

        for idx, sample in enumerate(sections["train"]):
            pred = fn(sample["input"])
            if _matches(pred, sample["output"]):
                solved_train += 1
            elif first_fail is None:
                first_fail = idx

        ratio = solved_train / total_train if total_train else 0.0
        line = f"  train: {solved_train}/{total_train} solved ({ratio:.2%})"
        if first_fail is not None:
            line += f", first failure at index {first_fail}"
        print(line)

        if sections["test"]:
            # Ensure the abstraction can run on test inputs.
            _ = [fn(sample["input"]) for sample in sections["test"]]
            print(f"  test: {len(sections['test'])} inputs processed")
        print()


if __name__ == "__main__":
    evaluate()
