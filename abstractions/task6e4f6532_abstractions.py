"""Abstractions explored for ARC task 6e4f6532."""

from __future__ import annotations

import json
import importlib
import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence


Grid = List[List[int]]


DATA_PATH = Path(__file__).resolve().parents[1] / "arc2_samples" / "6e4f6532.json"

# Ensure the project root is available for dynamic imports.
sys.path.append(str(DATA_PATH.parents[1]))


def load_dataset() -> dict:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def identity_solver(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def heuristic_orientation_solver(grid: Grid) -> Grid:
    """Attempt to rotate shapes by aligning their 9-cells to markers."""

    height = len(grid)
    width = len(grid[0])

    mod = importlib.import_module("arc2_samples.6e4f6532")
    base = mod._most_common_color(grid)
    components = mod._describe_components(grid, base)

    objects = [info for info in components if info["colors"].get(8) and info["colors"].get(9)]
    markers = [info for info in components if set(info["colors"]) == {9}]

    if not objects or len(objects) != len(markers):
        return [row[:] for row in grid]

    # Helper transforms copied locally to keep the abstraction self-contained.
    def rotate90(block: Grid) -> Grid:
        return [list(row) for row in zip(*block[::-1])]

    def flip_h(block: Grid) -> Grid:
        return [list(reversed(row)) for row in block]

    def flip_v(block: Grid) -> Grid:
        return block[::-1]

    def orientations(block: Grid) -> Iterable[Grid]:
        seen: set[tuple[tuple[int, ...], ...]] = set()
        current = block
        for _ in range(4):
            for candidate in (current, flip_h(current), flip_v(current), flip_v(flip_h(current))):
                key = tuple(tuple(row) for row in candidate)
                if key not in seen:
                    seen.add(key)
                    yield [row[:] for row in candidate]
            current = rotate90(current)

    result = [row[:] for row in grid]

    for obj in objects:
        for r, c in obj["cells"]:
            result[r][c] = base

    markers_by_size: Dict[int, List[dict]] = {}
    for marker in markers:
        markers_by_size.setdefault(len(marker["cells"]), []).append(marker)
    for size in markers_by_size:
        markers_by_size[size].sort(key=lambda m: (min(r for r, _ in m["cells"]), min(c for _, c in m["cells"])))

    for obj in objects:
        size = len(obj["nine_coords"])
        marker_list = markers_by_size.get(size)
        if not marker_list:
            continue

        marker = marker_list.pop(0)
        min_r = min(r for r, _ in marker["cells"])
        min_c = min(c for _, c in marker["cells"])

        placed = False
        for oriented in orientations(obj["block"]):
            nine_positions = [(r, c) for r in range(len(oriented)) for c in range(len(oriented[0])) if oriented[r][c] == 9]
            if not nine_positions:
                continue
            anchor_r = min_r - min(r for r, _ in nine_positions)
            anchor_c = min_c - min(c for _, c in nine_positions)
            if anchor_r < 0 or anchor_c < 0:
                continue
            if anchor_r + len(oriented) > height or anchor_c + len(oriented[0]) > width:
                continue
            for rr in range(len(oriented)):
                for cc, value in enumerate(oriented[rr]):
                    result[anchor_r + rr][anchor_c + cc] = value
            placed = True
            break

        if not placed:
            for r, c in obj["cells"]:
                result[r][c] = grid[r][c]

    return result


def canonical_template_solver(grid: Grid) -> Grid:
    mod = importlib.import_module("arc2_samples.6e4f6532")
    return mod.solve_6e4f6532(grid)


SOLVERS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": identity_solver,
    "heuristic_orientation": heuristic_orientation_solver,
    "canonical_template": canonical_template_solver,
}


def evaluate_solver(name: str, fn: Callable[[Grid], Grid], dataset: dict) -> None:
    print(f"== {name} ==")
    for split in ("train", "test", "generated", "arc_gen"):
        cases = dataset.get(split)
        if not cases:
            continue

        matches = 0
        first_fail: Optional[int] = None
        for idx, case in enumerate(cases):
            predicted = fn(case["input"])
            expected = case.get("output")
            if expected is None:
                continue
            if predicted == expected:
                matches += 1
            elif first_fail is None:
                first_fail = idx

        total = len(cases)
        if cases[0].get("output") is None:
            print(f"  {split}: no references available")
        else:
            msg = f"{matches}/{total} correct"
            if matches != total and first_fail is not None:
                msg += f"; first fail at index {first_fail}"
            print(f"  {split}: {msg}")


def main() -> None:
    dataset = load_dataset()
    for name, fn in SOLVERS.items():
        evaluate_solver(name, fn, dataset)
        print()


if __name__ == "__main__":
    main()
