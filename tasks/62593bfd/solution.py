"""Solver for ARC-AGI-2 task 62593bfd."""

from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

import numpy as np


Coord = Tuple[int, int]


def _extract_color_info(arr: np.ndarray) -> Tuple[Dict[int, Dict[str, object]], int]:
    """Collect per-color geometry summaries and return them with the background color."""

    h, w = arr.shape
    # Dominant color acts as background; array entries are small non-negative ints.
    bg = int(np.bincount(arr.flatten()).argmax())

    visited = np.zeros((h, w), dtype=bool)
    info: Dict[int, Dict[str, object]] = {}

    for r in range(h):
        for c in range(w):
            if visited[r, c] or int(arr[r, c]) == bg:
                continue

            color = int(arr[r, c])
            stack = [(r, c)]
            visited[r, c] = True
            cells: List[Coord] = []

            while stack:
                rr, cc = stack.pop()
                cells.append((rr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w:
                        if not visited[nr, nc] and int(arr[nr, nc]) == color:
                            visited[nr, nc] = True
                            stack.append((nr, nc))

            record = info.setdefault(
                color,
                {
                    "cells": [],
                    "min_row": h,
                    "max_row": -1,
                    "column_counts": defaultdict(int),
                },
            )

            for rr, cc in cells:
                record["cells"].append((rr, cc))
                record["min_row"] = min(record["min_row"], rr)
                record["max_row"] = max(record["max_row"], rr)
                record["column_counts"][cc] += 1

    return info, bg


def _choose_orientations(
    info: Dict[int, Dict[str, object]],
    height: int,
) -> Dict[int, str]:
    """Decide whether each color should be moved to the top or bottom edge."""

    colors = sorted(info)
    forced: Dict[int, Tuple[str, int]] = {}

    for idx, color_a in enumerate(colors):
        counts_a = info[color_a]["column_counts"]
        for color_b in colors[idx + 1 :]:
            counts_b = info[color_b]["column_counts"]
            common_cols = set(counts_a) & set(counts_b)
            if not common_cols:
                continue

            area_a = sum(counts_a[col] for col in common_cols)
            area_b = sum(counts_b[col] for col in common_cols)

            if area_a == area_b:
                if info[color_a]["min_row"] == info[color_b]["min_row"]:
                    top_color = max(color_a, color_b)
                else:
                    top_color = (
                        color_a
                        if info[color_a]["min_row"] > info[color_b]["min_row"]
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

    orientations: Dict[int, str] = {
        color: forced[color][0] if color in forced else None for color in colors
    }

    free_colors = [color for color, orient in orientations.items() if orient is None]
    if free_colors:
        min_rows = [info[color]["min_row"] for color in free_colors]
        if len(min_rows) > 1:
            threshold = float(np.median(min_rows))
        else:
            threshold = (height - 1) / 2.0

        for color, min_row in zip(free_colors, min_rows):
            orientations[color] = "top" if min_row >= threshold else "bottom"

    return orientations


def _apply_orientation(
    arr: np.ndarray,
    info: Dict[int, Dict[str, object]],
    orientations: Dict[int, str],
    bg: int,
) -> np.ndarray:
    """Paint the rearranged grid according to the decided orientations."""

    h, w = arr.shape
    out = np.full((h, w), bg, dtype=int)

    for color in sorted(info):
        orient = orientations[color]
        if orient not in {"top", "bottom"}:
            raise ValueError(f"Orientation for color {color} unresolved: {orient}")

        min_row = info[color]["min_row"]
        max_row = info[color]["max_row"]
        delta = -min_row if orient == "top" else (h - 1) - max_row

        for r, c in info[color]["cells"]:
            nr = r + delta
            if not (0 <= nr < h):
                raise ValueError("Invalid translation outside grid bounds")
            if out[nr, c] != bg:
                raise ValueError("Collision detected while placing components")
            out[nr, c] = color

    return out


def solve_62593bfd(grid):
    """Swap color groups vertically so each occupies either the top or bottom edge."""

    arr = np.array(grid, dtype=int)
    info, bg = _extract_color_info(arr)
    orientations = _choose_orientations(info, arr.shape[0])
    rearranged = _apply_orientation(arr, info, orientations, bg)
    return rearranged.tolist()


p = solve_62593bfd
