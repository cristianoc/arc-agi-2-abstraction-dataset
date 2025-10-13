"""Abstraction experiments for ARC-AGI-2 task 800d221b."""

from __future__ import annotations

import importlib.util
from collections import Counter, deque
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parent.parent
SOLVER_PATH = ROOT / "arc2_samples" / "800d221b.py"


def _load_solver():
    spec = importlib.util.spec_from_file_location("task800d221b", SOLVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


solver_module = _load_solver()
TRAINING_DATA = solver_module.TRAINING_DATA  # type: ignore[attr-defined]


Grid = List[List[int]]
Example = Dict[str, Grid]
Abstraction = Callable[[Grid], Grid]


def _load_cases() -> Dict[str, Sequence[Example]]:
    data = TRAINING_DATA
    return {
        "train": data.get("train", []),
        "test": data.get("test", []),
        "arc-gen": data.get("generated", data.get("arc_gen", [])),
    }


def _components(grid: Grid, colour: int) -> List[List[Tuple[int, int]]]:
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    comps: List[List[Tuple[int, int]]] = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] != colour or seen[r][c]:
                continue
            dq = deque([(r, c)])
            seen[r][c] = True
            comp: List[Tuple[int, int]] = []
            while dq:
                cr, cc = dq.popleft()
                comp.append((cr, cc))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc] and grid[nr][nc] == colour:
                        seen[nr][nc] = True
                        dq.append((nr, nc))
            comps.append(comp)
    return comps


def _dominant_colour(grid: Grid) -> int:
    return Counter(val for row in grid for val in row).most_common(1)[0][0]


def _guess_target_colour(grid: Grid) -> int:
    counts = Counter(val for row in grid for val in row)
    bg = counts.most_common(1)[0][0]
    for colour, _ in counts.most_common():
        if colour != bg:
            return colour
    return bg


def _adjacent_colours(grid: Grid, target: int, bg: int) -> List[int]:
    colours = Counter()
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val != target:
                continue
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(row):
                    neigh = grid[nr][nc]
                    if neigh not in (target, bg):
                        colours[neigh] += 1
    return [col for col, _ in colours.most_common()]


def _distance_map(component: Iterable[Tuple[int, int]], seeds: Iterable[Tuple[int, int]]) -> Dict[Tuple[int, int], int]:
    comp_set = set(component)
    seed_set = set(seeds)
    dist: Dict[Tuple[int, int], int] = {cell: 0 for cell in seed_set}
    dq = deque(seed_set)
    while dq:
        r, c = dq.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            nxt = (nr, nc)
            if nxt in comp_set and nxt not in dist:
                dist[nxt] = dist[(r, c)] + 1
                dq.append(nxt)
    return dist


def abstraction_column_threshold(grid: Grid) -> Grid:
    result = [row[:] for row in grid]
    target = _guess_target_colour(grid)
    bg = _dominant_colour(grid)
    colours = _adjacent_colours(grid, target, bg)
    if len(colours) < 2:
        return result
    left, right = colours[0], colours[-1]
    for comp in _components(grid, target):
        cols = [c for _, c in comp]
        c_min, c_max = min(cols), max(cols)
        for r, c in comp:
            col_norm = (c - c_min) / max(1, c_max - c_min)
            if col_norm < 0.45:
                result[r][c] = left
            elif col_norm > 0.55:
                result[r][c] = right
    return result


def abstraction_distance_threshold(grid: Grid) -> Grid:
    result = [row[:] for row in grid]
    target = _guess_target_colour(grid)
    bg = _dominant_colour(grid)
    colours = _adjacent_colours(grid, target, bg)
    if len(colours) < 2:
        return result
    left, right = colours[0], colours[-1]
    for comp in _components(grid, target):
        comp_set = set(comp)
        cols = [c for _, c in comp]
        rows = [r for r, _ in comp]
        c_min, c_max = min(cols), max(cols)
        width = max(1, c_max - c_min)
        left_seeds = [cell for cell in comp if _touches(grid, cell, left)]
        right_seeds = [cell for cell in comp if _touches(grid, cell, right)]
        if not left_seeds or not right_seeds:
            continue
        d_left = _distance_map(comp_set, left_seeds)
        d_right = _distance_map(comp_set, right_seeds)
        for r, c in comp:
            col_norm = (c - c_min) / width
            left_dist = d_left.get((r, c), 999)
            right_dist = d_right.get((r, c), 999)
            if min(left_dist, right_dist) >= 4:
                continue
            if col_norm <= 0.5:
                result[r][c] = left
            else:
                result[r][c] = right
    return result


def abstraction_knn(grid: Grid) -> Grid:
    return solver_module.solve_800d221b(grid)


def _touches(grid: Grid, cell: Tuple[int, int], colour: int) -> bool:
    r, c = cell
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == colour:
            return True
    return False


def evaluate_abstractions(abstractions: Dict[str, Abstraction]) -> None:
    cases = _load_cases()
    for name, fn in abstractions.items():
        print(f"\n=== {name} ===")
        for section, examples in cases.items():
            labelled = [ex for ex in examples if "output" in ex]
            if not labelled:
                continue
            correct = 0
            first_fail = None
            for idx, ex in enumerate(labelled):
                pred = fn([row[:] for row in ex["input"]])
                if pred == ex["output"]:
                    correct += 1
                elif first_fail is None:
                    first_fail = idx
            total = len(labelled)
            print(f"{section:8s} {correct:2d}/{total:2d}", "first_fail=" + ("-" if first_fail is None else str(first_fail)))


if __name__ == "__main__":
    evaluate_abstractions(
        {
            "column_threshold": abstraction_column_threshold,
            "distance_threshold": abstraction_distance_threshold,
            "hybrid_knn": abstraction_knn,
        }
    )
