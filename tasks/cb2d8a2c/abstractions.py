"""Abstraction experiments for task cb2d8a2c."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


Grid = List[List[int]]


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def transpose(grid: Grid) -> Grid:
    return [list(col) for col in zip(*grid)]


def get_components(grid: Grid) -> List[Tuple[set[int], set[int]]]:
    h = len(grid)
    w = len(grid[0])
    seen = [[False] * w for _ in range(h)]
    comps: List[Tuple[set[int], set[int]]] = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] not in (1, 2) or seen[r][c]:
                continue
            rows: set[int] = set()
            cols: set[int] = set()
            stack = [(r, c)]
            seen[r][c] = True
            while stack:
                rr, cc = stack.pop()
                rows.add(rr)
                cols.add(cc)
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc] and grid[nr][nc] in (1, 2):
                        seen[nr][nc] = True
                        stack.append((nr, nc))
            comps.append((rows, cols))
    return comps


def list_obstacles(grid: Grid) -> List[Tuple[int, int, int]]:
    obstacles: List[Tuple[int, int, int]] = []
    for r, row in enumerate(grid):
        cols = [c for c, val in enumerate(row) if val in (1, 2)]
        if cols:
            obstacles.append((r, min(cols), max(cols)))
    return obstacles


def derive_segments(
    grid: Grid, left_col: int, right_col: int, mode: str
) -> Tuple[List[Tuple[int, int, int]], int, int]:
    h = len(grid)
    w = len(grid[0])
    anchor_row, anchor_col = next((r, c) for r in range(h) for c in range(w) if grid[r][c] == 3)
    obstacles = list_obstacles(grid)
    segments: List[Tuple[int, int, int]] = []
    current_col = anchor_col
    prev_row = anchor_row
    for row, lo, hi in obstacles:
        if not (lo <= current_col <= hi):
            prev_row = row
            continue
        diff = row - prev_row
        if diff <= 1:
            change = prev_row + 1 if prev_row + 1 < row else prev_row
        else:
            if mode == "horizontal":
                change = prev_row + diff // 2
                if diff % 2 == 1:
                    change -= 1
            else:
                width = hi - lo + 1
                addition = max(0, diff - width) + (1 if diff % 2 == 0 else 0)
                change = prev_row + diff // 2 + addition
            if change <= prev_row:
                change = prev_row + 1
            if change >= row:
                change = row - 1
        target = right_col if not (lo <= right_col <= hi) else left_col
        segments.append((change, current_col, target))
        current_col = target
        prev_row = row
    return segments, anchor_row, anchor_col


def draw_path(
    grid: Grid,
    segments: Sequence[Tuple[int, int, int]],
    anchor_row: int,
    anchor_col: int,
    downward: bool,
) -> List[Tuple[int, int]]:
    h = len(grid)
    path: List[Tuple[int, int]] = []
    current_row = anchor_row
    current_col = anchor_col
    path.append((current_row, current_col))
    for row, _, target_col in segments:
        if row != current_row:
            step = 1 if row > current_row else -1
            for r in range(current_row + step, row + step, step):
                path.append((r, current_col))
            current_row = row
        if target_col != current_col:
            step = 1 if target_col > current_col else -1
            for c in range(current_col, target_col + step, step):
                path.append((current_row, c))
            current_col = target_col
        else:
            path.append((current_row, current_col))
    if downward:
        for r in range(current_row + 1, h):
            path.append((r, current_col))
    else:
        for r in range(current_row - 1, -1, -1):
            path.append((r, current_col))
    return path


def paint_path(grid: Grid, path: Iterable[Tuple[int, int]]) -> Grid:
    out = copy_grid(grid)
    for r, row in enumerate(out):
        for c, val in enumerate(row):
            if val == 1:
                out[r][c] = 2
    for r, c in path:
        out[r][c] = 3
    return out


def abstraction_horizontal(grid: Grid) -> Grid:
    obstacles = list_obstacles(grid)
    if not obstacles:
        return paint_path(grid, {(len(grid) - 1, next(c for c, v in enumerate(grid[0]) if v == 3))})
    min_col = min(lo for _, lo, _ in obstacles)
    left = max(1, min_col - 5)
    right = min(len(grid[0]) - 1, left + 7)
    segments, anchor_row, anchor_col = derive_segments(grid, left, right, "horizontal")
    path = draw_path(grid, segments, anchor_row, anchor_col, downward=True)
    return paint_path(grid, path)


def abstraction_vertical(grid: Grid) -> Grid:
    tgrid = transpose(grid)
    anchor_row, anchor_col = next((r, c) for r in range(len(tgrid)) for c in range(len(tgrid[0])) if tgrid[r][c] == 3)
    left = anchor_col
    right = min(len(tgrid[0]) - 1, 8)
    segments, a_row, a_col = derive_segments(tgrid, left, right, "vertical")
    t_path = draw_path(tgrid, segments, a_row, a_col, downward=True)
    path = {(c, r) for r, c in t_path}
    return paint_path(grid, path)


def hybrid_pipeline(grid: Grid) -> Grid:
    comps = get_components(grid)
    horizontal = all(len(rows) == 1 for rows, _ in comps) if comps else True
    if horizontal:
        return abstraction_horizontal(grid)
    return abstraction_vertical(grid)


def evaluate(pipeline, data: dict, split: str) -> Tuple[int, int, int]:
    total = len(data.get(split, []))
    if total == 0:
        return 0, 0, -1
    hits = 0
    first_fail = -1
    for idx, example in enumerate(data[split]):
        pred = pipeline(example["input"])
        if pred == example.get("output", []):
            hits += 1
        elif first_fail == -1:
            first_fail = idx
    return hits, total, first_fail


def main() -> None:
    data = json.loads(Path("arc2_samples/cb2d8a2c.json").read_text())
    pipelines = {
        "horizontal_only": abstraction_horizontal,
        "vertical_only": abstraction_vertical,
        "hybrid": hybrid_pipeline,
    }
    splits = ["train", "test", "arc-gen"]
    for name, fn in pipelines.items():
        print(f"Pipeline: {name}")
        for split in splits:
            hits, total, first_fail = evaluate(fn, data, split)
            if total == 0:
                continue
            print(
                f"  {split:<5}: {hits}/{total} matches",
                "first fail=" + ("none" if first_fail == -1 else str(first_fail)),
            )
        print()


if __name__ == "__main__":
    main()
