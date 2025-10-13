"""Abstractions explored for ARC task aa4ec2a5.

The module records the progression from a coarse rectangular framing
heuristic to the segment-aware neighborhood annotation that solves the
task. A compact harness evaluates each abstraction on the available ARC
splits (train/test/arc-gen) and reports match counts together with the
first failure index.
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple

Grid = List[List[int]]

TASK_ID = "aa4ec2a5"
TASK_DIR = Path(__file__).resolve().parent / "arc2_samples"
TASK_PATH = TASK_DIR / f"{TASK_ID}.json"
ARC_GEN_PATH = TASK_DIR / f"{TASK_ID}_arcgen.json"
SOLVER_PATH = TASK_DIR / f"{TASK_ID}.py"


def load_task() -> Dict[str, Sequence[dict]]:
    """Load the task JSON (train/test splits)."""

    return json.loads(TASK_PATH.read_text())


def load_arc_gen() -> Sequence[dict]:
    """Load synthetic arc-gen cases if the file exists."""

    if ARC_GEN_PATH.exists():
        return json.loads(ARC_GEN_PATH.read_text())
    return []


def identity_abstraction(grid: Grid) -> Grid:
    """Baseline: copy the grid unchanged."""

    return [row[:] for row in grid]


def _render_component_with_border(grid: Grid, use_segments: bool) -> Grid:
    """Shared component renderer used by the explored abstractions."""

    if not grid:
        return []

    height = len(grid)
    width = len(grid[0])
    background = Counter(val for row in grid for val in row).most_common(1)[0][0]
    result = [row[:] for row in grid]
    visited = [[False] * width for _ in range(height)]
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(height):
        for c in range(width):
            if grid[r][c] != 1 or visited[r][c]:
                continue

            stack = [(r, c)]
            visited[r][c] = True
            component: List[Tuple[int, int]] = []
            rows_to_cols: Dict[int, List[int]] = {}

            while stack:
                rr, cc = stack.pop()
                component.append((rr, cc))
                rows_to_cols.setdefault(rr, []).append(cc)
                for dr, dc in dirs:
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and grid[nr][nc] == 1 and not visited[nr][nc]:
                        visited[nr][nc] = True
                        stack.append((nr, nc))

            row_min = min(r0 for r0, _ in component)
            row_max = max(r0 for r0, _ in component)
            col_min = min(c0 for _, c0 in component)
            col_max = max(c0 for _, c0 in component)
            comp_cells = set(component)

            seen_bg = set()
            hole_cells = set()
            for rr in range(row_min, row_max + 1):
                for cc in range(col_min, col_max + 1):
                    if grid[rr][cc] != background or (rr, cc) in seen_bg:
                        continue
                    bucket = [(rr, cc)]
                    seen_bg.add((rr, cc))
                    touches_edge = False
                    pocket = []
                    while bucket:
                        sr, sc = bucket.pop()
                        pocket.append((sr, sc))
                        if sr in (row_min, row_max) or sc in (col_min, col_max):
                            touches_edge = True
                        for dr, dc in dirs:
                            nr, nc = sr + dr, sc + dc
                            if row_min <= nr <= row_max and col_min <= nc <= col_max:
                                if grid[nr][nc] == background and (nr, nc) not in seen_bg:
                                    seen_bg.add((nr, nc))
                                    bucket.append((nr, nc))
                    if not touches_edge:
                        hole_cells.update(pocket)

            has_hole = bool(hole_cells)
            for rr, cc in component:
                result[rr][cc] = 8 if has_hole else 1

            for rr in range(row_min, row_max + 1):
                for cc in range(col_min, col_max + 1):
                    if grid[rr][cc] != background:
                        continue
                    if (rr, cc) in hole_cells:
                        result[rr][cc] = 6
                        continue
                    if any((rr + dr, cc + dc) in comp_cells for dr, dc in dirs):
                        result[rr][cc] = 2

            for rr, cols in rows_to_cols.items():
                cols_sorted = sorted(cols)
                if use_segments:
                    segments: List[Tuple[int, int]] = []
                    for col in cols_sorted:
                        if not segments or col > segments[-1][1] + 1:
                            segments.append([col, col])
                        else:
                            segments[-1][1] = col
                else:
                    segments = [(min(cols_sorted), max(cols_sorted))]

                for start, end in segments:
                    for cc in (start - 1, end + 1):
                        if 0 <= cc < width and grid[rr][cc] == background and (rr, cc) not in hole_cells:
                            result[rr][cc] = 2
                    for adj in (rr - 1, rr + 1):
                        if not (0 <= adj < height):
                            continue
                        for cc in range(start - 1, end + 2):
                            if 0 <= cc < width and grid[adj][cc] == background and (adj, cc) not in hole_cells:
                                result[adj][cc] = 2

    return result


def rectangular_frame_abstraction(grid: Grid) -> Grid:
    """Early abstraction: treat each row as a single span (rectangular frame)."""

    return _render_component_with_border(grid, use_segments=False)


def segment_frame_abstraction(grid: Grid) -> Grid:
    """Refined abstraction: respect disjoint spans per row (final logic)."""

    return _render_component_with_border(grid, use_segments=True)


def solver_wrapper(grid: Grid) -> Grid:
    """Delegate to the production solver implementation."""

    spec = importlib.util.spec_from_file_location(f"task_{TASK_ID}_solver", SOLVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[assignment]
    solver = getattr(module, f"solve_{TASK_ID}")
    return solver(grid)


def render(grid: Grid) -> str:
    """Render grid values using hexadecimal digits for quick inspection."""

    palette = "0123456789abcdef"
    return "\n".join("".join(palette[val] for val in row) for row in grid)


def evaluate_abstractions() -> None:
    """Evaluate each abstraction on train/test/arc-gen splits."""

    data = load_task()
    arc_gen_cases = load_arc_gen()
    abstractions: Dict[str, Callable[[Grid], Grid]] = {
        "identity": identity_abstraction,
        "rectangular_frame": rectangular_frame_abstraction,
        "segment_frame": segment_frame_abstraction,
        "final_solver": solver_wrapper,
    }

    for split, cases in (("train", data.get("train")), ("test", data.get("test")), ("arc-gen", arc_gen_cases)):
        if not cases:
            print(f"[{split}] no cases available")
            continue

        print(f"[{split}] {len(cases)} case(s)")
        has_outputs = "output" in cases[0]
        for name, fn in abstractions.items():
            matches = 0
            first_fail = None
            preview = None

            for idx, case in enumerate(cases):
                prediction = fn(case["input"])
                if has_outputs and "output" in case:
                    ok = prediction == case["output"]
                    matches += int(ok)
                    if not ok and first_fail is None:
                        first_fail = idx
                elif preview is None:
                    preview = render(prediction)

            if has_outputs:
                summary = f"{matches}/{len(cases)} matched"
                fail_info = first_fail if first_fail is not None else "None"
                print(f"  - {name:20s}: {summary} (first failure={fail_info})")
            else:
                print(f"  - {name:20s}: outputs unavailable; preview below")
                if preview:
                    print(preview)

        print()

    test_cases = data.get("test", [])
    if test_cases:
        print("[solver] predicted test output:")
        print(render(solver_wrapper(test_cases[0]["input"])))


if __name__ == "__main__":
    evaluate_abstractions()
