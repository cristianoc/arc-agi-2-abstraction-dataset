"""Abstractions explored for ARC task db0c5428."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

DATA_PATH = Path("analysis/arc2_samples/db0c5428.json")

Grid = List[List[int]]
Block = List[List[int]]
Example = Dict[str, Grid]


def load_examples(path: Path = DATA_PATH) -> Dict[str, List[Example]]:
    return json.loads(path.read_text())


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def most_common_color(grid: Grid) -> int:
    counts: Counter[int] = Counter(value for row in grid for value in row)
    return counts.most_common(1)[0][0]


def bounding_box(grid: Grid, background: int) -> Optional[Tuple[int, int, int, int]]:
    coords = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value != background]
    if not coords:
        return None
    rows, cols = zip(*coords)
    return min(rows), max(rows), min(cols), max(cols)


def extract_blocks(grid: Grid, top: int, left: int) -> Dict[Tuple[int, int], Block]:
    blocks: Dict[Tuple[int, int], Block] = {}
    for br in range(3):
        for bc in range(3):
            rows = grid[top + br * 3 : top + (br + 1) * 3]
            block = [row[left + bc * 3 : left + (bc + 1) * 3] for row in rows]
            blocks[(br, bc)] = [row[:] for row in block]
    return blocks


def map_macro_index(mr: int, mc: int) -> Optional[Tuple[int, int]]:
    even_map = {0: 2, 2: 1, 4: 0}

    if (mr, mc) == (2, 2):
        return None
    if mr in {0, 4} and mc in {1, 3}:
        return (1, 1)
    if mc in {0, 4} and mr in {1, 3}:
        return (1, 1)
    if mr % 2 == 0 and mc % 2 == 0:
        return (even_map[mr], even_map[mc])
    if mr % 2 == 1 and mc % 2 == 1:
        return (2 * ((mr - 1) // 2), 2 * ((mc - 1) // 2))
    if mr % 2 == 1 and mc % 2 == 0:
        if mc in {0, 4}:
            return (1, 1)
        return (2 * ((mr - 1) // 2), even_map[mc])
    if mr in {0, 4}:
        return (1, 1)
    return (even_map[mr], 2 * ((mc - 1) // 2))


def build_center_block_single(blocks: Dict[Tuple[int, int], Block], background: int, ring_color: int) -> Block:
    counts: Counter[int] = Counter()
    for block in blocks.values():
        for row in block:
            for value in row:
                if value != background:
                    counts[value] += 1
    dominant = ring_color if not counts else counts.most_common(1)[0][0]
    return [[ring_color] * 3, [ring_color, dominant, ring_color], [ring_color] * 3]


def build_center_block_dual(
    blocks: Dict[Tuple[int, int], Block],
    background: int,
    corner_color: int,
    edge_color: int,
) -> Block:
    counts: Counter[int] = Counter()
    for block in blocks.values():
        for row in block:
            for value in row:
                if value != background:
                    counts[value] += 1
    dominant = edge_color if not counts else counts.most_common(1)[0][0]
    return [
        [corner_color, edge_color, corner_color],
        [edge_color, dominant, edge_color],
        [corner_color, edge_color, corner_color],
    ]


def apply_macro_layout(grid: Grid, *, dual_ring: bool) -> Grid:
    background = most_common_color(grid)
    bbox = bounding_box(grid, background)
    if bbox is None:
        return copy_grid(grid)

    r0, r1, c0, c1 = bbox
    if (r1 - r0 + 1) != 9 or (c1 - c0 + 1) != 9:
        return copy_grid(grid)

    blocks = extract_blocks(grid, r0, c0)

    edge_positions = [
        grid[r0 + 4][c0 + 2],
        grid[r0 + 4][c0 + 6],
        grid[r0 + 2][c0 + 4],
        grid[r0 + 6][c0 + 4],
    ]
    edge_color = edge_positions[0]
    if not all(color == edge_color for color in edge_positions):
        edge_color = max(set(edge_positions), key=edge_positions.count)

    if dual_ring:
        corner_positions = [
            grid[r0 + 2][c0 + 2],
            grid[r0 + 2][c0 + 6],
            grid[r0 + 6][c0 + 2],
            grid[r0 + 6][c0 + 6],
        ]
        corner_color = corner_positions[0]
        if not all(color == corner_color for color in corner_positions):
            corner_color = max(set(corner_positions), key=corner_positions.count)
        center_block = build_center_block_dual(blocks, background, corner_color, edge_color)
    else:
        center_block = build_center_block_single(blocks, background, edge_color)

    start_r = r0 - 3
    start_c = c0 - 3
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    if not (0 <= start_r and 0 <= start_c and start_r + 15 <= rows and start_c + 15 <= cols):
        return copy_grid(grid)

    out = copy_grid(grid)
    for mr in range(5):
        for mc in range(5):
            source = map_macro_index(mr, mc)
            block = center_block if source is None else blocks[source]
            for r in range(3):
                dest_r = start_r + mr * 3 + r
                row_block = block[r]
                row_out = out[dest_r]
                for c in range(3):
                    dest_c = start_c + mc * 3 + c
                    row_out[dest_c] = row_block[c]
    return out


# --- Abstractions ---------------------------------------------------------

def identity_abstraction(grid: Grid) -> Grid:
    return copy_grid(grid)


def macro_reflection_single_ring(grid: Grid) -> Grid:
    return apply_macro_layout(grid, dual_ring=False)


def macro_reflection_dual_ring(grid: Grid) -> Grid:
    return apply_macro_layout(grid, dual_ring=True)


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": identity_abstraction,
    "macro_single_ring": macro_reflection_single_ring,
    "macro_dual_ring": macro_reflection_dual_ring,
}


# --- Evaluation harness ---------------------------------------------------

def evaluate_split(
    examples: List[Example], fn: Callable[[Grid], Grid]
) -> Optional[Tuple[int, int, Optional[int]]]:
    total = len(examples)
    if total == 0:
        return (0, 0, None)

    if any("output" not in example for example in examples):
        return None

    solved = 0
    first_failure: Optional[int] = None
    for idx, example in enumerate(examples):
        prediction = fn(example["input"])
        if prediction == example["output"]:
            solved += 1
        elif first_failure is None:
            first_failure = idx
    return solved, total, first_failure


def format_result(stat: Optional[Tuple[int, int, Optional[int]]]) -> str:
    if stat is None:
        return "n/a"
    solved, total, first_failure = stat
    if total == 0:
        return "n/a"
    fail_str = "-" if first_failure is None else str(first_failure)
    return f"{solved}/{total} (first fail: {fail_str})"


def main() -> None:
    data = load_examples()
    splits: List[Tuple[str, List[Example]]] = [
        ("train", data.get("train", [])),
        ("test", data.get("test", [])),
        ("arc-gen", data.get("arc-gen", [])),
    ]

    for name, fn in ABSTRACTIONS.items():
        print(f"{name}:")
        for split_name, examples in splits:
            stat = evaluate_split(examples, fn)
            print(f"  {split_name}: {format_result(stat)}")
        print()


if __name__ == "__main__":
    main()
