"""Abstraction experiments for ARC task 80a900e0."""

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple


TASK_ID = "80a900e0"
TASK_PATH = Path(__file__).with_name("arc2_samples") / f"{TASK_ID}.json"


Grid = List[List[int]]
Pos = Tuple[int, int]


def load_task() -> Dict:
    return json.loads(TASK_PATH.read_text())


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def background_palette(grid: Grid) -> set[int]:
    counts = Counter(pixel for row in grid for pixel in row)
    palette = {c for c in (0, 1) if c in counts}
    if palette:
        return palette
    most_common = counts.most_common(1)
    return {most_common[0][0]} if most_common else {0}


def find_runs(points: Sequence[Pos], step: Pos) -> List[List[Pos]]:
    ordered = sorted(points)
    runs: List[List[Pos]] = []
    current: List[Pos] = []

    for r, c in ordered:
        if not current:
            current = [(r, c)]
            continue

        pr, pc = current[-1]
        if (r - pr, c - pc) == step:
            current.append((r, c))
        else:
            if len(current) >= 3:
                runs.append(current)
            current = [(r, c)]

    if len(current) >= 3:
        runs.append(current)

    return runs


def extend_handles(grid: Grid, guard_conflicts: bool) -> Grid:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    output = copy_grid(grid)
    background = background_palette(grid)

    coords_by_color: Dict[int, List[Pos]] = defaultdict(list)
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            if value not in background:
                coords_by_color[value].append((r, c))

    for color, coords in coords_by_color.items():
        sum_groups: Dict[int, List[Pos]] = defaultdict(list)
        diff_groups: Dict[int, List[Pos]] = defaultdict(list)

        for r, c in coords:
            sum_groups[r + c].append((r, c))
            diff_groups[r - c].append((r, c))

        target_sums: set[int] = set()
        target_diffs: set[int] = set()
        has_sum_runs = False
        has_diff_runs = False

        for points in sum_groups.values():
            runs = find_runs(points, (1, -1))
            if runs:
                has_sum_runs = True
                for run in runs:
                    first_r, first_c = run[0]
                    last_r, last_c = run[-1]
                    target_diffs.add(first_r - first_c)
                    target_diffs.add(last_r - last_c)

        for points in diff_groups.values():
            runs = find_runs(points, (1, 1))
            if runs:
                has_diff_runs = True
                for run in runs:
                    first_r, first_c = run[0]
                    last_r, last_c = run[-1]
                    target_sums.add(first_r + first_c)
                    target_sums.add(last_r + last_c)

        if has_sum_runs and has_diff_runs:
            continue

        def should_paint(r: int, c: int) -> bool:
            original = grid[r][c]
            if original not in background:
                return False
            if not guard_conflicts:
                return True
            current = output[r][c]
            return current in background or current == color

        if has_sum_runs:
            for diff in target_diffs:
                for r in range(rows):
                    c = r - diff
                    if 0 <= c < cols and should_paint(r, c):
                        output[r][c] = color

        if has_diff_runs:
            for total in target_sums:
                for r in range(rows):
                    c = total - r
                    if 0 <= c < cols and should_paint(r, c):
                        output[r][c] = color

    return output


def identity_baseline(grid: Grid) -> Grid:
    return copy_grid(grid)


def handle_extension_no_guard(grid: Grid) -> Grid:
    return extend_handles(grid, guard_conflicts=False)


def handle_extension_guarded(grid: Grid) -> Grid:
    return extend_handles(grid, guard_conflicts=True)


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": identity_baseline,
    "handle_extension_no_guard": handle_extension_no_guard,
    "handle_extension_guarded": handle_extension_guarded,
}


def evaluate(task: Dict, name: str, fn: Callable[[Grid], Grid]) -> None:
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
