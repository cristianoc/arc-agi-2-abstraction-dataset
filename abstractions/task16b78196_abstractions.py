"""Abstractions explored while solving ARC task 16b78196."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple
import json

Grid = List[List[int]]
Point = Tuple[int, int]


def load_task() -> Dict[str, List[Dict[str, Grid]]]:
    task_path = Path("arc2_samples/16b78196.json")
    return json.loads(task_path.read_text())


def deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def get_components(grid: Grid) -> List[Dict[str, object]]:
    height, width = len(grid), len(grid[0])
    seen = [[False] * width for _ in range(height)]
    components: List[Dict[str, object]] = []

    for r in range(height):
        for c in range(width):
            color = grid[r][c]
            if color == 0 or seen[r][c]:
                continue

            queue: deque[Point] = deque([(r, c)])
            seen[r][c] = True
            cells: List[Point] = []

            while queue:
                cr, cc = queue.popleft()
                cells.append((cr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not seen[nr][nc] and grid[nr][nc] == color:
                        seen[nr][nc] = True
                        queue.append((nr, nc))

            rows = [rr for rr, _ in cells]
            cols = [cc for _, cc in cells]
            top, left, bottom, right = min(rows), min(cols), max(rows), max(cols)
            comp_height = bottom - top + 1
            comp_width = right - left + 1
            shape = tuple(sorted((rr - top, cc - left) for rr, cc in cells))

            components.append(
                {
                    "color": grid[r][c],
                    "cells": cells,
                    "size": len(cells),
                    "top": top,
                    "left": left,
                    "bottom": bottom,
                    "right": right,
                    "height": comp_height,
                    "width": comp_width,
                    "shape": shape,
                }
            )

    return components


def paint_component(target: Grid, top: int, left: int, comp: Dict[str, object]) -> None:
    color = int(comp["color"])
    for dr, dc in comp["shape"]:  # type: ignore[index]
        target[top + dr][left + dc] = color


def reorder_wide_components(
    comps: Iterable[Dict[str, object]],
    *,
    tie_break: str,
) -> List[Dict[str, object]]:
    if tie_break == "left":
        key = lambda comp: (int(comp["top"]), int(comp["left"]))
    elif tie_break == "right":
        key = lambda comp: (int(comp["top"]), -int(comp["left"]))
    else:
        raise ValueError(f"unknown tie_break={tie_break}")
    return sorted(comps, key=key)


def order_narrow_components(comps: List[Dict[str, object]]) -> List[Dict[str, object]]:
    sorted_comps = sorted(comps, key=lambda comp: (int(comp["color"]), int(comp["top"]), int(comp["left"])) )
    buckets: Dict[int, List[Dict[str, object]]] = {}
    for comp in sorted_comps:
        buckets.setdefault(int(comp["color"]), []).append(comp)

    ordered: List[Dict[str, object]] = []
    tail: List[Dict[str, object]] = []
    for comp in sorted_comps:
        color = int(comp["color"])
        bucket = buckets[color]
        if bucket and bucket[0] is comp:
            ordered.append(comp)
            buckets[color] = bucket[1:]
            tail.extend(buckets[color])
            buckets[color] = []
    ordered.extend(tail)
    return ordered


def stack_components(
    output: Grid,
    comps: List[Dict[str, object]],
    *,
    above: bool,
    col: int,
    width: int,
    height: int,
    top_anchor: Optional[int],
    bottom_anchor: Optional[int],
    anchor_bottom: Optional[int],
    compress_bottom: bool,
) -> None:
    if not comps:
        return

    max_width = max(int(comp["width"]) for comp in comps)
    col_clamped = max(0, min(width - max_width, col))

    heights = [int(comp["height"]) for comp in comps]

    if above:
        assert bottom_anchor is not None
        total_height = sum(heights) - (len(comps) - 1)
        top0 = int(bottom_anchor) - total_height + 1
    else:
        assert top_anchor is not None
        top0 = int(top_anchor)

    if top0 < 0:
        shift = -top0
        top0 = 0
        if not above and top_anchor is not None:
            top_anchor += shift

    tops: List[int] = []
    curr_top = top0
    for h in heights:
        tops.append(curr_top)
        curr_top += h - 1

    bottom_last = tops[-1] + heights[-1] - 1
    if bottom_last >= height:
        shift = bottom_last - (height - 1)
        tops = [max(0, t - shift) for t in tops]

    if compress_bottom and not above and anchor_bottom is not None:
        max_height = max(heights)
        desired_bottom = anchor_bottom + len(comps) + max_height - 1
        bottom_last = tops[-1] + heights[-1] - 1
        excess = bottom_last - desired_bottom
        if excess > 0:
            for idx in range(len(tops) - 1, 0, -1):
                max_shift = tops[idx] - (tops[idx - 1] + 1)
                if max_shift <= 0:
                    continue
                shift = min(max_shift, excess)
                if shift > 0:
                    tops[idx] -= shift
                    excess -= shift
                    if excess == 0:
                        break
            if excess > 0:
                tops[0] = max(0, tops[0] - excess)

    for comp, top in zip(comps, tops):
        paint_component(output, top, col_clamped, comp)


def arrange_by_width(
    grid: Grid,
    *,
    tie_break: str,
    compress_bottom: bool,
) -> Grid:
    height, width = len(grid), len(grid[0])
    components = get_components(grid)
    if not components:
        return deep_copy(grid)

    dominant = max(components, key=lambda comp: comp["size"])  # type: ignore[index]
    output: Grid = [[0] * width for _ in range(height)]
    for r, c in dominant["cells"]:  # type: ignore[index]
        output[r][c] = int(dominant["color"])  # type: ignore[index]

    others = [comp for comp in components if comp is not dominant]
    wide = [comp for comp in others if int(comp["width"]) >= 5]
    narrow = [comp for comp in others if int(comp["width"]) < 5]

    if wide:
        wide_sorted = reorder_wide_components(wide, tie_break=tie_break)
        bottom_anchor = int(dominant["top"]) + 1  # type: ignore[index]
        stack_components(
            output,
            wide_sorted,
            above=True,
            col=4,
            width=width,
            height=height,
            top_anchor=None,
            bottom_anchor=bottom_anchor,
            anchor_bottom=None,
            compress_bottom=False,
        )

    if narrow:
        ordered = order_narrow_components(narrow)
        mean_left = sum(int(comp["left"]) for comp in ordered) / len(ordered)
        max_width = max(int(comp["width"]) for comp in ordered)

        dominant_bottom = int(dominant["bottom"])  # type: ignore[index]

        if wide:
            column = int(round(mean_left))
            top_anchor = dominant_bottom
        else:
            column = int(round(mean_left - 1))
            top_anchor = dominant_bottom - 1

        column = max(0, min(width - max_width, column))
        stack_components(
            output,
            ordered,
            above=False,
            col=column,
            width=width,
            height=height,
            top_anchor=top_anchor,
            bottom_anchor=None,
            anchor_bottom=dominant_bottom,
            compress_bottom=compress_bottom,
        )

    return output


def dominant_only(grid: Grid) -> Grid:
    components = get_components(grid)
    if not components:
        return deep_copy(grid)
    dominant = max(components, key=lambda comp: comp["size"])  # type: ignore[index]
    output = [[0] * len(grid[0]) for _ in grid]
    for r, c in dominant["cells"]:  # type: ignore[index]
        output[r][c] = int(dominant["color"])  # type: ignore[index]
    return output


def naive_width_stack(grid: Grid) -> Grid:
    return arrange_by_width(grid, tie_break="left", compress_bottom=False)


def ordered_width_stack(grid: Grid) -> Grid:
    return arrange_by_width(grid, tie_break="right", compress_bottom=False)


def compressed_width_stack(grid: Grid) -> Grid:
    return arrange_by_width(grid, tie_break="right", compress_bottom=True)


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "dominant_only": dominant_only,
    "naive_width_stack": naive_width_stack,
    "ordered_width_stack": ordered_width_stack,
    "compressed_width_stack": compressed_width_stack,
}


def evaluate() -> None:
    task = load_task()
    for name, fn in ABSTRACTIONS.items():
        print(f"Abstraction: {name}")
        for split in ("train", "test", "arc-gen"):
            examples = task.get(split, [])
            if not examples:
                print(f"  {split}: no examples")
                continue
            matches = 0
            first_fail: Optional[int] = None
            total = 0
            for idx, example in enumerate(examples):
                prediction = fn(example["input"])
                expected = example.get("output")
                if expected is None:
                    continue
                total += 1
                if prediction == expected:
                    matches += 1
                elif first_fail is None:
                    first_fail = idx
            if total:
                status = f"  {split}: {matches}/{total} matches"
                if matches != total:
                    status += f" first fail={first_fail}"
                print(status)
            else:
                print(f"  {split}: predictions generated (no references)")
        print()


def main() -> None:
    evaluate()


if __name__ == "__main__":
    main()

