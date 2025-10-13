"""Abstraction experiments for ARC task a25697e4."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

from arc2_samples.a25697e4 import solve_a25697e4, _select_bridge_color

Grid = List[List[int]]
Case = Dict[str, Grid]
Dataset = Dict[str, List[Case]]


def _sign(value: float) -> int:
    return (value > 0) - (value < 0)


def _collect_counts_and_positions(grid: Grid) -> Tuple[Dict[int, int], Dict[int, List[Tuple[int, int]]]]:
    counts: Dict[int, int] = {}
    positions: Dict[int, List[Tuple[int, int]]] = {}
    for r, row in enumerate(grid):
        for c, color in enumerate(row):
            counts[color] = counts.get(color, 0) + 1
            positions.setdefault(color, []).append((r, c))
    return counts, positions


def abstraction_fill_anchor_holes(grid: Grid) -> Grid:
    """Keep anchor component and fill its bounding holes with the closer secondary color."""

    counts, positions = _collect_counts_and_positions(grid)
    background = max(counts.items(), key=lambda kv: kv[1])[0]
    colors = [color for color in counts if color != background]
    anchor = max(colors, key=lambda color: counts[color])
    anchor_pts = positions[anchor]

    rows = [r for r, _ in anchor_pts]
    cols = [c for _, c in anchor_pts]
    r0, r1 = min(rows), max(rows)
    c0, c1 = min(cols), max(cols)
    anchor_set = set(anchor_pts)
    holes = [
        (r, c)
        for r in range(r0, r1 + 1)
        for c in range(c0, c1 + 1)
        if (r, c) not in anchor_set
    ]
    if not holes:
        return [row[:] for row in grid]

    anchor_mean_row = sum(r for r, _ in anchor_pts) / len(anchor_pts)
    hole_mean_row = sum(r for r, _ in holes) / len(holes)
    hole_diff = hole_mean_row - anchor_mean_row

    bridge = None
    best_score = float("inf")
    for color in colors:
        if color == anchor:
            continue
        pts = positions[color]
        avg_row = sum(r for r, _ in pts) / len(pts)
        row_diff = avg_row - anchor_mean_row
        score = abs(row_diff - hole_diff)
        if score < best_score:
            best_score = score
            bridge = color

    out = [[background for _ in row] for row in grid]
    for r, c in anchor_pts:
        out[r][c] = anchor
    if bridge is not None:
        for r, c in holes:
            out[r][c] = bridge
    return out


def abstraction_compact_components_v1(grid: Grid) -> Grid:
    """First compacting attempt: project third color using a fixed vertical orientation."""

    counts, positions = _collect_counts_and_positions(grid)
    background = max(counts.items(), key=lambda kv: kv[1])[0]
    colors = [color for color in counts if color != background]
    anchor = max(colors, key=lambda color: counts[color])
    anchor_pts = positions[anchor]

    rows = [r for r, _ in anchor_pts]
    cols = [c for _, c in anchor_pts]
    r0, r1 = min(rows), max(rows)
    c0, c1 = min(cols), max(cols)
    anchor_set = set(anchor_pts)
    holes = [
        (r, c)
        for r in range(r0, r1 + 1)
        for c in range(c0, c1 + 1)
        if (r, c) not in anchor_set
    ]

    anchor_mean_row = sum(r for r, _ in anchor_pts) / len(anchor_pts)
    hole_mean_row = sum(r for r, _ in holes) / len(holes)
    hole_diff = hole_mean_row - anchor_mean_row

    bridge = _select_bridge_color(anchor, colors, counts, positions, hole_diff, anchor_mean_row)
    third = next(color for color in colors if color not in {anchor, bridge})

    h = len(grid)
    w = len(grid[0])
    out = [[background for _ in row] for row in grid]
    for r, c in anchor_pts:
        out[r][c] = anchor
    for r, c in holes:
        out[r][c] = bridge

    total_other = sum(counts[color] for color in colors if color != anchor)
    need = total_other - len(holes)
    if need <= 0:
        return out

    horiz = max(2, need - 2)
    if horiz > need:
        horiz = need
    vert = need - horiz

    anchor_mean_col = sum(c for _, c in anchor_pts) / len(anchor_pts)
    third_mean_col = sum(c for _, c in positions[third]) / len(positions[third])
    hd = _sign(third_mean_col - anchor_mean_col) or 1
    vd = _sign(hole_diff) or -1

    hole_col_extreme = max(holes, key=lambda rc: hd * rc[1])[1]
    hole_rows = [rc[0] for rc in holes if rc[1] == hole_col_extreme]
    base_row = min(hole_rows) if vd < 0 else max(hole_rows)
    base_col = hole_col_extreme + (1 if hd > 0 else 0)
    base_row = max(0, min(h - 1, base_row))
    base_col = max(0, min(w - 1, base_col))

    cells = []
    for i in range(horiz):
        c = base_col + hd * i
        if 0 <= c < w:
            cells.append((base_row, c))
    if vert > 0:
        end_row = base_row
        end_col = base_col + hd * (horiz - 1)
        for step in range(1, vert + 1):
            r = end_row + vd * step
            if 0 <= r < h:
                cells.append((r, end_col))
    for r, c in cells[:need]:
        out[r][c] = third
    return out


def abstraction_compact_components_final(grid: Grid) -> Grid:
    """Wrapper around the refined solver."""

    return solve_a25697e4(grid)


ABSTRACTIONS: Sequence[Tuple[str, Callable[[Grid], Grid]]] = (
    ("fill_anchor_holes", abstraction_fill_anchor_holes),
    ("compact_components_v1", abstraction_compact_components_v1),
    ("compact_components_final", abstraction_compact_components_final),
)


def _load_dataset() -> Dataset:
    task_path = Path(__file__).with_name("arc2_samples").joinpath("a25697e4.json")
    with task_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _evaluate_section(cases: Sequence[Case], solver: Callable[[Grid], Grid]) -> Tuple[int, int]:
    if not cases or "output" not in cases[0]:
        return -1, -1

    solved = 0
    first_fail = -1
    for idx, case in enumerate(cases):
        prediction = solver(case["input"])
        if prediction == case["output"]:
            solved += 1
        elif first_fail == -1:
            first_fail = idx
    return solved, first_fail


def run_harness() -> None:
    data = _load_dataset()
    sections = [(name, data[name]) for name in ("train", "test") if name in data]
    print("== a25697e4 abstraction sweep ==")
    for label, solver in ABSTRACTIONS:
        print(f"\n[{label}]")
        for section_name, cases in sections:
            solved, first_fail = _evaluate_section(cases, solver)
            total = len(cases)
            if solved == -1:
                print(f"  {section_name:<5} --/-- (no_gt)")
                continue
            fail_repr = "ok" if solved == total else f"fail@{first_fail}"
            print(f"  {section_name:<5} {solved:02d}/{total:02d} ({fail_repr})")


if __name__ == "__main__":
    run_harness()
