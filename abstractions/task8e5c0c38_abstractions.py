"""Abstraction experiments for ARC task 8e5c0c38."""

from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


TASK_ID = "8e5c0c38"
TASK_PATH = Path(__file__).with_name("arc2_samples") / f"{TASK_ID}.json"


Grid = List[List[int]]
Pos = Tuple[int, int]


def load_task() -> Dict:
    return json.loads(TASK_PATH.read_text())


def background_color(grid: Grid) -> int:
    return Counter(pixel for row in grid for pixel in row).most_common(1)[0][0]


def pick_axis_and_removals(cells: Sequence[Pos]) -> Tuple[int, List[Pos]]:
    min_c = min(c for _, c in cells)
    max_c = max(c for _, c in cells)
    cells_set = set(cells)
    preferred_axis2 = min_c + max_c

    best_key = None
    best_axis2 = preferred_axis2
    best_removals: List[Pos] = []

    for axis2 in range(2 * min_c, 2 * max_c + 1):
        to_remove = [
            (r, c) for (r, c) in cells if (r, axis2 - c) not in cells_set
        ]
        key = (len(to_remove), abs(axis2 - preferred_axis2), axis2)
        if best_key is None or key < best_key:
            best_key = key
            best_axis2 = axis2
            best_removals = to_remove

    return best_axis2, best_removals


def collect_components(grid: Grid, background: int) -> Dict[int, List[List[Pos]]]:
    height = len(grid)
    width = len(grid[0]) if height else 0
    seen = [[False] * width for _ in range(height)]
    components: Dict[int, List[List[Pos]]] = defaultdict(list)

    for r in range(height):
        for c in range(width):
            value = grid[r][c]
            if value == background or seen[r][c]:
                continue

            queue: List[Pos] = [(r, c)]
            seen[r][c] = True
            current: List[Pos] = []

            while queue:
                cr, cc = queue.pop()
                current.append((cr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if not (0 <= nr < height and 0 <= nc < width):
                        continue
                    if seen[nr][nc] or grid[nr][nc] != value:
                        continue
                    seen[nr][nc] = True
                    queue.append((nr, nc))

            components[value].append(current)

    return components


def identity_baseline(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def component_axis_symmetry(grid: Grid) -> Grid:
    background = background_color(grid)
    result = [row[:] for row in grid]
    components = collect_components(grid, background)

    for color, comps in components.items():
        for cells in comps:
            if not cells:
                continue
            _, to_remove = pick_axis_and_removals(cells)
            for r, c in to_remove:
                result[r][c] = background

    return result


def global_color_symmetry(grid: Grid) -> Grid:
    background = background_color(grid)
    result = [row[:] for row in grid]
    by_color: Dict[int, List[Pos]] = defaultdict(list)

    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value != background:
                by_color[value].append((r, c))

    for color, cells in by_color.items():
        if not cells:
            continue
        _, to_remove = pick_axis_and_removals(cells)
        for r, c in to_remove:
            result[r][c] = background

    return result


ABSTRACTIONS = {
    "identity": identity_baseline,
    "component_axis_symmetry": component_axis_symmetry,
    "global_color_symmetry": global_color_symmetry,
}


def evaluate(task: Dict, name: str, fn) -> None:
    print(f"== {name} ==")
    for split in ("train", "test", "arc-gen"):
        examples = task.get(split, [])
        if not examples:
            continue

        total_with_targets = sum(1 for ex in examples if "output" in ex)
        matches = 0
        first_failure = None

        for idx, example in enumerate(examples):
            prediction = fn(example["input"])
            target = example.get("output")

            if target is None:
                continue

            if prediction == target:
                matches += 1
            elif first_failure is None:
                first_failure = idx

        if total_with_targets:
            print(
                f"  {split}: {matches}/{total_with_targets} matches; first failure index: {first_failure}"
            )
        else:
            print(f"  {split}: {len(examples)} examples (no targets)")

    print()


if __name__ == "__main__":
    task = load_task()
    for name, fn in ABSTRACTIONS.items():
        evaluate(task, name, fn)
