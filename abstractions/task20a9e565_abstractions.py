"""Abstraction experiments for ARC task 20a9e565."""

from __future__ import annotations

import json
from pathlib import Path
from collections import Counter, defaultdict
from itertools import groupby
from typing import Callable, Dict, Iterable, List, Tuple

Grid = List[List[int]]


def load_task() -> Dict[str, Iterable[Dict[str, Grid]]]:
    path = Path("analysis/arc2_samples/20a9e565.json")
    return json.loads(path.read_text())


def deepcopy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def nonzero_columns(grid: Grid) -> List[int]:
    h, w = len(grid), len(grid[0])
    return [c for c in range(w) if any(grid[r][c] != 0 for r in range(h))]


def column_groups(grid: Grid) -> Tuple[List[Dict[str, int]], int, List[int]]:
    h, w = len(grid), len(grid[0])
    cols = nonzero_columns(grid)
    if not cols:
        return [], 0, []
    tops = [next(grid[r][c] for r in range(h) if grid[r][c] != 0) for c in cols]
    groups: List[Dict[str, int]] = []
    start = 0
    for color, idx_iter in groupby(range(len(cols)), key=lambda idx: tops[idx]):
        idx_list = list(idx_iter)
        groups.append({"color": color, "start": start, "length": len(idx_list)})
        start += len(idx_list)
    return groups, len(cols), tops


def bounding_boxes(grid: Grid) -> Dict[int, Dict[str, int]]:
    boxes: Dict[int, List[int]] = defaultdict(lambda: [10**9, -1, 10**9, -1])
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value == 0:
                continue
            box = boxes[value]
            if r < box[0]:
                box[0] = r
            if r > box[1]:
                box[1] = r
            if c < box[2]:
                box[2] = c
            if c > box[3]:
                box[3] = c
    return {
        color: {"height": box[1] - box[0] + 1, "width": box[3] - box[2] + 1}
        for color, box in boxes.items()
    }


def classify_pattern(groups: List[Dict[str, int]]) -> str:
    colors = [g["color"] for g in groups]
    n = len(groups)
    for k in range(1, n // 2 + 1):
        if colors[:k] == colors[k: 2 * k]:
            return "S"
    lengths = [g["length"] for g in groups]
    freq = Counter(lengths)
    if any(freq[length] == 1 for length in freq):
        return "C"
    return "B"


def abstraction_column_cycle(grid: Grid) -> Grid:
    groups, _total, _ = column_groups(grid)
    if not groups:
        return deepcopy_grid(grid)
    freq_color = Counter(g["color"] for g in groups)
    first_color = groups[0]["color"]
    out: Grid = []
    for idx, group in enumerate(groups):
        color = group["color"]
        next_color = groups[idx + 1]["color"] if idx + 1 < len(groups) else None
        next_effective = next_color
        if next_color is not None and freq_color[next_color] == 1:
            next_effective = first_color
        for pos in range(group["length"]):
            if idx == len(groups) - 1:
                if pos == 0:
                    out.append([first_color, first_color])
                else:
                    out.append([0, first_color])
                continue
            if pos == 0:
                out.append([color, color])
            else:
                if idx % 2 == 0:
                    out.append([next_effective, color])
                else:
                    out.append([color, next_effective])
    return out


def abstraction_cross_banner(grid: Grid) -> Grid:
    groups, _total, _ = column_groups(grid)
    if not groups:
        return deepcopy_grid(grid)
    boxes = bounding_boxes(grid)
    lengths = [g["length"] for g in groups]
    freq_len = Counter(lengths)
    candidate = None
    best_width = None
    for group in groups:
        length = group["length"]
        if freq_len[length] != 1:
            continue
        width = boxes[group["color"]]["width"]
        if best_width is None or width < best_width:
            best_width = width
            candidate = (group["color"], length)
    if candidate is None:
        candidate = (groups[0]["color"], groups[0]["length"])
    color, length = candidate
    width = max(1, length * 2)
    out = [[0] * width for _ in range(3)]
    for c in range(width):
        out[0][c] = color
        out[2][c] = color
    for r in range(3):
        out[r][0] = color
    return out


def abstraction_alternating_bar(grid: Grid) -> Grid:
    groups, total_cols, _ = column_groups(grid)
    if not groups:
        return deepcopy_grid(grid)
    base = groups[0]["color"]
    rows = max(1, total_cols - 1)
    out: Grid = []
    for idx in range(rows):
        if idx % 2 == 0:
            out.append([base, base, base])
        else:
            out.append([base, 0, base])
    return out


def hybrid_solver(grid: Grid) -> Grid:
    groups, total_cols, _ = column_groups(grid)
    if not groups:
        return deepcopy_grid(grid)
    kind = classify_pattern(groups)
    if kind == "S":
        return abstraction_column_cycle(grid)
    if kind == "C":
        return abstraction_cross_banner(grid)
    return abstraction_alternating_bar(grid)


def compare(expected: Grid, predicted: Grid) -> bool:
    return expected == predicted


def evaluate() -> None:
    data = load_task()
    abstractions: Dict[str, Callable[[Grid], Grid]] = {
        "column_cycle": abstraction_column_cycle,
        "cross_banner": abstraction_cross_banner,
        "alternating_bar": abstraction_alternating_bar,
        "hybrid": hybrid_solver,
    }
    for name, fn in abstractions.items():
        print(f"\n{name}")
        for split in ("train", "test"):
            samples = data[split]
            if not samples:
                print(f"  {split}: no samples")
                continue
            if "output" not in samples[0]:
                preds = [fn(sample["input"]) for sample in samples]
                example = preds[0]
                height = len(example)
                width = len(example[0]) if example else 0
                print(f"  {split}: generated {len(preds)} predictions; example size {height}x{width}")
                continue
            matches = 0
            first_fail = None
            for idx, sample in enumerate(samples):
                pred = fn(sample["input"])
                if compare(sample["output"], pred):
                    matches += 1
                elif first_fail is None:
                    first_fail = idx
            total = len(samples)
            print(f"  {split}: {matches}/{total} correct", end="")
            if first_fail is not None:
                print(f" (first fail at index {first_fail})")
            else:
                print(" (all match)")


if __name__ == "__main__":
    evaluate()
