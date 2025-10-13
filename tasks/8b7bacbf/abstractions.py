"""Abstraction experiments for ARC task 8b7bacbf."""

from collections import Counter, defaultdict, deque
import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple


TASK_ID = "8b7bacbf"
TASK_PATH = Path(__file__).with_name("arc2_samples") / f"{TASK_ID}.json"


Grid = List[List[int]]
Component = List[Tuple[int, int]]


def load_task() -> Dict:
    return json.loads(TASK_PATH.read_text())


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def zero_components(grid: Grid) -> Iterable[Tuple[Component, Optional[int]]]:
    """Yield (component, boundary_colour) pairs for 4-connected zero regions."""

    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]

    for r in range(h):
        for c in range(w):
            if grid[r][c] != 0 or seen[r][c]:
                continue

            queue = deque([(r, c)])
            seen[r][c] = True
            component: Component = []
            boundary = set()

            while queue:
                rr, cc = queue.popleft()
                component.append((rr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if not (0 <= nr < h and 0 <= nc < w):
                        continue
                    if grid[nr][nc] == 0 and not seen[nr][nc]:
                        seen[nr][nc] = True
                        queue.append((nr, nc))
                    elif grid[nr][nc] != 0:
                        boundary.add(grid[nr][nc])

            boundary_colour = next(iter(boundary)) if len(boundary) == 1 else None
            yield component, boundary_colour


def identity_baseline(grid: Grid) -> Grid:
    return copy_grid(grid)


def fill_all_enclosed(grid: Grid) -> Grid:
    """Fill every uniquely bounded zero component with the maximal colour."""

    result = copy_grid(grid)
    fill_colour = max(max(row) for row in grid)

    for component, boundary in zero_components(grid):
        if boundary is None:
            continue
        for r, c in component:
            result[r][c] = fill_colour

    return result


def distance_filtered_fill(grid: Grid) -> Grid:
    """Fill only cavities that are close to informative colours."""

    h, w = len(grid), len(grid[0])
    counts = Counter()
    positions = defaultdict(list)
    for r, row in enumerate(grid):
        for c, value in enumerate(row):
            counts[value] += 1
            positions[value].append((r, c))

    fill_colour = max(counts)
    result = copy_grid(grid)

    def min_distance(component: Component, colour: int) -> Optional[int]:
        pts = positions.get(colour)
        if not pts:
            return None
        best = None
        for rr, cc in component:
            for pr, pc in pts:
                dist = abs(rr - pr) + abs(cc - pc)
                if best is None or dist < best:
                    best = dist
                    if best == 0:
                        return 0
        return best

    for component, border_colour in zero_components(grid):
        if border_colour is None:
            continue

        candidate_colours = [
            colour
            for colour, count in counts.items()
            if colour not in (0, border_colour) and count > 1
        ]
        if not candidate_colours:
            continue

        higher = [colour for colour in candidate_colours if colour > border_colour]
        lower = [colour for colour in candidate_colours if colour <= border_colour]

        should_fill = False

        if higher:
            distances = [min_distance(component, colour) for colour in higher]
            distances = [d for d in distances if d is not None]
            if distances and min(distances) <= 4:
                should_fill = True

        if not should_fill and (not higher or border_colour > 2) and lower:
            distances = [min_distance(component, colour) for colour in lower]
            distances = [d for d in distances if d is not None]
            if distances and min(distances) <= 3:
                should_fill = True

        if should_fill:
            for r, c in component:
                result[r][c] = fill_colour

    return result


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": identity_baseline,
    "fill_all_enclosed": fill_all_enclosed,
    "distance_filtered_fill": distance_filtered_fill,
}


def evaluate(task: Dict, name: str, abstraction: Callable[[Grid], Grid]) -> None:
    print(f"== {name} ==")
    for split in ("train", "test", "arc-gen"):
        examples = task.get(split, [])
        if not examples:
            continue

        total = sum(1 for ex in examples if "output" in ex)
        matches = 0
        first_failure = None

        for idx, example in enumerate(examples):
            if "output" not in example:
                continue
            prediction = abstraction(example["input"])
            if prediction == example["output"]:
                matches += 1
            elif first_failure is None:
                first_failure = idx

        if total:
            print(
                f"  {split}: {matches}/{total} matches; "
                f"first failure index: {first_failure}"
            )
        else:
            print(f"  {split}: {len(examples)} examples (no outputs)")
    print()


if __name__ == "__main__":
    dataset = load_task()
    for name, abstraction in ABSTRACTIONS.items():
        evaluate(dataset, name, abstraction)
