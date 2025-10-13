"""Abstraction experiments for ARC task 58490d8a."""

from collections import deque
import json
from pathlib import Path


TASK_PATH = Path(__file__).parent / "arc2_samples" / "58490d8a.json"


def load_task():
    return json.loads(TASK_PATH.read_text())


def zero_rectangle(grid):
    zeros = [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == 0]
    if not zeros:
        return None
    rows, cols = zip(*zeros)
    return min(rows), max(rows), min(cols), max(cols)


def scoreboard_slice(grid):
    rect = zero_rectangle(grid)
    if rect is None:
        return [row[:] for row in grid]
    r0, r1, c0, c1 = rect
    return [row[c0 : c1 + 1] for row in grid[r0 : r1 + 1]]


def count_components(grid, color, rect, adjacency):
    r0, r1, c0, c1 = rect
    height = len(grid)
    width = len(grid[0])
    visited = [[False] * width for _ in range(height)]

    if adjacency == "4":
        moves = ((1, 0), (-1, 0), (0, 1), (0, -1))
    elif adjacency == "8":
        moves = tuple((dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc)
    else:
        raise ValueError("adjacency must be '4' or '8'")

    def in_board(row, col):
        return r0 <= row <= r1 and c0 <= col <= c1

    components = 0

    for row in range(height):
        for col in range(width):
            if in_board(row, col):
                continue
            if visited[row][col] or grid[row][col] != color:
                continue

            components += 1
            queue = deque([(row, col)])
            visited[row][col] = True

            while queue:
                cr, cc = queue.popleft()
                for dr, dc in moves:
                    nr, nc = cr + dr, cc + dc
                    if not (0 <= nr < height and 0 <= nc < width):
                        continue
                    if in_board(nr, nc) or visited[nr][nc] or grid[nr][nc] != color:
                        continue
                    visited[nr][nc] = True
                    queue.append((nr, nc))

    return components


def scoreboard_counts(grid, adjacency):
    rect = zero_rectangle(grid)
    if rect is None:
        return [row[:] for row in grid]

    r0, r1, c0, c1 = rect
    height = r1 - r0 + 1
    width = c1 - c0 + 1
    output = [[0] * width for _ in range(height)]
    cache = {}

    for out_row, src_row in enumerate(range(r0, r1 + 1)):
        row_color = None
        for src_col in range(c0, c1 + 1):
            val = grid[src_row][src_col]
            if val != 0:
                row_color = val
                break

        if row_color is None:
            continue

        if row_color not in cache:
            cache[row_color] = count_components(grid, row_color, rect, adjacency)

        repeats = cache[row_color]
        if repeats == 0:
            continue

        col = 1 if width > 1 else 0
        placed = 0
        while placed < repeats and col < width:
            output[out_row][col] = row_color
            placed += 1
            col += 2

        if placed < repeats:
            for fallback_col in range(width):
                if output[out_row][fallback_col] != 0:
                    continue
                output[out_row][fallback_col] = row_color
                placed += 1
                if placed == repeats:
                    break

    return output


ABSTRACTIONS = {
    "board_copy": scoreboard_slice,
    "count4": lambda grid: scoreboard_counts(grid, "4"),
    "count8": lambda grid: scoreboard_counts(grid, "8"),
}


def evaluate(task, name, fn):
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


def main():
    task = load_task()
    for name, fn in ABSTRACTIONS.items():
        evaluate(task, name, fn)

    test_examples = task.get("test", [])
    if test_examples:
        print("count8 prediction on test[0]:")
        pred = ABSTRACTIONS["count8"](test_examples[0]["input"])
        for row in pred:
            print("".join(str(val) for val in row))


if __name__ == "__main__":
    main()
