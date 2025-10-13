"""Abstraction experiments for ARC task 195c6913."""

import json
from importlib import util
from pathlib import Path
from typing import Callable, Dict, List, Tuple

TASK_ID = "195c6913"
TASK_PATH = Path(__file__).parent / "arc2_samples" / f"{TASK_ID}.json"
SOLVER_PATH = Path(__file__).parent / "arc2_samples" / f"{TASK_ID}.py"

Grid = List[List[int]]


def load_task() -> Dict:
    return json.loads(TASK_PATH.read_text())


def _extract_pattern_and_anchors(grid: Grid) -> Tuple[List[int], List[Tuple[int, int, int]], int]:
    height = len(grid)
    width = len(grid[0])
    background = grid[0][0]

    # basic component analysis (duplicated from the solver for introspection)
    module_spec = util.spec_from_file_location("solver195c6913_support", SOLVER_PATH)
    module = util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    components = list(module._iter_components(grid))  # type: ignore[attr-defined]

    pattern_infos = []
    totals: Dict[int, int] = {}
    for color, cells in components:
        totals[color] = totals.get(color, 0) + len(cells)
        if len(cells) == 4:
            rows = [r for r, _ in cells]
            cols = [c for _, c in cells]
            if max(rows) - min(rows) != 1 or max(cols) - min(cols) != 1:
                continue
            if min(rows) > 2:
                continue
            pattern_infos.append((min(cols), color, cells))

    pattern_infos.sort(key=lambda item: item[0])
    pattern = [color for _, color, _ in pattern_infos]

    candidates = [
        (totals[color], color)
        for color in totals
        if color != background and color not in pattern
    ]
    fill_color = candidates[0][1] if candidates else background

    anchors: List[Tuple[int, int, int]] = []
    for r, row in enumerate(grid):
        first = row[0]
        if first not in pattern:
            continue
        start_idx = pattern.index(first) if pattern else 0
        c = 1
        while c < width and row[c] == fill_color:
            c += 1
        if c <= 1:
            continue
        anchors.append((r, c, start_idx))

    return pattern, anchors, fill_color


def identity(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def anchor_rows_only(grid: Grid) -> Grid:
    pattern, anchors, _ = _extract_pattern_and_anchors(grid)
    pattern_len = len(pattern)
    output = [row[:] for row in grid]

    for r, boundary, start_idx in anchors:
        idx = start_idx
        for c in range(boundary):
            output[r][c] = pattern[idx]
            idx = (idx + 1) % pattern_len
    return output


def full_propagation(grid: Grid) -> Grid:
    module_spec = util.spec_from_file_location("solver195c6913", SOLVER_PATH)
    module = util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.solve_195c6913(grid)  # type: ignore[attr-defined]


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": identity,
    "anchor_rows_only": anchor_rows_only,
    "full_propagation": full_propagation,
}


def evaluate(task: Dict, name: str, fn: Callable[[Grid], Grid]) -> None:
    print(f"== {name} ==")
    for split in ("train", "test", "arc-gen"):
        examples = task.get(split, [])
        if not examples:
            continue

        total = sum(1 for ex in examples if "output" in ex)
        matches = 0
        first_failure = None

        for idx, example in enumerate(examples):
            inp = example["input"]
            out = example.get("output")
            if out is None:
                continue

            pred = fn(inp)
            if pred == out:
                matches += 1
            elif first_failure is None:
                first_failure = idx

        if total:
            print(f"  {split}: {matches}/{total} matches; first failure index: {first_failure}")
        else:
            print(f"  {split}: {len(examples)} examples (no targets)")
    print()


def main() -> None:
    task = load_task()
    for name, fn in ABSTRACTIONS.items():
        evaluate(task, name, fn)


if __name__ == "__main__":
    main()
