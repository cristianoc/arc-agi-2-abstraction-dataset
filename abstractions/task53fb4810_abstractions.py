"""Abstraction experiments for ARC task 53fb4810."""

from pathlib import Path
import json


TASK_PATH = Path(__file__).parent / "arc2_samples" / "53fb4810.json"


def load_task():
    return json.loads(TASK_PATH.read_text())


def _copy_grid(grid):
    return [row[:] for row in grid]


def identity_baseline(grid):
    return _copy_grid(grid)


def fill_topmost_four(grid):
    grid_copy = _copy_grid(grid)
    height = len(grid_copy)
    width = len(grid_copy[0])

    for col in range(width):
        top_row = None
        for row in range(height):
            if grid_copy[row][col] == 4:
                top_row = row
                break

        if top_row is None:
            continue

        for row in range(top_row - 1, -1, -1):
            grid_copy[row][col] = 4

    return grid_copy


def tile_mixed_component(grid):
    result = _copy_grid(grid)
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    targets = {2, 4}

    for r in range(h):
        for c in range(w):
            if grid[r][c] not in targets or seen[r][c]:
                continue

            stack = [(r, c)]
            seen[r][c] = True
            cells = []
            colors = set()

            while stack:
                rr, cc = stack.pop()
                color = grid[rr][cc]
                cells.append((rr, cc, color))
                colors.add(color)

                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc]:
                        if grid[nr][nc] in targets:
                            seen[nr][nc] = True
                            stack.append((nr, nc))

            if colors != targets:
                continue

            rows = [row for row, _, _ in cells]
            cols = [col for _, col, _ in cells]
            row_min, row_max = min(rows), max(rows)
            col_min, col_max = min(cols), max(cols)

            height = row_max - row_min + 1
            pattern_rows = [[] for _ in range(height)]
            for row, col, color in cells:
                pattern_rows[row - row_min].append((col - col_min, color))

            for row in range(row_min - 1, -1, -1):
                pattern_idx = (row - row_min) % height
                for dc, color in pattern_rows[pattern_idx]:
                    result[row][col_min + dc] = color

    return result


ABSTRACTIONS = {
    "identity": identity_baseline,
    "top4_fill": fill_topmost_four,
    "mixed_component": tile_mixed_component,
}


def evaluate(task, name, fn):
    print(f"== {name} ==")
    for split in ("train", "test", "arc-gen"):
        examples = task.get(split, [])
        if not examples:
            continue

        total = sum(1 for ex in examples if "output" in ex)
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

        print(
            f"  {split}: {matches}/{total} matches; first failure index: {first_failure}"
        )

    print()


def main():
    task = load_task()
    for name, fn in ABSTRACTIONS.items():
        evaluate(task, name, fn)

    test_examples = task.get("test", [])
    if test_examples:
        print("mixed_component prediction on test[0]:")
        pred = ABSTRACTIONS["mixed_component"](test_examples[0]["input"])
        for row in pred:
            print("".join(str(val) for val in row))


if __name__ == "__main__":
    main()
