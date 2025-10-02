"""Exploratory abstractions for task e87109e9."""

from collections import Counter
import json
from pathlib import Path
from typing import Callable, List


DATA_PATH = Path(__file__).with_name("arc2_samples") / "e87109e9.json"
HEADER_COLOR = 5
BLOCK_WIDTH = 6
ROWS_PER_GROUP = 4
MASK_ROWS = 16


def identity_solver(grid):
    return [row[:] for row in grid]


_UNION_TEMPLATE = {
    1: [set(), {4, 5}, {4, 5}, {4, 5}],
    2: [{0, 1, 4, 5}, {0, 1, 4, 5}, {0, 1, 4, 5}, {0, 1, 2, 3, 4, 5}],
    3: [{0, 1, 2, 3, 4, 5}, {0, 1}, {0, 1, 2, 3, 4, 5}, {0, 1, 2, 3, 4, 5}],
    4: [{2, 3, 4, 5}, {0, 1, 2, 3, 4, 5}, {0, 1, 2, 3, 4, 5}, {0, 1, 2, 3, 4, 5}],
    6: [{2, 3, 4, 5}, {0, 1, 2, 3, 4, 5}, {0, 1, 2, 3, 4, 5}, {0, 1, 2, 3, 4, 5}],
}


def union_template_solver(grid):
    split = _find_body_start(grid)
    header = grid[:split]
    body = [row[:] for row in grid[split:]]
    if not body:
        return body

    header_colors = {val for row in header for val in row if val not in (0, HEADER_COLOR)}
    target = _find_target_color(body, header_colors)

    block_count = len(body[0]) // BLOCK_WIDTH
    for block in range(block_count):
        digit = _read_digit(header, block)
        groups = _UNION_TEMPLATE.get(digit)
        if not groups:
            continue
        start = block * BLOCK_WIDTH
        for r in range(min(len(body), ROWS_PER_GROUP * 4)):
            g = min(r // ROWS_PER_GROUP, 3)
            allowed = groups[g]
            for c in allowed:
                col = start + c
                if body[r][col] == target:
                    body[r][col] = 8
    return body


def nearest_neighbor_solver(grid):
    split = _find_body_start(grid)
    header = grid[:split]
    body = [row[:] for row in grid[split:]]
    if not body:
        return body

    header_colors = {val for row in header for val in row if val not in (0, HEADER_COLOR)}
    target_color = _find_target_color(body, header_colors)
    block_count = len(body[0]) // BLOCK_WIDTH

    for block in range(block_count):
        digit = _read_digit(header, block)
        if digit is None:
            continue
        target_mask = _compute_target_mask(body, block, target_color)
        diff_mask = _select_diff_mask(digit, target_mask)
        if diff_mask is None:
            continue
        _apply_diff_mask(body, block, target_color, diff_mask)

    return body


def _find_body_start(grid):
    for idx, row in enumerate(grid):
        if HEADER_COLOR not in row:
            return idx
    return len(grid)


def _find_target_color(body, header_colors):
    counts = Counter()
    for row in body:
        for val in row:
            if val != 8 and val not in header_colors:
                counts[val] += 1
    if counts:
        return counts.most_common(1)[0][0]
    fallback = Counter(val for row in body for val in row if val != 8)
    return fallback.most_common(1)[0][0] if fallback else 0


def _read_digit(header, block):
    start = block * BLOCK_WIDTH
    end = start + BLOCK_WIDTH
    for row in header[1:-1]:
        for val in row[start:end]:
            if val not in (0, HEADER_COLOR):
                return val
    return None


def _compute_target_mask(body, block, target_color):
    start = block * BLOCK_WIDTH
    end = start + BLOCK_WIDTH
    mask = []
    for r in range(MASK_ROWS):
        if r >= len(body):
            mask.append((0,) * BLOCK_WIDTH)
            continue
        mask.append(tuple(1 if body[r][c] == target_color else 0 for c in range(start, end)))
    return tuple(mask)


def _select_diff_mask(digit, target_mask):
    best = None
    best_score = None
    for sample_digit, sample_target, sample_diff in _SAMPLES:
        if sample_digit != digit:
            continue
        score = _hamming_distance(sample_target, target_mask)
        if best_score is None or score < best_score:
            best_score = score
            best = sample_diff
    return best


def _apply_diff_mask(body, block, target_color, diff_mask):
    start = block * BLOCK_WIDTH
    for r in range(min(len(body), MASK_ROWS)):
        for c in range(BLOCK_WIDTH):
            if diff_mask[r][c] and body[r][start + c] == target_color:
                body[r][start + c] = 8


def _hamming_distance(mask_a, mask_b):
    total = 0
    for row_a, row_b in zip(mask_a, mask_b):
        for val_a, val_b in zip(row_a, row_b):
            total += val_a != val_b
    return total


def _load_samples():
    with DATA_PATH.open() as fh:
        data = json.load(fh)
    samples = []
    for pair in data["train"]:
        input_grid = pair["input"]
        header_height = _find_body_start(input_grid)
        header = input_grid[:header_height]
        body = input_grid[header_height:]
        out = pair["output"]
        diff_counter = Counter()
        for r in range(len(out)):
            for c in range(len(out[0])):
                if out[r][c] != body[r][c]:
                    diff_counter[(body[r][c], out[r][c])] += 1
        target = None
        for (src, dst), cnt in diff_counter.items():
            if dst == 8:
                target = src
                break
        if target is None:
            header_colors = {val for row in header for val in row if val not in (0, HEADER_COLOR)}
            body_colors = Counter(val for row in body for val in row if val not in header_colors and val != 8)
            target = body_colors.most_common(1)[0][0]
        block_count = len(out[0]) // BLOCK_WIDTH
        for block in range(block_count):
            digit = _read_digit(header, block)
            if digit is None:
                continue
            target_mask = _compute_target_mask(body, block, target)
            diff_mask = tuple(
                tuple(1 if out[r][c] != body[r][c] else 0 for c in range(block * BLOCK_WIDTH, (block + 1) * BLOCK_WIDTH))
                for r in range(MASK_ROWS)
            )
            samples.append((digit, target_mask, diff_mask))
    return samples


# Preload samples for nearest-neighbour solver.
_SAMPLES = _load_samples()


def evaluate():
    with DATA_PATH.open() as fh:
        dataset = json.load(fh)

    solvers: List[tuple[str, Callable]] = [
        ("identity", identity_solver),
        ("union_template", union_template_solver),
        ("nearest_neighbor", nearest_neighbor_solver),
    ]

    for name, solver in solvers:
        train_ok, train_first = _evaluate_split(dataset["train"], solver)
        test_ok, test_first = _evaluate_split(dataset.get("test", []), solver)
        train_display = f"{train_ok:.2f}" if train_ok == train_ok else "n/a"
        test_display = f"{test_ok:.2f}" if test_ok == test_ok else "n/a"
        print(
            f"[{name}] train={train_display} first_train_fail={train_first} "
            f"test={test_display} first_test_fail={test_first}"
        )


def _evaluate_split(pairs, solver):
    if not pairs:
        return 0.0, None
    total = len(pairs)
    correct = 0
    first_fail = None
    for idx, pair in enumerate(pairs):
        predicted = solver(pair["input"])
        expected = pair.get("output")
        if expected is None:
            continue
        if predicted == expected:
            correct += 1
        elif first_fail is None:
            first_fail = idx
    evaluated = sum(1 for pair in pairs if pair.get("output") is not None)
    accuracy = correct / evaluated if evaluated else float("nan")
    return accuracy, first_fail


if __name__ == "__main__":
    evaluate()
