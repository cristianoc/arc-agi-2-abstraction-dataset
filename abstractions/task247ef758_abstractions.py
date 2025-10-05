"""Abstractions explored while solving ARC task 247ef758."""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

Grid = list[list[int]]


def _load_dataset() -> dict:
    path = Path(__file__).resolve().parent / "arc2_samples" / "247ef758.json"
    return json_load(path)


def json_load(path: Path) -> dict:
    import json

    return json.loads(path.read_text())


def deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def identity_abstraction(grid: Grid) -> Grid:
    """Leave the grid untouched (baseline)."""

    return deep_copy(grid)


def gravity_drop_abstraction(grid: Grid) -> Grid:
    """Initial attempt: align left shapes to top-row markers then drop."""

    work = deep_copy(grid)
    height = len(work)
    width = len(work[0]) if height else 0
    if not height or not width:
        return work

    axis = _find_uniform_column(work)
    if axis is None:
        return work

    color_shapes = _collect_color_shapes(work, axis)
    top_columns = _map_top_row_columns(grid[0], axis)

    for color, cells in color_shapes.items():
        if color not in top_columns:
            continue
        anchor = min(cells)  # approx top-most cell
        relative = [(r - anchor[0], c - anchor[1]) for r, c in cells]
        for target_col in sorted(top_columns[color]):
            col_shift = target_col - anchor[1]
            positions = [(anchor[0] + dr, anchor[1] + col_shift + dc) for dr, dc in relative]
            positions = [(r, c) for r, c in positions if 0 <= r < height and 0 <= c < width]
            drop = _max_drop(work, positions)
            for r, c in positions:
                work[r + drop][c] = color

    return work


def border_marker_cartesian_abstraction(grid: Grid) -> Grid:
    """Final abstraction: Cartesian placement from top-row and last-column markers."""

    work = deep_copy(grid)
    height = len(work)
    width = len(work[0]) if height else 0
    if not height or not width:
        return work

    axis = _find_uniform_column(work)
    if axis is None:
        return work

    color_shapes = _collect_color_shapes(work, axis)
    top_columns = _map_top_row_columns(grid[0], axis)
    last_column = _map_last_column_rows(grid, width - 1)

    def min_row(color: int) -> int:
        return min(r for r, _ in color_shapes[color])

    movable = [
        color
        for color in color_shapes
        if top_columns.get(color) and last_column.get(color)
    ]

    movable.sort(key=min_row, reverse=True)

    for color in movable:
        cells = color_shapes[color]
        center_r, center_c = _shape_center(cells)
        offsets = [(r - center_r, c - center_c) for r, c in cells]

        for r, c in cells:
            work[r][c] = 0

        for target_row in sorted(last_column[color]):
            for target_col in sorted(top_columns[color]):
                for dr, dc in offsets:
                    rr = target_row + dr
                    cc = target_col + dc
                    if 0 <= rr < height and 0 <= cc < width:
                        work[rr][cc] = color

    return work


def _find_uniform_column(grid: Grid) -> int | None:
    height = len(grid)
    width = len(grid[0]) if height else 0
    for c in range(width):
        column = [grid[r][c] for r in range(height)]
        if column and column[0] != 0 and all(v == column[0] for v in column):
            return c
    return None


def _collect_color_shapes(grid: Grid, axis: int) -> dict[int, list[tuple[int, int]]]:
    color_shapes: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for r, row in enumerate(grid):
        for c in range(axis):
            val = row[c]
            if val != 0:
                color_shapes[val].append((r, c))
    return color_shapes


def _map_top_row_columns(top_row: Sequence[int], axis: int) -> dict[int, set[int]]:
    mapping: dict[int, set[int]] = defaultdict(set)
    for c in range(axis + 1, len(top_row)):
        val = top_row[c]
        if val != 0:
            mapping[val].add(c)
    return mapping


def _map_last_column_rows(grid: Grid, column: int) -> dict[int, set[int]]:
    mapping: dict[int, set[int]] = defaultdict(set)
    for r, row in enumerate(grid):
        val = row[column]
        if val != 0:
            mapping[val].add(r)
    return mapping


def _shape_center(cells: Iterable[tuple[int, int]]) -> tuple[int, int]:
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    min_r, max_r = min(rows), max(rows)
    min_c, max_c = min(cols), max(cols)
    return (min_r + max_r) // 2, (min_c + max_c) // 2


def _max_drop(grid: Grid, positions: Iterable[tuple[int, int]]) -> int:
    height = len(grid)
    positions = list(positions)
    drop = 0
    while True:
        can_drop = True
        for r, c in positions:
            nr = r + drop + 1
            if nr >= height or grid[nr][c] != 0:
                can_drop = False
                break
        if not can_drop:
            break
        drop += 1
    return drop


@dataclass
class SplitOutcome:
    solved: int
    total: int
    first_fail: int | None

    def __str__(self) -> str:  # pragma: no cover - helper stringify
        if self.total == 0:
            return "no-targets"
        ratio = self.solved / self.total
        fail = "-" if self.first_fail is None else str(self.first_fail)
        return f"{self.solved}/{self.total} ({ratio:.0%}) first_fail={fail}"


Abstraction = Callable[[Grid], Grid]


def evaluate_abstractions(abstractions: dict[str, Abstraction]) -> None:
    data = _load_dataset()
    splits = {
        "train": data.get("train", []),
        "test": data.get("test", []),
        "arc-gen": data.get("arc_gen", []),
    }

    for name, fn in abstractions.items():
        print(f"[abstraction] {name}")
        for split_name, tasks in splits.items():
            outcome = _evaluate_split(fn, tasks)
            print(f"  {split_name:7s}: {outcome}")
        print()


def _evaluate_split(fn: Abstraction, tasks: Sequence[dict]) -> SplitOutcome:
    solved = 0
    total = 0
    first_fail = None

    for idx, entry in enumerate(tasks):
        grid = entry["input"]
        target = entry.get("output")
        if target is None:
            continue
        total += 1
        pred = fn(grid)
        if pred == target:
            solved += 1
        elif first_fail is None:
            first_fail = idx

    return SplitOutcome(solved=solved, total=total, first_fail=first_fail)


ABSTRACTIONS: dict[str, Abstraction] = {
    "identity": identity_abstraction,
    "gravity_drop": gravity_drop_abstraction,
    "border_marker_cartesian": border_marker_cartesian_abstraction,
}


def main() -> None:  # pragma: no cover - manual harness
    evaluate_abstractions(ABSTRACTIONS)


if __name__ == "__main__":  # pragma: no cover - manual harness
    main()

