"""Abstraction experiments for ARC task 58f5dbd5."""

import json
from collections import Counter
from pathlib import Path


TASK_PATH = Path(__file__).parent / "arc2_samples" / "58f5dbd5.json"

# 3×3 interior patterns used to paint 5×5 scoreboard glyphs.
PATTERNS = {
    (3, 1, 0, 0): ((0, 0, 0), (1, 0, 1), (0, 0, 0)),
    (3, 1, 1, 0): ((0, 1, 0), (0, 0, 1), (0, 1, 1)),
    (3, 1, 2, 0): ((0, 0, 0), (0, 1, 0), (0, 1, 0)),
    (1, 3, 0, 0): ((0, 0, 1), (1, 0, 1), (0, 0, 0)),
    (1, 3, 0, 1): ((0, 1, 0), (0, 0, 1), (0, 1, 0)),
    (1, 3, 0, 2): ((0, 1, 0), (0, 0, 0), (1, 0, 0)),
    (2, 2, 0, 0): ((0, 0, 1), (0, 0, 1), (1, 1, 0)),
    (2, 2, 0, 1): ((0, 1, 0), (0, 0, 0), (1, 0, 1)),
    (2, 2, 1, 0): ((0, 0, 0), (1, 0, 1), (1, 0, 1)),
    (2, 2, 1, 1): ((0, 1, 0), (0, 0, 1), (1, 0, 1)),
    (3, 2, 0, 0): ((0, 0, 1), (0, 0, 1), (1, 1, 0)),
    (3, 2, 0, 1): ((0, 1, 0), (0, 0, 0), (1, 0, 1)),
    (3, 2, 1, 0): ((0, 0, 0), (1, 0, 1), (1, 0, 1)),
    (3, 2, 1, 1): ((0, 1, 0), (0, 0, 1), (1, 0, 1)),
    (3, 2, 2, 0): ((0, 0, 0), (0, 1, 0), (0, 1, 0)),
    (3, 2, 2, 1): ((0, 1, 0), (1, 1, 0), (0, 1, 0)),
}


def load_task():
    return json.loads(TASK_PATH.read_text())


def copy_grid(grid):
    return [row[:] for row in grid]


def identity(grid):
    """Straight copy of the input (baseline)."""

    return copy_grid(grid)


def significant_colors(grid, min_pixels=10):
    counts = Counter(val for row in grid for val in row)
    background = counts.most_common(1)[0][0]
    colors = [c for c, n in counts.items() if c != background and n >= min_pixels]
    return background, colors


def centroids(grid, colors):
    info = {}
    for color in colors:
        coords = [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == color]
        if not coords:
            continue
        rr = [r for r, _ in coords]
        cc = [c for _, c in coords]
        info[color] = (sum(rr) / len(rr), sum(cc) / len(cc))
    return info


def choose_arrangement(colors, info):
    if not colors:
        return 0, 0

    rows = [pos[0] for pos in info.values()]
    cols = [pos[1] for pos in info.values()]
    row_spread = max(rows) - min(rows)
    col_spread = max(cols) - min(cols)
    count = len(colors)

    if col_spread < row_spread / 3:
        return count, 1
    if row_spread < col_spread / 3:
        return 1, count

    ratio = row_spread / max(col_spread, 1e-6)

    def factor_pairs(n):
        pairs = []
        for r in range(1, int(n ** 0.5) + 1):
            if n % r == 0:
                pairs.append((r, n // r))
                if r != n // r:
                    pairs.append((n // r, r))
        return pairs

    best_diff, best_pair = None, (count, 1)
    for r, c in factor_pairs(count):
        diff = abs((r / c) - ratio)
        if best_diff is None or diff < best_diff:
            best_diff, best_pair = diff, (r, c)
    return best_pair


def assign_positions(info, nrows, ncols):
    ordered = sorted(info.items(), key=lambda kv: kv[1][0])
    colors_per_row = max(1, ncols)
    row_index = {
        color: min(idx // colors_per_row, nrows - 1)
        for idx, (color, _) in enumerate(ordered)
    }

    ordered = sorted(info.items(), key=lambda kv: kv[1][1])
    colors_per_col = max(1, nrows)
    col_index = {
        color: min(idx // colors_per_col, ncols - 1)
        for idx, (color, _) in enumerate(ordered)
    }

    return {color: (row_index[color], col_index[color]) for color in info}


def draw_scoreboard(grid):
    background, colors = significant_colors(grid)
    if not colors:
        return copy_grid(grid)

    info = centroids(grid, colors)
    nrows, ncols = choose_arrangement(colors, info)
    if nrows == 0 or ncols == 0:
        return copy_grid(grid)

    mapping = assign_positions(info, nrows, ncols)
    height = nrows * 5 + (nrows + 1)
    width = ncols * 5 + (ncols + 1)
    out = [[background] * width for _ in range(height)]

    for color, (rr, cc) in mapping.items():
        pattern = PATTERNS.get((nrows, ncols, rr, cc))
        if pattern is None:
            return copy_grid(grid)

        start_r = 1 + rr * 6
        start_c = 1 + cc * 6

        for i in range(5):
            for j in range(5):
                if i in (0, 4) or j in (0, 4):
                    out[start_r + i][start_c + j] = color
                else:
                    out[start_r + i][start_c + j] = (
                        color if pattern[i - 1][j - 1] else background
                    )

    return out


ABSTRACTIONS = {
    "identity": identity,
    "scoreboard": draw_scoreboard,
}


def evaluate(task, name, fn):
    print(f"== {name} ==")
    for split in ("train", "test", "arc-gen"):
        cases = task.get(split, [])
        if not cases:
            continue

        total = sum(1 for ex in cases if "output" in ex)
        matches = 0
        first_failure = None

        for idx, example in enumerate(cases):
            prediction = fn(example["input"])
            target = example.get("output")
            if target is None:
                continue
            if prediction == target:
                matches += 1
            elif first_failure is None:
                first_failure = idx

        if total:
            print(f"  {split}: {matches}/{total} matched; first failure: {first_failure}")
        else:
            print(f"  {split}: {len(cases)} examples (no targets)")
    print()


def main():
    task = load_task()
    for name, fn in ABSTRACTIONS.items():
        evaluate(task, name, fn)

    test_examples = task.get("test", [])
    if test_examples:
        print("scoreboard prediction on test[0]:")
        pred = draw_scoreboard(test_examples[0]["input"])
        for row in pred:
            print("".join(str(cell) for cell in row))


if __name__ == "__main__":
    main()
