"""Abstractions explored for ARC task 5961cc34.

The module records the candidate pipelines we tried and provides a compact
evaluation harness so we can compare them on every available split.
"""

from __future__ import annotations

import importlib.util
import json
from collections import deque
from pathlib import Path
from typing import Callable, Iterable, List, Sequence, Tuple


HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / "arc2_samples" / "5961cc34.json"
SOLVER_PATH = HERE / "arc2_samples" / "5961cc34.py"


def _load_solver_module():
    spec = importlib.util.spec_from_file_location("task5961cc34_solver", SOLVER_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive guard
        raise RuntimeError("Failed to load solver module for 5961cc34")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


solver_module = _load_solver_module()

solve_5961cc34 = solver_module.solve_5961cc34
_component_scan = solver_module._component_scan
_extend_ray = solver_module._extend_ray

Grid = List[List[int]]
Case = Tuple[Grid, Grid]
Abstraction = Callable[[Grid], Grid]


def _ray_connect_all(grid: Grid) -> Grid:
    """Early attempt: scaffold every motif without filtering the guides."""

    components = _component_scan(grid)
    sentinel = next(comp for comp in components if 2 in comp["colors"])
    others = [comp for comp in components if comp is not sentinel]

    candidates = set(sentinel["coords"])

    for (cell, directions) in sentinel["fours"]:
        direction = next((d for d in directions if d == (-1, 0)), None)
        if direction is None and directions:
            direction = directions[0]
        if direction:
            candidates.update(_extend_ray(grid, cell, direction))

    for comp in others:
        candidates.update(comp["coords"])
        for (cell, directions) in comp["threes"]:
            if not directions:
                continue
            candidates.update(_extend_ray(grid, cell, directions[0]))

    queue = deque(candidates & set(sentinel["coords"]))
    reachable = set(queue)

    while queue:
        r, c = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (r + dr, c + dc)
            if nxt in candidates and nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)

    h, w = len(grid), len(grid[0])
    out = [[8] * w for _ in range(h)]
    for r, c in reachable:
        out[r][c] = 2

    return out


def filtered_scaffold(grid: Grid) -> Grid:
    """Final abstraction: reuse the shipped solver."""

    return solve_5961cc34(grid)


ABSTRACTIONS: Sequence[Tuple[str, Abstraction]] = (
    ("ray_connect_all", _ray_connect_all),
    ("filtered_scaffold", filtered_scaffold),
)


def _load_dataset() -> dict:
    with DATA_PATH.open() as handle:
        return json.load(handle)


def _iter_splits(data: dict) -> Iterable[Tuple[str, List[dict]]]:
    preferred = ("train", "test", "arc_gen", "arc-gen", "generated")
    yielded = set()
    for key in preferred:
        if key in data:
            yielded.add(key)
            yield key, data[key]
    for key, value in data.items():
        if key not in yielded:
            yield key, value


def _format_grid(grid: Grid) -> str:
    return "\n".join("".join(str(cell) for cell in row) for row in grid)


def evaluate_abstractions() -> None:
    data = _load_dataset()
    splits = list(_iter_splits(data))

    for name, fn in ABSTRACTIONS:
        print(f"[{name}]")
        for split_name, cases in splits:
            if not cases:
                print(f"  {split_name}: no cases")
                continue

            if all("output" in case for case in cases):
                matches = 0
                first_fail = None
                for idx, case in enumerate(cases):
                    prediction = fn(case["input"])
                    if prediction == case["output"]:
                        matches += 1
                    elif first_fail is None:
                        first_fail = idx
                total = len(cases)
                accuracy = matches / total
                fail_label = first_fail if first_fail is not None else "-"
                print(
                    f"  {split_name}: {matches}/{total}"
                    f" acc={accuracy:.2%} first_fail={fail_label}"
                )
            else:
                sample = fn(cases[0]["input"])
                print(
                    f"  {split_name}: no targets; sample prediction:\n"
                    f"{_format_grid(sample)}"
                )
        print()


if __name__ == "__main__":
    evaluate_abstractions()
