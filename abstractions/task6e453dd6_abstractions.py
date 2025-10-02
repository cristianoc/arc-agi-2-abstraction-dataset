"""Abstraction experiments for ARC task 6e453dd6."""

from collections import Counter, deque
from pathlib import Path
import json


TASK_PATH = Path(__file__).parent / "arc2_samples" / "6e453dd6.json"


def _copy_grid(grid):
    return [row[:] for row in grid]


def _locate_five_column(grid):
    width = len(grid[0])
    for c in range(width):
        if any(row[c] == 5 for row in grid):
            return c
    return None


def _most_common_nonzero(grid):
    counts = Counter(cell for row in grid for cell in row)
    non_zero = [color for color in counts if color != 0]
    if non_zero:
        return max(non_zero, key=counts.__getitem__)
    return 0


def _highlight_color(grid, preferred=2):
    present = {cell for row in grid for cell in row}
    if preferred not in present:
        return preferred
    for candidate in range(10):
        if candidate not in present:
            return candidate
    return preferred


def _shift_against_five(grid):
    """Slide zero components so their right edge touches the five-column."""
    col_five = _locate_five_column(grid)
    if col_five is None:
        return _copy_grid(grid), None, None

    background = _most_common_nonzero(grid)
    height = len(grid)
    width = len(grid[0])
    result = _copy_grid(grid)

    for r in range(height):
        for c in range(col_five):
            result[r][c] = background

    visited = [[False] * width for _ in range(height)]
    for r in range(height):
        for c in range(col_five):
            if grid[r][c] == 0 and not visited[r][c]:
                component = []
                queue = deque([(r, c)])
                visited[r][c] = True
                while queue:
                    rr, cc = queue.popleft()
                    component.append((rr, cc))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = rr + dr, cc + dc
                        if 0 <= nr < height and 0 <= nc < col_five and not visited[nr][nc] and grid[nr][nc] == 0:
                            visited[nr][nc] = True
                            queue.append((nr, nc))

                rightmost = max(col for _, col in component)
                shift = max(0, (col_five - 1) - rightmost)
                for rr, cc in component:
                    result[rr][cc + shift] = 0

    for r in range(height):
        for c in range(col_five + 1, width):
            result[r][c] = grid[r][c]

    return result, background, col_five


def abstraction_identity(grid):
    return _copy_grid(grid)


def abstraction_slide_only(grid):
    shifted, _, _ = _shift_against_five(grid)
    return shifted


def abstraction_slide_pattern(grid):
    shifted, background, col_five = _shift_against_five(grid)
    if col_five is None:
        return shifted

    height = len(grid)
    width = len(grid[0])
    highlight = _highlight_color(grid)

    if col_five >= 3 and col_five + 1 < width:
        for r in range(height):
            window = shifted[r][col_five - 3 : col_five + 1]
            if window == [0, background, 0, 5]:
                for c in range(col_five + 1, width):
                    shifted[r][c] = highlight

    return shifted


def abstraction_slide_gap(grid):
    shifted, background, col_five = _shift_against_five(grid)
    if col_five is None:
        return shifted

    height = len(grid)
    width = len(grid[0])
    highlight = _highlight_color(grid)

    if col_five >= 2 and col_five + 1 < width:
        for r in range(height):
            if shifted[r][col_five - 1] == 0 and shifted[r][col_five - 2] == background:
                for c in range(col_five + 1, width):
                    shifted[r][c] = highlight

    return shifted


ABSTRACTIONS = [
    ("identity", abstraction_identity),
    ("slide_only", abstraction_slide_only),
    ("slide_pattern", abstraction_slide_pattern),
    ("slide_gap", abstraction_slide_gap),
]


def _load_samples():
    with TASK_PATH.open() as f:
        return json.load(f)


def _evaluate_abstraction(name, fn, samples):
    print(f"== {name} ==")
    for split in ("train", "test", "arc_gen"):
        entries = samples.get(split) or []
        if not entries:
            print(f"  {split}: n/a")
            continue

        total = len(entries)
        successes = 0
        first_failure = None
        predictions = []

        for idx, sample in enumerate(entries):
            prediction = fn(sample["input"])
            predictions.append(prediction)
            target = sample.get("output")
            if target is None:
                continue
            if prediction == target:
                successes += 1
            elif first_failure is None:
                first_failure = idx

        has_gt = all("output" in sample for sample in entries)
        if has_gt:
            status = f"{successes}/{total}"
            first = "none" if first_failure is None else str(first_failure)
            print(f"  {split}: {status} first_fail={first}")
        else:
            print(f"  {split}: generated {total} predictions (no GT available)")
            preview = predictions[0]
            print("    preview:")
            for row in preview:
                print("     ", "".join(str(v) for v in row))


def main():
    samples = _load_samples()
    for name, fn in ABSTRACTIONS:
        _evaluate_abstraction(name, fn, samples)


if __name__ == "__main__":
    main()
