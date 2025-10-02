"""Abstraction experiments for ARC task 9385bd28."""

from __future__ import annotations

import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

Grid = List[List[int]]

DATA_PATH = Path(__file__).with_name("arc2_samples") / "9385bd28.json"


def _load_samples() -> Dict[str, Sequence[Dict[str, Grid]]]:
    with DATA_PATH.open() as fh:
        data = json.load(fh)
    return {
        "train": data.get("train", []),
        "test": data.get("test", []),
        "arc_gen": data.get("arc_gen", []),
    }


def _extract_components(grid: Grid):
    height, width = len(grid), len(grid[0])
    coords_by_color: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val:
                coords_by_color[val].append((r, c))

    comps_by_color: Dict[int, List[List[Tuple[int, int]]]] = {}
    comp_lookup: Dict[Tuple[int, int], Tuple[int, int]] = {}
    for color, coords in coords_by_color.items():
        visited = set()
        comps: List[List[Tuple[int, int]]] = []
        for coord in coords:
            if coord in visited:
                continue
            queue = deque([coord])
            visited.add(coord)
            comp: List[Tuple[int, int]] = []
            while queue:
                r, c = queue.popleft()
                comp.append((r, c))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < height and 0 <= nc < width and
                            grid[nr][nc] == color and (nr, nc) not in visited):
                        visited.add((nr, nc))
                        queue.append((nr, nc))
            comp_index = len(comps)
            for cell in comp:
                comp_lookup[cell] = (color, comp_index)
            comps.append(comp)
        comps_by_color[color] = comps
    return comps_by_color, comp_lookup


def _run_pipeline(
    grid: Grid,
    *,
    accept_zero_targets: bool,
    apply_zero_pairs: bool,
    protect_nonlegend: bool,
    only_background_fill: bool,
    recolor_pure_source: bool,
) -> Grid:
    height, width = len(grid), len(grid[0])
    legend_rows = min(5, height)
    legend_cols = min(4, width)
    legend_row_start = max(0, height - legend_rows)

    background = Counter(cell for row in grid for cell in row).most_common(1)[0][0]

    comps_by_color, comp_lookup = _extract_components(grid)

    zero_pairs: List[Tuple[int, int]] = []
    fill_pairs: List[Tuple[int, int]] = []
    seen_pairs = set()
    max_c = max(0, legend_cols - 1)

    for r in range(legend_row_start, height):
        for c in range(max_c):
            left = grid[r][c]
            right = grid[r][c + 1]
            if left == 0:
                continue
            if right == 0 and background == 0:
                continue
            if right == background:
                continue
            if not accept_zero_targets and right == 0:
                continue
            lookup = comp_lookup.get((r, c))
            if lookup is None:
                continue
            color, comp_idx = lookup
            comp = comps_by_color[color][comp_idx]
            if not all(legend_row_start <= rr and cc < legend_cols for rr, cc in comp):
                continue
            pair = (left, right)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            if right == 0:
                zero_pairs.append(pair)
            else:
                fill_pairs.append(pair)

    if not apply_zero_pairs:
        zero_pairs = []

    legend_sources = {source for source, _ in zero_pairs + fill_pairs if source != 0}

    bbox_by_color: Dict[int, Tuple[int, int, int, int]] = {}
    for color, comps in comps_by_color.items():
        cells = [cell for comp in comps
                 if not all(legend_row_start <= r and c < legend_cols for r, c in comp)
                 for cell in comp]
        if not cells:
            continue
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        bbox_by_color[color] = (min(rows), max(rows), min(cols), max(cols))

    protected_boxes: List[Tuple[int, int, int, int]]
    if protect_nonlegend:
        protected_boxes = [bbox for color, bbox in bbox_by_color.items()
                           if color not in legend_sources and color != background]
    else:
        protected_boxes = []

    result = [row[:] for row in grid]

    for source, _ in zero_pairs:
        bbox = bbox_by_color.get(source)
        if not bbox:
            continue
        r0, r1, c0, c1 = bbox
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if result[r][c] == source:
                    result[r][c] = 0

    for source, target in fill_pairs:
        bbox = bbox_by_color.get(source)
        if not bbox:
            continue
        r0, r1, c0, c1 = bbox
        recolor_entire = recolor_pure_source
        if recolor_pure_source:
            recolor_entire = True
            for r in range(r0, r1 + 1):
                for c in range(c0, c1 + 1):
                    if grid[r][c] in (0, background):
                        recolor_entire = False
                        break
                if not recolor_entire:
                    break

        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if result[r][c] == source:
                    if recolor_entire:
                        result[r][c] = target
                    continue
                skip = False
                for pr0, pr1, pc0, pc1 in protected_boxes:
                    if pr0 <= r <= pr1 and pc0 <= c <= pc1:
                        skip = True
                        break
                if skip:
                    continue
                if not only_background_fill or result[r][c] in (0, background):
                    result[r][c] = target
    return result


def abstraction_identity(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def abstraction_naive(grid: Grid) -> Grid:
    return _run_pipeline(
        grid,
        accept_zero_targets=False,
        apply_zero_pairs=False,
        protect_nonlegend=False,
        only_background_fill=False,
        recolor_pure_source=False,
    )


def abstraction_guarded(grid: Grid) -> Grid:
    return _run_pipeline(
        grid,
        accept_zero_targets=False,
        apply_zero_pairs=True,
        protect_nonlegend=True,
        only_background_fill=True,
        recolor_pure_source=False,
    )


def abstraction_final(grid: Grid) -> Grid:
    return _run_pipeline(
        grid,
        accept_zero_targets=True,
        apply_zero_pairs=True,
        protect_nonlegend=True,
        only_background_fill=True,
        recolor_pure_source=True,
    )


ABSTRACTIONS: List[Tuple[str, Callable[[Grid], Grid]]] = [
    ("identity", abstraction_identity),
    ("naive_fill", abstraction_naive),
    ("guarded_fill", abstraction_guarded),
    ("final_solver", abstraction_final),
]


def _evaluate() -> None:
    samples = _load_samples()
    for name, fn in ABSTRACTIONS:
        print(f"=== {name} ===")
        for split in ("train", "test", "arc_gen"):
            entries = samples.get(split, [])
            if not entries:
                print(f"  {split}: no samples")
                continue
            matches = 0
            total = 0
            first_failure = None
            for idx, sample in enumerate(entries):
                pred = fn(sample["input"])
                expected = sample.get("output")
                if expected is None:
                    continue
                total += 1
                if pred == expected:
                    matches += 1
                elif first_failure is None:
                    first_failure = idx
            summary = f"{matches}/{total}" if total else "n/a"
            failure_str = f" first-fail={first_failure}" if first_failure is not None else ""
            print(f"  {split}: {summary}{failure_str}")
        print()


if __name__ == "__main__":
    _evaluate()
