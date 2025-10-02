"""Abstraction experiments for ARC task 4c7dc4dd."""

from __future__ import annotations

import json
from collections import Counter, deque
from pathlib import Path
from typing import Dict, List, Tuple


TASK_ID = "4c7dc4dd"
TASK_PATH = Path(__file__).parent / "arc2_samples" / f"{TASK_ID}.json"

Grid = List[List[int]]


def load_task() -> Dict[str, List[Dict[str, Grid]]]:
    return json.loads(TASK_PATH.read_text())


def identity(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def downsample_zero_presence(grid: Grid) -> Grid:
    """Coarse map where cells indicate whether the block contains a zero."""

    height = len(grid)
    width = len(grid[0])
    # Assume 5×5 coarse view as first attempt.
    out_size = 5
    block_h = height // out_size
    block_w = width // out_size
    output = [[0] * out_size for _ in range(out_size)]

    for r in range(out_size):
        for c in range(out_size):
            r0 = r * block_h
            c0 = c * block_w
            block = [grid[rr][cc] for rr in range(r0, min(height, r0 + block_h)) for cc in range(c0, min(width, c0 + block_w))]
            if any(val == 0 for val in block):
                output[r][c] = 2

    return output


def zero_component_glyph(grid: Grid) -> Grid:
    """Projection implemented by the production solver."""

    def find_components(min_size: int = 6) -> List[Tuple[List[Tuple[int, int]], Tuple[int, int, int, int]]]:
        h = len(grid)
        w = len(grid[0])
        visited = [[False] * w for _ in range(h)]
        comps: List[Tuple[List[Tuple[int, int]], Tuple[int, int, int, int]]] = []

        for r in range(h):
            for c in range(w):
                if grid[r][c] != 0 or visited[r][c]:
                    continue

                queue = deque([(r, c)])
                visited[r][c] = True
                cells: List[Tuple[int, int]] = []

                while queue:
                    cr, cc = queue.popleft()
                    cells.append((cr, cc))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < h and 0 <= nc < w and not visited[nr][nc] and grid[nr][nc] == 0:
                            visited[nr][nc] = True
                            queue.append((nr, nc))

                if len(cells) < min_size:
                    continue

                rows = [cell[0] for cell in cells]
                cols = [cell[1] for cell in cells]
                comps.append((cells, (min(rows), max(rows), min(cols), max(cols))))

        return comps

    components = find_components()
    if not components:
        return [[0]]

    heights = [bbox[1] - bbox[0] + 1 for _, bbox in components]
    robust = [h for h in heights if h >= 3]
    out_size = max(3, max(robust or heights))
    out = [[0] * out_size for _ in range(out_size)]

    centres: List[Tuple[float, float]] = []
    h = len(grid)
    w = len(grid[0])
    for cells, _ in components:
        rows = [r for r, _ in cells]
        cols = [c for _, c in cells]
        centres.append(((sum(rows) / len(rows)) / h * out_size, (sum(cols) / len(cols)) / w * out_size))

    row_centres = sorted(r for r, _ in centres)
    anchor_row = (row_centres[0] + row_centres[1]) / 2 if len(row_centres) >= 2 else row_centres[0]
    anchor_row = max(0, min(out_size - 1, int(round(anchor_row))))
    for c in range(out_size):
        out[anchor_row][c] = 2

    col_centres = [c for _, c in centres]
    midpoint = out_size / 2
    left = [c for c in col_centres if c < midpoint]
    right = [c for c in col_centres if c >= midpoint]
    if len(right) > len(left):
        side = "right"
        anchor_col = int(round(max(col_centres)))
    else:
        side = "left"
        anchor_col = int(min(col_centres))
    anchor_col = max(0, min(out_size - 1, anchor_col))

    if side == "right":
        start_row, end_row = 0, out_size - 1
    else:
        max_row = int(round(max(r for r, _ in centres)))
        start_row = anchor_row
        end_row = max(start_row, min(out_size - 1, max_row))
    for r in range(start_row, end_row + 1):
        out[r][anchor_col] = 2

    if side == "right" and left:
        left_span = int(min(col_centres))
        left_span = max(0, min(out_size - 1, left_span))
        for c in range(0, left_span + 1):
            out[0][c] = 2
        bottom_row = int(round(max(r for r, _ in centres)))
        bottom_row = max(0, min(out_size - 1, bottom_row))
        for c in range(0, max(0, left_span)):
            out[bottom_row][c] = 2

    counts = Counter(value for row in grid for value in row if value != 0)
    if counts:
        rare_color, rare_freq = min(counts.items(), key=lambda item: (item[1], item[0]))
        if rare_color not in {0, 2} and rare_freq <= 10:
            out[anchor_row][anchor_col] = rare_color

    return out


ABSTRACTIONS = {
    "identity": identity,
    "downsample_zero_presence": downsample_zero_presence,
    "zero_component_glyph": zero_component_glyph,
}


def evaluate(task: Dict[str, List[Dict[str, Grid]]], name: str, fn) -> None:
    print(f"== {name} ==")
    for split in ("train", "test", "arc-gen"):
        examples = task.get(split, [])
        if not examples:
            continue

        total = sum(1 for ex in examples if "output" in ex)
        matches = 0
        first_failure = None

        for idx, example in enumerate(examples):
            expected = example.get("output")
            if expected is None:
                continue

            prediction = fn(example["input"])
            if prediction == expected:
                matches += 1
            elif first_failure is None:
                first_failure = idx

        if total:
            print(
                f"  {split}: {matches}/{total} matches; "
                f"first failure index: {first_failure}"
            )
        else:
            print(f"  {split}: {len(examples)} examples (no targets)")
    print()


def main() -> None:
    task = load_task()
    for name, fn in ABSTRACTIONS.items():
        evaluate(task, name, fn)


if __name__ == "__main__":
    main()

