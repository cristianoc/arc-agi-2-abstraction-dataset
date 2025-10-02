"""Abstraction experiments for ARC task 4a21e3da."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Callable, Iterable, List


Grid = List[List[int]]


def load_dataset() -> dict:
    data_path = Path(__file__).with_name("arc2_samples") / "4a21e3da.json"
    return json.loads(data_path.read_text())


def identity_baseline(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def simple_corner_projection(grid: Grid) -> Grid:
    """First attempt: align entire left/right subsets without guarding."""
    height, width = len(grid), len(grid[0])
    sevens = [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == 7]
    twos = [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == 2]
    if not sevens:
        return identity_baseline(grid)

    min_r = min(r for r, _ in sevens)
    max_r = max(r for r, _ in sevens)
    min_c = min(c for _, c in sevens)
    max_c = max(c for _, c in sevens)

    out = [[1] * width for _ in range(height)]

    def align(cells: Iterable[tuple[int, int]], corner: str) -> None:
        cells = list(cells)
        if not cells:
            return
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        r0, c0 = min(rows), min(cols)
        span_r = max(rows) - r0 + 1
        span_c = max(cols) - c0 + 1
        if corner == "top-left":
            dy, dx = -r0, -c0
        elif corner == "top-right":
            dy, dx = -r0, (width - span_c) - c0
        elif corner == "bottom-left":
            dy, dx = (height - span_r) - r0, -c0
        else:  # bottom-right
            dy, dx = (height - span_r) - r0, (width - span_c) - c0
        for r, c in cells:
            nr, nc = r + dy, c + dx
            if 0 <= nr < height and 0 <= nc < width:
                out[nr][nc] = 7

    for sr, sc in twos:
        out[sr][sc] = 2
        if sr < min_r:
            align([(r, c) for r, c in sevens if c < sc], "top-left")
            align([(r, c) for r, c in sevens if c > sc], "top-right")
        elif sr > max_r:
            align([(r, c) for r, c in sevens if c < sc], "bottom-left")
            align([(r, c) for r, c in sevens if c > sc], "bottom-right")
        elif sc < min_c:
            align([(r, c) for r, c in sevens if r < sr], "top-left")
            align([(r, c) for r, c in sevens if r > sr], "bottom-left")
        elif sc > max_c:
            align([(r, c) for r, c in sevens if r < sr], "top-right")
            align([(r, c) for r, c in sevens if r > sr], "bottom-right")

    return out


def final_corner_projection(grid: Grid) -> Grid:
    module_path = Path(__file__).with_name("arc2_samples") / "4a21e3da.py"
    spec = importlib.util.spec_from_file_location("solver_4a21e3da", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # type: ignore[arg-type]
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module.solve_4a21e3da(grid)  # type: ignore[attr-defined]


Solver = Callable[[Grid], Grid]


def evaluate_solver(name: str, solver: Solver, dataset: dict) -> None:
    def check_split(split: str) -> tuple[int, int, int | None]:
        samples = dataset.get(split, [])
        total = len(samples)
        if total == 0:
            return 0, 0, None
        ok = 0
        first_fail = None
        for idx, sample in enumerate(samples):
            pred = solver(sample["input"])
            if pred == sample.get("output", pred):
                ok += 1
            elif first_fail is None:
                first_fail = idx
        return ok, total, first_fail

    train_ok, train_total, train_fail = check_split("train")
    test_ok, test_total, test_fail = check_split("test")
    arc_gen_ok, arc_gen_total, arc_gen_fail = check_split("arc_gen")

    def fmt(ok: int, total: int, fail: int | None) -> str:
        if total == 0:
            return "n/a"
        ratio = 100 * ok / total
        return f"{ratio:5.1f}% (first_fail={fail})"

    print(f"{name:>28}: train {fmt(train_ok, train_total, train_fail)} | test {fmt(test_ok, test_total, test_fail)} | arc-gen {fmt(arc_gen_ok, arc_gen_total, arc_gen_fail)}")


def main() -> None:
    dataset = load_dataset()
    solvers: dict[str, Solver] = {
        "identity_baseline": identity_baseline,
        "simple_corner_projection": simple_corner_projection,
        "final_corner_projection": final_corner_projection,
    }
    for name, solver in solvers.items():
        evaluate_solver(name, solver, dataset)


if __name__ == "__main__":
    main()
