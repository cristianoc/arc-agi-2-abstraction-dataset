"""Abstraction experiments for ARC task 7491f3cf."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, List

Grid = List[List[int]]


def _load_solver_module():
    module_path = Path(__file__).resolve().parent / "arc2_samples" / "7491f3cf.py"
    spec = importlib.util.spec_from_file_location("solver_module", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("solver_module", module)
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


def _load_solver() -> Callable[[Grid], Grid]:
    module = _load_solver_module()
    return module.solve_7491f3cf  # type: ignore[attr-defined]


SOLVER = _load_solver()
MODULE = _load_solver_module()


def copy_left_panel(grid: Grid) -> Grid:
    left_start, center_start, right_start, width = MODULE._extract_sections(grid)  # type: ignore
    left = [row[left_start : left_start + width] for row in grid]
    output = [row[:] for row in grid]
    for r in range(len(grid)):
        output[r][right_start : right_start + width] = left[r]
    return output


def cross_overlay_only(grid: Grid) -> Grid:
    left_start, center_start, right_start, width = MODULE._extract_sections(grid)  # type: ignore
    left = [row[left_start : left_start + width] for row in grid]
    center = [row[center_start : center_start + width] for row in grid]
    left_base = MODULE._panel_base(left)  # type: ignore
    center_base = MODULE._panel_base(center)  # type: ignore
    left_shape = MODULE._interior_shape(left, left_base)  # type: ignore
    center_shape = MODULE._interior_shape(center, center_base)  # type: ignore
    if left_shape != MODULE.DIAMOND_SHAPE or center_shape != MODULE.CROSS_SHAPE:  # type: ignore
        raise ValueError("Cross abstraction not applicable")
    center_counter = Counter(
        center[r][c]
        for r in range(1, len(center) - 1)
        for c in range(width)
        if center[r][c] != center_base
    )
    center_accent = center_counter.most_common(1)[0][0]
    subset = MODULE._choose_cross_subset(left_base, center_accent)  # type: ignore
    result_panel = MODULE._apply_cross_subset(left, center, subset)  # type: ignore
    output = [row[:] for row in grid]
    for r in range(len(grid)):
        output[r][right_start : right_start + width] = result_panel[r]
    return output


def block_template_only(grid: Grid) -> Grid:
    left_start, center_start, right_start, width = MODULE._extract_sections(grid)  # type: ignore
    left = [row[left_start : left_start + width] for row in grid]
    center = [row[center_start : center_start + width] for row in grid]
    left_base = MODULE._panel_base(left)  # type: ignore
    center_base = MODULE._panel_base(center)  # type: ignore
    left_shape = MODULE._interior_shape(left, left_base)  # type: ignore
    center_shape = MODULE._interior_shape(center, center_base)  # type: ignore
    if left_shape != MODULE.BLOCK_LEFT_SHAPE or center_shape != MODULE.BLOCK_CENTER_SHAPE:  # type: ignore
        raise ValueError("Block template abstraction not applicable")
    result_panel = MODULE._apply_block_template(left, center)  # type: ignore
    output = [row[:] for row in grid]
    for r in range(len(grid)):
        output[r][right_start : right_start + width] = result_panel[r]
    return output


def final_solver(grid: Grid) -> Grid:
    return SOLVER(grid)


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "copy_left": copy_left_panel,
    "cross_overlay": cross_overlay_only,
    "block_template": block_template_only,
    "final_solver": final_solver,
}


def main() -> None:
    with open(Path(__file__).resolve().parent / "arc2_samples" / "7491f3cf.json") as fh:
        data = json.load(fh)

    entries: List[Tuple[str, Grid, Grid]] = []
    for split_name in ("train", "test"):
        for sample in data.get(split_name, []):
            entries.append((split_name, sample["input"], sample.get("output")))

    total = len(entries)
    for name, func in ABSTRACTIONS.items():
        matches = 0
        first_fail = None
        for idx, (split, inp, out) in enumerate(entries):
            try:
                pred = func(inp)
            except Exception:
                pred = None
            if pred == out:
                matches += 1
            elif first_fail is None:
                first_fail = (split, idx)
        fail_str = "pass" if matches == total else f"first_fail={first_fail}"
        print(f"{name:15s} {matches}/{total} {fail_str}")


if __name__ == "__main__":
    main()
