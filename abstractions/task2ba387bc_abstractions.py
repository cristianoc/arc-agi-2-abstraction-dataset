"""Abstraction experiments for ARC task 2ba387bc."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

Grid = List[List[int]]
Example = Dict[str, Grid]

TASK_PATH = Path("analysis/arc2_samples/2ba387bc.json")


def load_task() -> Dict[str, Iterable[Example]]:
    data = json.loads(TASK_PATH.read_text())
    return data


def deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _extract_components(grid: Grid) -> List[Dict[str, object]]:
    height = len(grid)
    width = len(grid[0])
    seen = [[False] * width for _ in range(height)]
    components: List[Dict[str, object]] = []

    for r in range(height):
        for c in range(width):
            color = grid[r][c]
            if color == 0 or seen[r][c]:
                continue

            stack = [(r, c)]
            seen[r][c] = True
            min_r = max_r = r
            min_c = max_c = c

            while stack:
                y, x = stack.pop()
                min_r = min(min_r, y)
                max_r = max(max_r, y)
                min_c = min(min_c, x)
                max_c = max(max_c, x)

                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width and not seen[ny][nx] and grid[ny][nx] == color:
                        seen[ny][nx] = True
                        stack.append((ny, nx))

            pattern = [grid[row][min_c : max_c + 1] for row in range(min_r, max_r + 1)]
            has_zero = any(cell == 0 for row in pattern for cell in row)
            components.append(
                {
                    "color": color,
                    "top": min_r,
                    "left": min_c,
                    "pattern": [row[:] for row in pattern],
                    "hollow": has_zero,
                }
            )

    components.sort(key=lambda item: (item["top"], item["left"]))
    return components


def _resample_to_four(pattern: Grid) -> Grid:
    target = 4
    src_h = len(pattern)
    src_w = len(pattern[0])

    if src_h == target and src_w == target:
        return [row[:] for row in pattern]

    def sample(idx: int, size: int) -> int:
        return 0 if size == 1 else int(round(idx * (size - 1) / (target - 1)))

    resized: Grid = []
    for i in range(target):
        src_i = sample(i, src_h)
        row: List[int] = []
        for j in range(target):
            src_j = sample(j, src_w)
            row.append(pattern[src_i][src_j])
        resized.append(row)
    return resized


def _canonical_pattern(component: Optional[Dict[str, object]]) -> Grid:
    if component is None:
        return [[0] * 4 for _ in range(4)]
    pattern = component["pattern"]
    return _resample_to_four(pattern)  # type: ignore[arg-type]


def abstraction_identity(grid: Grid) -> Grid:
    return deep_copy(grid)


def abstraction_scan_pairing(grid: Grid) -> Grid:
    components = _extract_components(grid)
    output: Grid = []
    for i in range(0, len(components), 2):
        left = components[i]
        right = components[i + 1] if i + 1 < len(components) else None
        left_block = _canonical_pattern(left)
        right_block = _canonical_pattern(right)
        for lr, rr in zip(left_block, right_block):
            output.append(lr + rr)
    return output


def abstraction_hollow_vs_solid(grid: Grid) -> Grid:
    components = _extract_components(grid)
    hollows = [comp for comp in components if comp["hollow"]]
    solids = [comp for comp in components if not comp["hollow"]]

    pair_count = max(len(hollows), len(solids))
    output: Grid = []
    for idx in range(pair_count):
        left = hollows[idx] if idx < len(hollows) else None
        right = solids[idx] if idx < len(solids) else None
        left_block = _canonical_pattern(left)
        right_block = _canonical_pattern(right)
        for lr, rr in zip(left_block, right_block):
            output.append(lr + rr)
    return output


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": abstraction_identity,
    "scan_pairing": abstraction_scan_pairing,
    "hollow_vs_solid": abstraction_hollow_vs_solid,
}


def evaluate_split(examples: Iterable[Example], func: Callable[[Grid], Grid]) -> Tuple[int, int, Optional[int]]:
    matches = 0
    total = 0
    first_fail: Optional[int] = None
    for idx, example in enumerate(examples):
        prediction = func(example["input"])
        if "output" in example:
            total += 1
            if prediction == example["output"]:
                matches += 1
            elif first_fail is None:
                first_fail = idx
    return matches, total, first_fail


def main() -> None:
    task = load_task()
    splits = [
        ("train", task.get("train", [])),
        ("test", task.get("test", [])),
        ("arc-gen", task.get("arc-gen", [])),
    ]

    for name, func in ABSTRACTIONS.items():
        print(f"=== {name} ===")
        for split_name, examples in splits:
            if not examples:
                print(f"  {split_name}: no samples")
                continue
            matches, total, first_fail = evaluate_split(examples, func)
            if total == 0:
                print(f"  {split_name}: no references available")
            else:
                rate = matches / total * 100
                print(
                    f"  {split_name}: {matches}/{total} matched ({rate:.1f}%), "
                    f"first failure index: {first_fail if first_fail is not None else 'none'}"
                )
        print()


if __name__ == "__main__":
    main()

