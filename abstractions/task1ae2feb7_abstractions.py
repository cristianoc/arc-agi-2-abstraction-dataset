"""Abstraction experiments for ARC task 1ae2feb7."""

from pathlib import Path
import json
from typing import List, Tuple


TASK_ID = "1ae2feb7"
TASK_PATH = Path(__file__).parent / "arc2_samples" / f"{TASK_ID}.json"

Grid = List[List[int]]


def load_task() -> dict:
    return json.loads(TASK_PATH.read_text())


def identity(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def repeat_last_nonzero_block(grid: Grid) -> Grid:
    """Repeat only the rightmost non-zero block left of the final 2."""

    output = [row[:] for row in grid]

    for r, row in enumerate(grid):
        try:
            barrier = max(c for c, val in enumerate(row) if val == 2)
        except ValueError:
            continue

        idx = barrier - 1
        while idx >= 0 and row[idx] == 0:
            idx -= 1

        if idx < 0:
            continue

        color = row[idx]
        length = 0
        while idx - length >= 0 and row[idx - length] == color:
            length += 1

        pos = barrier + 1
        width = len(row)
        while pos < width:
            output[r][pos] = color if (pos - barrier - 1) % max(length, 1) == 0 else 0
            pos += 1

    return output


def repeat_all_blocks(grid: Grid) -> Grid:
    """Project every non-zero block across the barrier column of 2s."""

    output = [row[:] for row in grid]

    for r, row in enumerate(grid):
        try:
            barrier = max(c for c, val in enumerate(row) if val == 2)
        except ValueError:
            continue

        segments: List[Tuple[int, int]] = []
        idx = 0
        while idx < barrier:
            color = row[idx]
            if color == 0:
                idx += 1
                continue

            start = idx
            while idx < barrier and row[idx] == color:
                idx += 1
            segments.append((color, idx - start))

        width = len(row)
        for color, length in reversed(segments):
            if length <= 0:
                continue
            pos = barrier + 1
            while pos < width:
                if output[r][pos] == 0:
                    output[r][pos] = color
                pos += length

    return output


ABSTRACTIONS = {
    "identity": identity,
    "repeat_last_nonzero_block": repeat_last_nonzero_block,
    "repeat_all_blocks": repeat_all_blocks,
}


def evaluate(task: dict, name: str, fn) -> None:
    print(f"== {name} ==")
    for split in ("train", "test", "arc-gen"):
        examples = task.get(split, [])
        if not examples:
            continue

        total = sum(1 for ex in examples if "output" in ex)
        matches = 0
        first_failure = None

        for idx, example in enumerate(examples):
            inp = example["input"]
            out = example.get("output")
            if out is None:
                continue

            pred = fn(inp)
            if pred == out:
                matches += 1
            elif first_failure is None:
                first_failure = idx

        if total:
            print(
                f"  {split}: {matches}/{total} matches; "
                f"first failure index: {first_failure}"
            )
        else:
            print(f"  {split}: {len(examples)} examples (no targets)")
    print()


def main() -> None:
    task = load_task()
    for name, fn in ABSTRACTIONS.items():
        evaluate(task, name, fn)


if __name__ == "__main__":
    main()
