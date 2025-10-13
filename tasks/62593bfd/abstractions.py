"""Abstractions explored for ARC-AGI-2 task 62593bfd."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

import numpy as np


Grid = List[List[int]]
ColorInfo = Dict[int, Dict[str, object]]


DATA_PATH = Path(__file__).resolve().parents[1] / "arc2_samples" / "62593bfd.json"


def load_dataset() -> dict:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _extract_color_info(grid: Grid) -> Tuple[ColorInfo, int]:
    arr = np.array(grid, dtype=int)
    h, w = arr.shape
    bg = int(np.bincount(arr.flatten()).argmax())

    visited = np.zeros((h, w), dtype=bool)
    info: ColorInfo = {}

    for r in range(h):
        for c in range(w):
            if visited[r, c] or int(arr[r, c]) == bg:
                continue

            color = int(arr[r, c])
            stack = [(r, c)]
            visited[r, c] = True
            cells: List[Tuple[int, int]] = []

            while stack:
                rr, cc = stack.pop()
                cells.append((rr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not visited[nr, nc] and int(arr[nr, nc]) == color:
                        visited[nr, nc] = True
                        stack.append((nr, nc))

            record = info.setdefault(
                color,
                {
                    "cells": [],
                    "min_row": h,
                    "max_row": -1,
                    "components": [],
                    "column_counts": {},
                },
            )

            comp_min = h
            comp_max = -1
            comp_cols: Dict[int, int] = {}
            for rr, cc in cells:
                record["cells"].append((rr, cc))
                record["min_row"] = min(record["min_row"], rr)
                record["max_row"] = max(record["max_row"], rr)
                record["column_counts"][cc] = record["column_counts"].get(cc, 0) + 1
                comp_min = min(comp_min, rr)
                comp_max = max(comp_max, rr)
                comp_cols[cc] = comp_cols.get(cc, 0) + 1
            record["components"].append({
                "cells": cells,
                "min_row": comp_min,
                "max_row": comp_max,
                "column_counts": comp_cols,
            })

    return info, bg


def _paint(arr_shape: Tuple[int, int], bg: int, info: ColorInfo, orientations: Dict[int, str]) -> Grid:
    h, w = arr_shape
    out = np.full((h, w), bg, dtype=int)

    for color in sorted(info):
        orient = orientations[color]
        min_row = info[color]["min_row"]  # type: ignore[index]
        max_row = info[color]["max_row"]  # type: ignore[index]
        delta = -min_row if orient == "top" else (h - 1) - max_row
        for r, c in info[color]["cells"]:  # type: ignore[index]
            nr = r + delta
            out[nr, c] = color

    return out.tolist()


def _median_split(info: ColorInfo, height: int) -> Dict[int, str]:
    min_rows = [info[color]["min_row"] for color in info]  # type: ignore[index]
    threshold = float(np.median(min_rows)) if min_rows else 0.0
    return {
        color: ("top" if info[color]["min_row"] >= threshold else "bottom")  # type: ignore[index]
        for color in info
    }


def _component_overlap_orientation(info: ColorInfo, height: int) -> Dict[int, str]:
    orientations: Dict[int, str] = {color: None for color in info}
    colors = sorted(info)

    for idx, color_a in enumerate(colors):
        comps_a = info[color_a]["components"]  # type: ignore[index]
        for color_b in colors[idx + 1 :]:
            comps_b = info[color_b]["components"]  # type: ignore[index]
            for comp_a in comps_a:
                for comp_b in comps_b:
                    common = set(comp_a["column_counts"]) & set(comp_b["column_counts"])
                    if not common:
                        continue
                    area_a = sum(comp_a["column_counts"][col] for col in common)
                    area_b = sum(comp_b["column_counts"][col] for col in common)
                    if area_a == area_b:
                        chosen = color_a if comp_a["min_row"] > comp_b["min_row"] else color_b
                    else:
                        chosen = color_a if area_a > area_b else color_b
                    other = color_b if chosen == color_a else color_a
                    orientations[chosen] = orientations.get(chosen) or "top"
                    orientations[other] = orientations.get(other) or "bottom"

    free = [color for color, orient in orientations.items() if orient is None]
    if free:
        min_rows = [info[color]["min_row"] for color in free]  # type: ignore[index]
        threshold = float(np.median(min_rows)) if len(min_rows) > 1 else (height - 1) / 2.0
        for color, min_row in zip(free, min_rows):
            orientations[color] = "top" if min_row >= threshold else "bottom"

    return orientations  # type: ignore[return-value]


def _aggregated_overlap_orientation(info: ColorInfo, height: int) -> Dict[int, str]:
    forced: Dict[int, Tuple[str, int]] = {}
    colors = sorted(info)

    for idx, color_a in enumerate(colors):
        counts_a = info[color_a]["column_counts"]  # type: ignore[index]
        for color_b in colors[idx + 1 :]:
            counts_b = info[color_b]["column_counts"]  # type: ignore[index]
            common = set(counts_a) & set(counts_b)
            if not common:
                continue

            area_a = sum(counts_a[col] for col in common)
            area_b = sum(counts_b[col] for col in common)
            if area_a == area_b:
                if info[color_a]["min_row"] == info[color_b]["min_row"]:  # type: ignore[index]
                    top_color = max(color_a, color_b)
                else:
                    top_color = (
                        color_a
                        if info[color_a]["min_row"] > info[color_b]["min_row"]  # type: ignore[index]
                        else color_b
                    )
                weight = 1
            else:
                top_color = color_a if area_a > area_b else color_b
                weight = 1 + abs(area_a - area_b)

            bottom_color = color_b if top_color == color_a else color_a
            for color, orient in ((top_color, "top"), (bottom_color, "bottom")):
                current = forced.get(color)
                if current is None or weight > current[1]:
                    forced[color] = (orient, weight)

    orientations: Dict[int, Optional[str]] = {
        color: (forced[color][0] if color in forced else None) for color in colors
    }

    free = [color for color, orient in orientations.items() if orient is None]
    if free:
        min_rows = [info[color]["min_row"] for color in free]  # type: ignore[index]
        threshold = float(np.median(min_rows)) if len(min_rows) > 1 else (height - 1) / 2.0
        for color, min_row in zip(free, min_rows):
            orientations[color] = "top" if min_row >= threshold else "bottom"

    return {color: orientations[color] for color in colors}  # type: ignore[return-value]


def median_split_abstraction(grid: Grid) -> Grid:
    info, bg = _extract_color_info(grid)
    orientations = _median_split(info, len(grid))
    return _paint((len(grid), len(grid[0])), bg, info, orientations)


def per_component_overlap_abstraction(grid: Grid) -> Grid:
    info, bg = _extract_color_info(grid)
    orientations = _component_overlap_orientation(info, len(grid))
    return _paint((len(grid), len(grid[0])), bg, info, orientations)


def aggregated_overlap_abstraction(grid: Grid) -> Grid:
    info, bg = _extract_color_info(grid)
    orientations = _aggregated_overlap_orientation(info, len(grid))
    return _paint((len(grid), len(grid[0])), bg, info, orientations)


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "median_split": median_split_abstraction,
    "component_overlap": per_component_overlap_abstraction,
    "aggregated_overlap": aggregated_overlap_abstraction,
}


def evaluate_abstraction(name: str, fn: Callable[[Grid], Grid], dataset: dict) -> None:
    print(f"=== {name} ===")
    for split in ("train", "test", "arc_gen", "generated"):
        cases = dataset.get(split)
        if not cases:
            continue

        evaluated = 0
        matches = 0
        first_fail = None

        for idx, case in enumerate(cases):
            expected = case.get("output")
            if expected is None:
                continue

            evaluated += 1
            pred = fn(case["input"])
            if pred == expected:
                matches += 1
            elif first_fail is None:
                first_fail = idx

        if evaluated == 0:
            status = "n/a"
        else:
            status = f"{matches}/{evaluated}"
        suffix = "" if first_fail is None else f", first fail @ {first_fail}"
        print(f"  {split:<9}: {status}{suffix}")


def main() -> None:
    dataset = load_dataset()
    for name, fn in ABSTRACTIONS.items():
        evaluate_abstraction(name, fn, dataset)


if __name__ == "__main__":
    main()
