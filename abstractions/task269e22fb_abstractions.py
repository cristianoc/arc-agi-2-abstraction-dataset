"""Abstraction experiments for ARC task 269e22fb."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple


HERE = Path(__file__).resolve().parent
TASK_PATH = HERE / "arc2_samples" / "269e22fb.json"
SOLVER_PATH = HERE / "arc2_samples" / "269e22fb.py"


def _load_solver_module():
    spec = importlib.util.spec_from_file_location("task269e22fb_solver", SOLVER_PATH)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise RuntimeError("unable to load solver module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


solver_module = _load_solver_module()

BASE_PATTERN: List[List[int]] = solver_module.BASE_PATTERN
TRANSFORMS: Sequence[Tuple[str, Callable[[List[List[int]]], List[List[int]]]]] = solver_module.TRANSFORMS
INVERSE: Dict[str, str] = solver_module.INVERSE


def _map_colors(grid: List[List[int]], mapping: Dict[int, int]) -> List[List[int]]:
    return [[mapping[value] for value in row] for row in grid]


def _try_alignment(grid: List[List[int]], allow_swap: bool) -> Optional[Dict[str, object]]:
    colors = sorted({value for row in grid for value in row})
    if len(colors) != 2:
        return None

    orders = [tuple(colors)]
    if allow_swap:
        orders.append(tuple(colors[::-1]))

    seen = set()
    for order in orders:
        if order in seen:
            continue
        seen.add(order)
        mapping = {order[0]: 0, order[1]: 1}
        grid_bin = _map_colors(grid, mapping)
        for name, fn in TRANSFORMS:
            candidate = fn(grid_bin)
            h, w = len(candidate), len(candidate[0])
            max_r = len(BASE_PATTERN) - h + 1
            max_c = len(BASE_PATTERN[0]) - w + 1
            for r in range(max_r):
                for c in range(max_c):
                    if all(candidate[i] == BASE_PATTERN[r + i][c : c + w] for i in range(h)):
                        return {
                            "transform": name,
                            "mapping": mapping,
                            "pattern": candidate,
                            "position": (r, c),
                        }
    return None


def _assemble_from_alignment(alignment: Dict[str, object]) -> List[List[int]]:
    base = solver_module.deep_copy(BASE_PATTERN)
    r, c = alignment["position"]  # type: ignore[index]
    pattern: List[List[int]] = alignment["pattern"]  # type: ignore[assignment]
    h, w = len(pattern), len(pattern[0])
    for i in range(h):
        base[r + i][c : c + w] = pattern[i][:]

    inverse_name = INVERSE[alignment["transform"]]  # type: ignore[index]
    out_bin = solver_module.apply_named_transform(base, inverse_name)
    reverse_map = {binary: color for color, binary in alignment["mapping"].items()}  # type: ignore[attr-defined]
    return [[reverse_map[value] for value in row] for row in out_bin]


def abstraction_identity(grid: List[List[int]]) -> List[List[int]]:
    return [row[:] for row in grid]


def abstraction_alignment_no_swap(grid: List[List[int]]) -> Optional[List[List[int]]]:
    alignment = _try_alignment(grid, allow_swap=False)
    return None if alignment is None else _assemble_from_alignment(alignment)


def abstraction_alignment_with_swap(grid: List[List[int]]) -> Optional[List[List[int]]]:
    alignment = _try_alignment(grid, allow_swap=True)
    return None if alignment is None else _assemble_from_alignment(alignment)


ABSTRACTIONS: Dict[str, Callable[[List[List[int]]], Optional[List[List[int]]]]] = {
    "identity": abstraction_identity,
    "align_no_swap": abstraction_alignment_no_swap,
    "align_with_swap": abstraction_alignment_with_swap,
}


def _load_task() -> Dict[str, List[Dict[str, List[List[int]]]]]:
    return json.loads(TASK_PATH.read_text())


def _contains_input(grid: List[List[int]], subgrid: List[List[int]]) -> bool:
    h, w = len(subgrid), len(subgrid[0])
    gh, gw = len(grid), len(grid[0])
    for r in range(gh - h + 1):
        for c in range(gw - w + 1):
            if all(grid[r + i][c : c + w] == subgrid[i] for i in range(h)):
                return True
    return False


def evaluate_abstractions() -> None:
    data = _load_task()
    splits = ("train", "test", "arc-gen")

    for name, fn in ABSTRACTIONS.items():
        print(f"== {name} ==")
        for split in splits:
            cases = data.get(split)
            if not cases:
                print(f"  {split}: no cases")
                continue

            total_with_targets = sum(1 for case in cases if case.get("output"))
            matches = 0
            first_failure: Optional[int] = None
            embeddings = 0

            for idx, case in enumerate(cases):
                prediction = fn(case["input"])
                if prediction is None:
                    if first_failure is None and case.get("output"):
                        first_failure = idx
                    continue

                if case.get("output"):
                    if prediction == case["output"]:
                        matches += 1
                    elif first_failure is None:
                        first_failure = idx
                else:
                    if _contains_input(prediction, case["input"]):
                        embeddings += 1

            if total_with_targets:
                success_rate = f"{matches}/{total_with_targets}"
                fail_text = first_failure if first_failure is not None else "-"
                print(f"  {split}: matches {success_rate}, first failure {fail_text}")
            else:
                print(f"  {split}: generated {len(cases)} outputs; input embedded in {embeddings}")
        print()


if __name__ == "__main__":
    evaluate_abstractions()

