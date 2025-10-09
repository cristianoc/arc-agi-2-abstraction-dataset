"""Abstractions explored for ARC task f560132c."""

from __future__ import annotations

import json
import os
from collections import Counter, deque
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


Grid = List[List[int]]
Cells = List[Tuple[int, int]]


def load_samples() -> Dict[str, List[Dict[str, Grid]]]:
    """Load train/test (and optional arc-gen) splits for the task."""

    base = Path(__file__).resolve().parents[1]
    data = json.loads((base / "arc2_samples" / "f560132c.json").read_text())

    # Optional synthetic split.
    gen_path = base / "arc2_samples" / "f560132c_gen.json"
    if gen_path.exists():
        data["arc_gen"] = json.loads(gen_path.read_text())["samples"]

    return data


def get_components(grid: Grid) -> List[Dict[str, object]]:
    """Return connected non-zero components with centroid metadata."""

    height, width = len(grid), len(grid[0])
    seen = [[False] * width for _ in range(height)]
    components: List[Dict[str, object]] = []

    for r in range(height):
        for c in range(width):
            if grid[r][c] == 0 or seen[r][c]:
                continue
            stack = deque([(r, c)])
            seen[r][c] = True
            cells: Cells = []
            while stack:
                cr, cc = stack.pop()
                cells.append((cr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width:
                        if grid[nr][nc] != 0 and not seen[nr][nc]:
                            seen[nr][nc] = True
                            stack.append((nr, nc))
            rows = [rr for rr, _ in cells]
            cols = [cc for _, cc in cells]
            size = len(cells)
            centroid = (sum(rows) / size, sum(cols) / size)
            components.append({
                "cells": cells,
                "size": size,
                "centroid": centroid,
            })
    return components


def trimmed_mask(cells: Cells, grid: Grid) -> Grid:
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    r0, r1 = min(rows), max(rows)
    c0, c1 = min(cols), max(cols)
    mask = [[0] * (c1 - c0 + 1) for _ in range(r1 - r0 + 1)]
    for r, c in cells:
        mask[r - r0][c - c0] = 1

    while mask and all(val == 0 for val in mask[0]):
        mask.pop(0)
    while mask and all(val == 0 for val in mask[-1]):
        mask.pop()
    if mask:
        while all(row[0] == 0 for row in mask):
            for row in mask:
                row.pop(0)
        while all(row[-1] == 0 for row in mask):
            for row in mask:
                row.pop()
    return mask


def rotate_mask(mask: Grid, times: int) -> Grid:
    times %= 4
    rotated = [row[:] for row in mask]
    for _ in range(times):
        rotated = [list(row) for row in zip(*rotated[::-1])]
    return rotated


def palette_info(grid: Grid) -> Tuple[List[int], List[Tuple[int, int]], Dict[str, int]]:
    counts = Counter(val for row in grid for val in row if val)
    palette = [val for val, cnt in counts.items() if cnt == 1]
    cells = [(r, c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] in palette]
    min_row = min(r for r, _ in cells)
    min_col = min(c for _, c in cells)
    block = [[None, None], [None, None]]
    for r, c in cells:
        block[r - min_row][c - min_col] = grid[r][c]
    mapping = {"a": block[0][0], "b": block[0][1], "c": block[1][0], "d": block[1][1]}
    return palette, cells, mapping


def abstraction_identity(grid: Grid) -> Grid:
    """Baseline identity abstraction."""

    return [row[:] for row in grid]


def abstraction_size_sorted(grid: Grid) -> Grid:
    """Assign palette colours by descending component size (naïve)."""

    components = get_components(grid)
    palette, cells, mapping = palette_info(grid)
    palette_comp = next(comp for comp in components if set(cells).issubset(set(comp["cells"])))
    others = [comp for comp in components if comp is not palette_comp]

    ordered = sorted(others, key=lambda comp: comp["size"], reverse=True)
    assignment = {"a": palette_comp, "b": ordered[0], "c": ordered[1], "d": ordered[2]}

    masks = {}
    dims = {}
    for key in "abcd":
        mask = trimmed_mask(assignment[key]["cells"], grid)
        masks[key] = mask
        dims[key] = (len(mask), len(mask[0]))

    out_h = max(dim[0] for dim in dims.values())
    out_w = max(dim[1] for dim in dims.values())
    canvas = [[0] * out_w for _ in range(out_h)]

    placements = {
        "a": (0, 0),
        "b": (0, out_w - dims["b"][1]),
        "c": (out_h - dims["c"][0], 0),
        "d": (out_h - dims["d"][0], out_w - dims["d"][1]),
    }

    for key in "abcd":
        colour = mapping[key]
        mask = masks[key]
        sr, sc = placements[key]
        for r, row in enumerate(mask):
            for c, value in enumerate(row):
                if value:
                    canvas[min(sr + r, out_h - 1)][min(sc + c, out_w - 1)] = colour

    return canvas


def abstraction_offset_oriented(grid: Grid) -> Grid:
    """Final abstraction mirroring the production solver."""

    height, width = len(grid), len(grid[0])
    components = get_components(grid)
    palette, palette_cells, mapping = palette_info(grid)

    def contains_all(comp: Dict[str, object], coords: Iterable[Tuple[int, int]]) -> bool:
        return set(coords).issubset(set(comp["cells"]))

    comp_a = next(comp for comp in components if contains_all(comp, palette_cells))
    px, py = comp_a["centroid"]
    others = [comp for comp in components if comp is not comp_a]
    for comp in others:
        cy, cx = comp["centroid"]
        comp["dy"] = cy - px
        comp["dx"] = cx - py

    comp_d = min(others, key=lambda comp: (comp["dx"], comp["dy"]))
    remaining = [comp for comp in others if comp is not comp_d]
    negative_dy = [comp for comp in remaining if comp["dy"] < 0]
    if negative_dy:
        comp_c = min(negative_dy, key=lambda comp: comp["dy"])
    else:
        comp_c = max(remaining, key=lambda comp: comp["dy"])
    comp_b = next(comp for comp in remaining if comp is not comp_c)

    assignment = {"a": comp_a, "b": comp_b, "c": comp_c, "d": comp_d}
    rotations = {
        "a": 0,
        "b": 3,
        "c": 2 if comp_c["dy"] < 0 else 1,
        "d": 1 if comp_d["dx"] < 0 else 2,
    }

    masks: Dict[str, Grid] = {}
    dims: Dict[str, Tuple[int, int]] = {}
    for key in "abcd":
        mask = trimmed_mask(assignment[key]["cells"], grid)
        rotated = rotate_mask(mask, rotations[key])
        masks[key] = rotated
        dims[key] = (len(rotated), len(rotated[0]))

    out_h = min(dims["a"][0] + dims["c"][0], dims["b"][0] + dims["d"][0])
    out_w = min(dims["a"][1] + dims["b"][1], dims["c"][1] + dims["d"][1])
    canvas = [[0] * out_w for _ in range(out_h)]

    placements = {
        "a": (0, 0),
        "b": (0, out_w - dims["b"][1]),
        "c": (out_h - dims["c"][0], 0),
        "d": (out_h - dims["d"][0], out_w - dims["d"][1]),
    }

    for key in "abcd":
        start_r, start_c = placements[key]
        colour = mapping[key]
        mask = masks[key]
        for r, row in enumerate(mask):
            for c, value in enumerate(row):
                if value:
                    canvas[start_r + r][start_c + c] = colour

    return canvas


ABSTRACTIONS = {
    "identity": abstraction_identity,
    "size_sorted": abstraction_size_sorted,
    "offset_oriented": abstraction_offset_oriented,
}


def evaluate(split: Sequence[Dict[str, Grid]], fn) -> Tuple[int, int, List[int]]:
    matches = 0
    total = len(split)
    first_fail: List[int] = []
    for idx, sample in enumerate(split):
        prediction = fn(sample["input"])
        if "output" not in sample:
            continue
        if prediction == sample["output"]:
            matches += 1
        elif not first_fail:
            first_fail.append(idx)
    return matches, total, first_fail


def preview_prediction(split: Sequence[Dict[str, Grid]], fn) -> None:
    if not split:
        return
    result = fn(split[0]["input"])
    for row in result:
        print("".join(str(x) for x in row))


def main() -> None:
    samples = load_samples()
    for name, fn in ABSTRACTIONS.items():
        print(f"\n=== {name} ===")
        train = samples.get("train", [])
        matches, total, first_fail = evaluate(train, fn)
        suffix = f"first fail @ train[{first_fail[0]}]" if first_fail else "all matched"
        print(f"train: {matches}/{total} ({suffix})")

        test = samples.get("test", [])
        if test and "output" in test[0]:
            tm, tt, tf = evaluate(test, fn)
            tsuffix = f"first fail @ test[{tf[0]}]" if tf else "all matched"
            print(f"test:  {tm}/{tt} ({tsuffix})")
        else:
            print("test prediction preview:")
            preview_prediction(test, fn)

        arc_gen = samples.get("arc_gen", [])
        if arc_gen:
            gm, gt, gf = evaluate(arc_gen, fn)
            gsuffix = f"first fail @ arc_gen[{gf[0]}]" if gf else "all matched"
            print(f"arc-gen: {gm}/{gt} ({gsuffix})")


if __name__ == "__main__":
    main()
