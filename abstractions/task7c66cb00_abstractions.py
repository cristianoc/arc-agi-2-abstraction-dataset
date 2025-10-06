"""Abstraction experiments for ARC task 7c66cb00."""

from __future__ import annotations

import importlib.util
import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Callable, Iterable, List, Tuple

Grid = List[List[int]]
Case = dict[str, Grid]
Component = dict[str, object]

_DATA_PATH = Path("analysis/arc2_samples/7c66cb00.json")


def _load_cases(split: str) -> list[Case]:
    if not _DATA_PATH.exists():
        return []
    with _DATA_PATH.open() as fh:
        data = json.load(fh)
    return list(data.get(split, []))


def _split_sections(grid: Grid, base: int) -> list[tuple[int, int]]:
    sections: list[tuple[int, int]] = []
    start: int | None = None
    for r, row in enumerate(grid):
        if all(cell == base for cell in row):
            if start is not None:
                sections.append((start, r - 1))
                start = None
        else:
            if start is None:
                start = r
    if start is not None:
        sections.append((start, len(grid) - 1))
    return sections


def _collect_prototypes(
    grid: Grid,
) -> tuple[int, dict[int, list[Component]], list[tuple[int, int]], list[tuple[int, int]]]:
    base = grid[0][0]
    sections = _split_sections(grid, base)
    prototypes: dict[int, list[Component]] = defaultdict(list)
    prototype_sections: list[tuple[int, int]] = []
    target_sections: list[tuple[int, int]] = []

    found_target = False
    width = len(grid[0])

    for r0, r1 in sections:
        colors = {cell for row in grid[r0 : r1 + 1] for cell in row}
        if not found_target and base in colors:
            prototype_sections.append((r0, r1))
            height = r1 - r0 + 1
            visited = [[False] * width for _ in range(height)]
            for rr in range(height):
                for cc in range(width):
                    if visited[rr][cc]:
                        continue
                    color = grid[r0 + rr][cc]
                    if color == base:
                        visited[rr][cc] = True
                        continue
                    visited[rr][cc] = True
                    queue: deque[tuple[int, int]] = deque([(rr, cc)])
                    cells: list[tuple[int, int]] = []
                    while queue:
                        ar, ac = queue.popleft()
                        cells.append((ar, ac))
                        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            nr, nc = ar + dr, ac + dc
                            if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[r0 + nr][nc] == color:
                                visited[nr][nc] = True
                                queue.append((nr, nc))
                    min_r = min(r for r, _ in cells)
                    min_c = min(c for _, c in cells)
                    norm = [(r - min_r, c - min_c) for r, c in cells]
                    comp_height = max(r for r, _ in norm) + 1
                    comp_width = max(c for _, c in norm) + 1
                    prototypes[color].append(
                        {
                            "height": comp_height,
                            "width": comp_width,
                            "col": min_c,
                            "offsets": norm,
                        }
                    )
        else:
            found_target = True
            target_sections.append((r0, r1))

    return base, prototypes, prototype_sections, target_sections


def _blank_prototypes(grid: Grid) -> Grid:
    base, _, prototype_sections, _ = _collect_prototypes(grid)
    result = [row[:] for row in grid]
    width = len(grid[0])
    for r0, r1 in prototype_sections:
        for r in range(r0, r1 + 1):
            result[r] = [base] * width
    return result


def _stamp_sections(grid: Grid, align_to: str) -> Grid:
    base, prototypes, prototype_sections, target_sections = _collect_prototypes(grid)
    width = len(grid[0])
    result = [row[:] for row in grid]

    # Always clear the prototype area first.
    for r0, r1 in prototype_sections:
        for r in range(r0, r1 + 1):
            result[r] = [base] * width

    for r0, r1 in target_sections:
        colors = {cell for row in grid[r0 : r1 + 1] for cell in row}
        if not colors:
            continue
        edge_color = grid[r0][0]
        fill_candidates = colors - {edge_color}
        if len(fill_candidates) != 1:
            edge_color = grid[r0][-1]
            fill_candidates = colors - {edge_color}
        if len(fill_candidates) != 1:
            continue
        fill_color = next(iter(fill_candidates))
        comps = prototypes.get(fill_color)
        if not comps:
            continue
        section_height = r1 - r0 + 1
        for comp in comps:
            comp_height = int(comp["height"])
            comp_width = int(comp["width"])
            if comp_height > section_height:
                continue
            if align_to == "top":
                top_row = r0
            else:  # align_to == "bottom"
                top_row = r1 - comp_height + 1
            left_col = int(comp["col"])
            if left_col < 0 or left_col + comp_width > width:
                continue
            for dr, dc in comp["offsets"]:
                rr = top_row + dr
                cc = left_col + dc
                if r0 <= rr <= r1 and 0 <= cc < width:
                    result[rr][cc] = edge_color
    return result


def _identity(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _clear_prototypes_only(grid: Grid) -> Grid:
    return _blank_prototypes(grid)


def _top_aligned_stamping(grid: Grid) -> Grid:
    return _stamp_sections(grid, align_to="top")


def _bottom_aligned_stamping(grid: Grid) -> Grid:
    return _stamp_sections(grid, align_to="bottom")


def _solver_pipeline(grid: Grid) -> Grid:
    spec = importlib.util.spec_from_file_location(
        "task7c66cb00", _DATA_PATH.with_suffix(".py")
    )
    if spec is None or spec.loader is None:
        raise ImportError("cannot load solver module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.solve_7c66cb00(grid)


_ABSTRACTIONS: list[tuple[str, Callable[[Grid], Grid]]] = [
    ("identity", _identity),
    ("clear_prototypes", _clear_prototypes_only),
    ("stamp_top", _top_aligned_stamping),
    ("stamp_bottom", _bottom_aligned_stamping),
    ("final_solver", _solver_pipeline),
]


def _evaluate_split(
    abstraction: Callable[[Grid], Grid],
    cases: Iterable[Case],
) -> tuple[int, int, int | None]:
    indexed_cases = [(idx, case) for idx, case in enumerate(cases) if "output" in case]
    total = len(indexed_cases)
    failures: list[int] = []
    for idx, case in indexed_cases:
        prediction = abstraction(case["input"])
        if prediction != case["output"]:
            failures.append(idx)
    solved = total - len(failures)
    first_failure = failures[0] if failures else None
    return solved, total, first_failure


def _format_result(name: str, split: str, solved: int, total: int, first_fail: int | None) -> str:
    if total == 0:
        return f"{name:>18s} | {split:<8s} | (no cases)"
    frac = solved / total * 100.0
    failure = "-" if first_fail is None else str(first_fail)
    return f"{name:>18s} | {split:<8s} | {solved:2d}/{total:<2d} ({frac:5.1f}%) | first fail: {failure}"


def main() -> None:
    splits = {split: _load_cases(split) for split in ("train", "test", "arc_gen")}
    for name, fn in _ABSTRACTIONS:
        for split_name, cases in splits.items():
            solved, total, first_fail = _evaluate_split(fn, cases)
            print(_format_result(name, split_name, solved, total, first_fail))
        print("-" * 72)


if __name__ == "__main__":
    main()
