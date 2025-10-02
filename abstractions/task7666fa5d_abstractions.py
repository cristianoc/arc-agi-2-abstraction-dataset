"""Abstractions explored while solving ARC task 7666fa5d."""

from __future__ import annotations

import json
from collections import Counter, deque
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

Grid = List[List[int]]
Cell = Tuple[int, int]
Component = Tuple[int, int, int]


def load_task() -> Dict[str, Sequence[Dict[str, Grid]]]:
    path = Path("analysis/arc2_samples/7666fa5d.json")
    return json.loads(path.read_text())


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def background_and_foreground(grid: Grid) -> Tuple[int, int] | Tuple[int, None]:
    counts = Counter(val for row in grid for val in row)
    if not counts:
        return 0, None
    background, _ = counts.most_common(1)[0]
    others = {val for val in counts if val != background}
    if len(others) != 1:
        return background, None
    return background, others.pop()


def diagonal_components(grid: Grid, color: int) -> List[Component]:
    height = len(grid)
    width = len(grid[0]) if height else 0
    visited = [[False] * width for _ in range(height)]
    components: List[Component] = []

    for r in range(height):
        for c in range(width):
            if grid[r][c] != color or visited[r][c]:
                continue

            dq = deque([(r, c)])
            visited[r][c] = True
            coords: List[Cell] = []

            while dq:
                x, y = dq.popleft()
                coords.append((x, y))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < height
                            and 0 <= ny < width
                            and not visited[nx][ny]
                            and grid[nx][ny] == color
                        ):
                            visited[nx][ny] = True
                            dq.append((nx, ny))

            diag_sum = coords[0][0] + coords[0][1]
            if any(x + y != diag_sum for x, y in coords):
                continue

            offsets = [y - x for x, y in coords]
            components.append((diag_sum, min(offsets), max(offsets)))

    components.sort()
    return components


def abstraction_identity(grid: Grid) -> Grid:
    """Baseline: return the input as-is."""

    return copy_grid(grid)


def abstraction_uv_box(grid: Grid) -> Grid:
    """Fill the interior of a coarse bounding box in (r+c, c-r) space."""

    background, foreground = background_and_foreground(grid)
    if foreground is None:
        return copy_grid(grid)

    comps = diagonal_components(grid, foreground)
    if len(comps) < 2:
        return copy_grid(grid)

    u_values = [comp[0] for comp in comps]
    min_candidates = sorted(comp[1] for comp in comps)
    max_candidates = sorted(comp[2] for comp in comps)

    u_min = min(u_values) + 1
    u_max = max(u_values) - 1
    if len(min_candidates) < 2 or len(max_candidates) < 2:
        return copy_grid(grid)

    v_min = min_candidates[1]
    v_max = max_candidates[-2]

    result = copy_grid(grid)
    height = len(grid)
    width = len(grid[0]) if height else 0

    for r in range(height):
        for c in range(width):
            if grid[r][c] != background:
                continue
            u = r + c
            v = c - r
            if u_min <= u <= u_max and v_min <= v <= v_max:
                result[r][c] = 2

    return result


def abstraction_component_lerp(grid: Grid) -> Grid:
    """Linear interpolation between component envelopes (over-fills top rows)."""

    background, foreground = background_and_foreground(grid)
    if foreground is None:
        return copy_grid(grid)

    comps = diagonal_components(grid, foreground)
    if len(comps) < 2:
        return copy_grid(grid)

    result = copy_grid(grid)
    height = len(grid)
    width = len(grid[0]) if height else 0

    for idx in range(len(comps) - 1):
        u0, v0_min, v0_max = comps[idx]
        u1, v1_min, v1_max = comps[idx + 1]
        span = u1 - u0
        if span <= 0:
            continue
        for step in range(span + 1):
            u = u0 + step
            t = step / span
            v_min = (1 - t) * v0_min + t * v1_min
            v_max = (1 - t) * v0_max + t * v1_max
            v_start = int(round(v_min))
            v_end = int(round(v_max))
            if v_start > v_end:
                v_start, v_end = v_end, v_start
            for v in range(v_start, v_end + 1):
                if (u + v) % 2 != 0:
                    continue
                r = (u - v) // 2
                c = (u + v) // 2
                if 0 <= r < height and 0 <= c < width and grid[r][c] == background:
                    result[r][c] = 2

    return result


def abstraction_component_corridor(grid: Grid) -> Grid:
    """Final solver: ensure each filled cell is bracketed by guide components."""

    background, foreground = background_and_foreground(grid)
    if foreground is None:
        return copy_grid(grid)

    comps = diagonal_components(grid, foreground)
    if len(comps) < 2:
        return copy_grid(grid)

    result = copy_grid(grid)
    height = len(grid)
    width = len(grid[0]) if height else 0

    for r in range(height):
        for c in range(width):
            if grid[r][c] != background:
                continue
            u = r + c
            v = c - r

            left_sum = None
            for comp_sum, v_min, v_max in comps:
                if comp_sum > u:
                    break
                if v_min <= v <= v_max:
                    left_sum = comp_sum

            if left_sum is None:
                continue

            right_sum = None
            for comp_sum, v_min, v_max in comps:
                if comp_sum < u:
                    continue
                if v_min <= v <= v_max:
                    right_sum = comp_sum
                    break

            if right_sum is None or left_sum >= right_sum:
                continue

            result[r][c] = 2

    return result


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": abstraction_identity,
    "uv_box": abstraction_uv_box,
    "component_lerp": abstraction_component_lerp,
    "component_corridor": abstraction_component_corridor,
}


def evaluate_split(split: str, cases: Sequence[Dict[str, Grid]]) -> None:
    print(f"[{split}]")
    has_output = cases and "output" in cases[0]

    for name, fn in ABSTRACTIONS.items():
        if not has_output:
            print(f"  {name}: (no expected outputs)")
            continue

        first_fail = None
        for idx, sample in enumerate(cases):
            prediction = fn(sample["input"])
            if prediction != sample["output"]:
                first_fail = idx
                break
        if first_fail is None:
            print(f"  {name}: PASS")
        else:
            print(f"  {name}: fail first-fail={first_fail}")

    if not has_output and cases:
        preview = ABSTRACTIONS["component_corridor"](cases[0]["input"])
        print("  component_corridor preview:")
        for row in preview:
            print("   ", "".join(str(v) for v in row))


def main() -> None:
    data = load_task()
    for split in ("train", "test", "arc-gen"):
        if split in data:
            evaluate_split(split, data[split])


if __name__ == "__main__":
    main()

