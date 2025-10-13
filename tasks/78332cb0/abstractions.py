"""Abstraction experiments for ARC task 78332cb0."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

Grid = List[List[int]]

TASK_ID = "78332cb0"
TASK_PATH = Path(__file__).resolve().parents[1] / "arc2_samples" / f"{TASK_ID}.json"


def load_task() -> Dict[str, Sequence[Dict[str, Grid]]]:
    return json.loads(TASK_PATH.read_text())


def deepcopy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def find_separator_color(grid: Grid) -> int:
    colors = {cell for row in grid for cell in row}
    height, width = len(grid), len(grid[0])

    def has_full_line(color: int) -> bool:
        row_full = any(all(cell == color for cell in row) for row in grid)
        col_full = any(all(grid[r][c] == color for r in range(height)) for c in range(width))
        return row_full or col_full

    if 6 in colors and has_full_line(6):
        return 6

    for color in colors:
        if has_full_line(color):
            return color

    return 6


def segments_along_axis(grid: Grid, separator: int, axis: int) -> List[Tuple[int, int]]:
    if axis == 0:
        length = len(grid)
        is_separator = lambda idx: all(cell == separator for cell in grid[idx])
    else:
        length = len(grid[0])
        is_separator = lambda idx: all(row[idx] == separator for row in grid)

    segments: List[Tuple[int, int]] = []
    start: Optional[int] = None
    for idx in range(length):
        if is_separator(idx):
            if start is not None:
                segments.append((start, idx))
                start = None
        else:
            if start is None:
                start = idx
    if start is not None:
        segments.append((start, length))

    if not segments:
        segments.append((0, length))
    return segments


def extract_blocks(grid: Grid, separator: int) -> List[List[Grid]]:
    row_segments = segments_along_axis(grid, separator, axis=0)
    col_segments = segments_along_axis(grid, separator, axis=1)

    blocks: List[List[Grid]] = []
    for r0, r1 in row_segments:
        row_blocks: List[Grid] = []
        for c0, c1 in col_segments:
            block = [row[c0:c1] for row in grid[r0:r1]]
            row_blocks.append(block)
        blocks.append(row_blocks)
    return blocks


def assemble_blocks(blocks: Sequence[Grid], separator: int, orientation: str) -> Grid:
    if not blocks:
        return []

    block_height = len(blocks[0])
    block_width = len(blocks[0][0]) if block_height else 0

    if orientation == "horizontal":
        total_width = len(blocks) * block_width + (len(blocks) - 1)
        result = [[separator] * total_width for _ in range(block_height)]
        cursor = 0
        for index, block in enumerate(blocks):
            for r in range(block_height):
                for c in range(block_width):
                    result[r][cursor + c] = block[r][c]
            cursor += block_width
            if index != len(blocks) - 1:
                for r in range(block_height):
                    result[r][cursor] = separator
                cursor += 1
        return result

    total_height = len(blocks) * block_height + (len(blocks) - 1)
    result: Grid = []
    for index, block in enumerate(blocks):
        result.extend(deepcopy_grid(block))
        if index != len(blocks) - 1:
            result.append([separator] * block_width)
    return result


def rotate_blocks_clockwise(blocks: Sequence[Sequence[Grid]]) -> List[List[Grid]]:
    if not blocks:
        return []
    block_rows = len(blocks)
    block_cols = len(blocks[0])
    rotated: List[List[Grid]] = [[None for _ in range(block_rows)] for _ in range(block_cols)]  # type: ignore[list-item]
    for r, row in enumerate(blocks):
        for c, block in enumerate(row):
            nr = c
            nc = block_rows - 1 - r
            rotated[nr][nc] = block
    return rotated  # type: ignore[return-value]


def flatten_block_grid(block_grid: Sequence[Sequence[Grid]]) -> List[Grid]:
    return [block for row in block_grid for block in row]


def abstraction_row_major_stack(grid: Grid) -> Grid:
    separator = find_separator_color(grid)
    blocks = extract_blocks(grid, separator)
    flat = flatten_block_grid(blocks)
    return assemble_blocks(flat, separator, orientation="vertical")


def abstraction_rotated_cycle(grid: Grid) -> Grid:
    separator = find_separator_color(grid)
    blocks = extract_blocks(grid, separator)
    rotated = rotate_blocks_clockwise(blocks)
    flat = flatten_block_grid(rotated)

    block_rows = len(blocks)
    block_cols = len(blocks[0]) if blocks else 0
    if block_rows > 1 and block_cols > 1:
        start_index = block_rows - 1
        flat = flat[start_index:] + flat[:start_index]
        orientation = "vertical"
    else:
        orientation = "horizontal" if len(rotated) == 1 else "vertical"

    return assemble_blocks(flat, separator, orientation)


Abstraction = Callable[[Grid], Grid]


@dataclass
class AbstractionResult:
    name: str
    matches: Dict[str, Optional[Tuple[int, int]]]
    first_failure: Dict[str, Optional[int]]


def evaluate_abstraction(name: str, fn: Abstraction, data: Dict[str, Sequence[Dict[str, Grid]]]) -> AbstractionResult:
    matches: Dict[str, Optional[Tuple[int, int]]] = {}
    first_failure: Dict[str, Optional[int]] = {}

    for split, examples in data.items():
        total = len(examples)
        ok = 0
        fail_index: Optional[int] = None
        has_ground_truth = all("output" in example for example in examples)

        for idx, example in enumerate(examples):
            predicted = fn(example["input"])
            if has_ground_truth and predicted == example["output"]:
                ok += 1
            elif has_ground_truth and fail_index is None and predicted != example["output"]:
                fail_index = idx

        matches[split] = (ok, total) if has_ground_truth else None
        first_failure[split] = fail_index if has_ground_truth else None
    return AbstractionResult(name=name, matches=matches, first_failure=first_failure)


def print_report(result: AbstractionResult) -> None:
    print(f"== {result.name} ==")
    for split, summary in result.matches.items():
        fail = result.first_failure[split]
        if summary is None:
            print(f"  {split}: generated outputs (no ground truth)")
        else:
            ok, total = summary
            fail_repr = "None" if fail is None else str(fail)
            print(f"  {split}: {ok}/{total} correct, first_failure={fail_repr}")


def main() -> None:
    data = load_task()
    abstractions: List[Tuple[str, Abstraction]] = [
        ("row_major_stack", abstraction_row_major_stack),
        ("rotated_cycle", abstraction_rotated_cycle),
    ]

    for name, fn in abstractions:
        result = evaluate_abstraction(name, fn, data)
        print_report(result)


if __name__ == "__main__":
    main()
