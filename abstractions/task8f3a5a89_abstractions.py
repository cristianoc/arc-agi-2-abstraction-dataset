"""Abstractions explored while solving task 8f3a5a89."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

Grid = Sequence[Sequence[int]]


def _copy_grid(grid: Grid) -> List[List[int]]:
    return [list(row) for row in grid]


def _accessible_from_left(grid: Grid) -> Tuple[set[Tuple[int, int]], int, int]:
    h = len(grid)
    w = len(grid[0]) if h else 0
    accessible: set[Tuple[int, int]] = set()
    seen = [[False] * w for _ in range(h)]
    q: deque[Tuple[int, int]] = deque()
    for r in range(h):
        if grid[r][0] == 8 and not seen[r][0]:
            seen[r][0] = True
            q.append((r, 0))
    while q:
        r, c = q.popleft()
        accessible.add((r, c))
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 8 and not seen[nr][nc]:
                seen[nr][nc] = True
                q.append((nr, nc))
    return accessible, h, w


def _complement_touch_map(h: int, w: int, accessible: set[Tuple[int, int]]) -> List[List[bool]]:
    comp_touch = [[False] * w for _ in range(h)]
    all_cells = {(r, c) for r in range(h) for c in range(w)}
    blocked = all_cells - accessible
    visited: set[Tuple[int, int]] = set()
    for cell in blocked:
        if cell in visited:
            continue
        q: deque[Tuple[int, int]] = deque([cell])
        visited.add(cell)
        component: list[Tuple[int, int]] = []
        touches_border = False
        while q:
            r, c = q.popleft()
            component.append((r, c))
            if r in (0, h - 1) or c in (0, w - 1):
                touches_border = True
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w and (nr, nc) in blocked and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append((nr, nc))
        for r, c in component:
            comp_touch[r][c] = touches_border
    return comp_touch


def _prune_ones(result: List[List[int]], grid: Grid, accessible: set[Tuple[int, int]]) -> None:
    h = len(grid)
    w = len(grid[0]) if h else 0
    seen = [[False] * w for _ in range(h)]
    for sr in range(h):
        for sc in range(w):
            if grid[sr][sc] != 1 or seen[sr][sc]:
                continue
            q: deque[Tuple[int, int]] = deque([(sr, sc)])
            seen[sr][sc] = True
            component: list[Tuple[int, int]] = []
            touches_left = False
            near_access = False
            while q:
                r, c = q.popleft()
                component.append((r, c))
                if c == 0:
                    touches_left = True
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < h and 0 <= nc < w and (nr, nc) in accessible:
                            near_access = True
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 1 and not seen[nr][nc]:
                        seen[nr][nc] = True
                        q.append((nr, nc))
            if touches_left or near_access:
                continue
            for r, c in component:
                result[r][c] = 8


def _collect_sevens(
    grid: Grid,
    accessible: set[Tuple[int, int]],
    comp_touch: List[List[bool]],
    filter_holes: bool,
    add_diag: bool,
) -> set[Tuple[int, int]]:
    if not accessible:
        return set()
    h = len(grid)
    w = len(grid[0])
    sevens: set[Tuple[int, int]] = set()

    def neighbor_valid(r: int, c: int) -> bool:
        if not (0 <= r < h and 0 <= c < w):
            return True
        if (r, c) in accessible:
            return False
        return comp_touch[r][c] if filter_holes else True

    for r, c in accessible:
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if neighbor_valid(r + dr, c + dc):
                sevens.add((r, c))
                break

    if add_diag:
        for r, c in accessible:
            if (r, c) in sevens:
                continue
            for dr, dc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == 1:
                    if not filter_holes or comp_touch[nr][nc]:
                        sevens.add((r, c))
                        break

    return sevens


def _run_pipeline(
    grid: Grid,
    *,
    prune_ones: bool,
    filter_holes: bool,
    add_diag: bool,
) -> List[List[int]]:
    accessible, h, w = _accessible_from_left(grid)
    comp_touch = _complement_touch_map(h, w, accessible)
    result = _copy_grid(grid)
    if prune_ones:
        _prune_ones(result, grid, accessible)
    sevens = _collect_sevens(grid, accessible, comp_touch, filter_holes, add_diag)
    for r, c in accessible:
        result[r][c] = 7 if (r, c) in sevens else 8
    return result


def abstraction_boundary_only(grid: Grid) -> List[List[int]]:
    """Accessible boundary, no hole filtering, no pruning."""
    return _run_pipeline(grid, prune_ones=False, filter_holes=False, add_diag=False)


def abstraction_boundary_with_diag(grid: Grid) -> List[List[int]]:
    """Boundary plus diagonal halo around relevant components."""
    return _run_pipeline(grid, prune_ones=False, filter_holes=False, add_diag=True)


def abstraction_final(grid: Grid) -> List[List[int]]:
    """Final hybrid: prunes detached ones and filters internal holes."""
    return _run_pipeline(grid, prune_ones=True, filter_holes=True, add_diag=True)


ABSTRACTIONS = [
    ("boundary_only", abstraction_boundary_only),
    ("boundary_with_diag", abstraction_boundary_with_diag),
    ("final_hybrid", abstraction_final),
]


def _evaluate_split(split: str, cases: Iterable[dict]) -> None:
    cases = list(cases)
    total = len(cases)
    has_outputs = all("output" in sample for sample in cases)

    if not has_outputs:
        print(f"[{split}] ground-truth outputs unavailable; inference only")
        for name, solver in ABSTRACTIONS:
            preds = [solver(sample["input"]) for sample in cases]
            shapes = { (len(p), len(p[0]) if p else 0) for p in preds }
            print(f"[{split}] {name:<20} produced {len(preds)} predictions, shapes={sorted(shapes)}")
        return

    for name, solver in ABSTRACTIONS:
        successes = 0
        first_fail = None
        for idx, sample in enumerate(cases):
            pred = solver(sample["input"])
            if pred == sample["output"]:
                successes += 1
            elif first_fail is None:
                first_fail = idx
        print(
            f"[{split}] {name:<20} matches={successes}/{total} first_fail={first_fail}"
        )


def main() -> None:
    data_path = Path(__file__).with_name("arc2_samples").joinpath("8f3a5a89.json")
    with data_path.open() as fh:
        data = json.load(fh)

    print("Evaluating abstractions for 8f3a5a89")
    for split in ("train", "test", "arc-gen"):
        if split not in data:
            print(f"[{split}] no cases available")
            continue
        _evaluate_split(split, data[split])


if __name__ == "__main__":  # pragma: no cover
    main()
