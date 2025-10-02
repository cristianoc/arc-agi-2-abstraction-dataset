"""Abstractions explored while solving ARC task 28a6681f."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

Grid = List[List[int]]
Cell = Tuple[int, int]
Segment = Tuple[int, int, int, int, int]


def load_task() -> Dict[str, Sequence[Dict[str, Grid]]]:
    path = Path("analysis/arc2_samples/28a6681f.json")
    return json.loads(path.read_text())


def deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def candidate_segments(grid: Grid) -> List[Segment]:
    """Return horizontal zero segments bracketed by non-zero colors."""

    segments: List[Segment] = []
    width = len(grid[0]) if grid else 0
    for r, row in enumerate(grid):
        c = 0
        while c < width:
            if row[c] != 0:
                c += 1
                continue

            start = c
            while c < width and row[c] == 0:
                c += 1
            end = c - 1

            left_color = row[start - 1] if start > 0 else 0
            right_color = row[end + 1] if end + 1 < width else 0
            if left_color != 0 and right_color != 0:
                segments.append((r, start, end, left_color, right_color))

    return segments


def segment_cells(segments: Iterable[Segment]) -> List[Cell]:
    cells: List[Cell] = []
    for r, start, end, *_ in segments:
        cells.extend((r, c) for c in range(start, end + 1))
    return cells


def abstraction_identity(grid: Grid) -> Grid:
    """Baseline: leave the grid untouched."""

    return deep_copy(grid)


def abstraction_fill_all(grid: Grid) -> Grid:
    """Fill every bounded horizontal gap with color 1."""

    result = deep_copy(grid)
    for r, c in segment_cells(candidate_segments(grid)):
        result[r][c] = 1
    return result


def abstraction_equal_boundaries(grid: Grid) -> Grid:
    """Fill only those gaps framed by the same non-zero color on both sides."""

    result = deep_copy(grid)
    for segment in candidate_segments(grid):
        r, start, end, left_color, right_color = segment
        if left_color != right_color:
            continue
        for c in range(start, end + 1):
            result[r][c] = 1
    return result


def abstraction_bottom_greedy(grid: Grid) -> Grid:
    """Final solver: bottom-first placement with top-first supply removal."""

    height = len(grid)
    width = len(grid[0]) if height else 0
    result = deep_copy(grid)

    supply: List[Cell] = sorted(
        (r, c) for r in range(height) for c in range(width) if grid[r][c] == 1
    )

    candidates: List[Cell] = segment_cells(candidate_segments(grid))
    candidates.sort(key=lambda rc: (-rc[0], -rc[1]))

    removed: List[Cell] = []
    for r, c in candidates:
        if not supply:
            break
        if supply[0][0] <= r:
            removed.append(supply.pop(0))
            result[r][c] = 1

    for r, c in removed:
        result[r][c] = 0

    return result


ABSTRACTIONS = {
    "identity": abstraction_identity,
    "fill_all_gaps": abstraction_fill_all,
    "equal_boundaries": abstraction_equal_boundaries,
    "bottom_greedy": abstraction_bottom_greedy,
}


def evaluate_split(split_name: str, cases: Sequence[Dict[str, Grid]]) -> None:
    print(f"[{split_name}]")
    has_output = cases and "output" in cases[0]

    for name, fn in ABSTRACTIONS.items():
        if not has_output:
            print(f"  {name}: (no reference outputs)")
            continue

        all_match = True
        first_fail = None
        for idx, sample in enumerate(cases):
            prediction = fn(sample["input"])
            if prediction != sample["output"]:
                all_match = False
                first_fail = idx
                break
        status = "PASS" if all_match else "fail"
        extra = "" if all_match else f" first-fail={first_fail}"
        print(f"  {name}: {status}{extra}")

    if not has_output and cases:
        sample = cases[0]
        pred = ABSTRACTIONS["bottom_greedy"](sample["input"])
        print("  bottom_greedy prediction:")
        for row in pred:
            print("   ", "".join(str(v) for v in row))


def main() -> None:
    data = load_task()
    for split in ("train", "test", "arc-gen"):
        if split in data:
            evaluate_split(split, data[split])


if __name__ == "__main__":
    main()

