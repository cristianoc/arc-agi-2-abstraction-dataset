"""Abstractions explored for ARC task edb79dae."""

from __future__ import annotations

from collections import Counter
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

Grid = List[List[int]]
ROI = Tuple[int, int, int, int]


def load_task() -> Dict[str, Sequence[Dict[str, Grid]]]:
    import json
    from pathlib import Path

    path = Path(__file__).with_name("arc2_samples") / "edb79dae.json"
    with path.open() as fh:
        return json.load(fh)


def bounding_box(grid: Grid, color: int) -> ROI:
    coords = [(r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == color]
    rows = [r for r, _ in coords]
    cols = [c for _, c in coords]
    return min(rows), max(rows), min(cols), max(cols)


def detect_block_size(grid: Grid, roi: ROI, ignored: Iterable[int]) -> int:
    ignore_set = set(ignored)
    min_r, max_r, min_c, max_c = roi
    counts: Counter[int] = Counter()
    for r in range(min_r + 1, max_r):
        row = grid[r][min_c + 1 : max_c]
        current = None
        run = 0
        for value in row:
            if value == current:
                run += 1
            else:
                if current is not None and current not in ignore_set and run > 0:
                    counts[run] += 1
                current = value
                run = 1
        if current is not None and current not in ignore_set and run > 0:
            counts[run] += 1
    return counts.most_common(1)[0][0]


def collect_digit_metadata(grid: Grid, roi: ROI, block: int) -> Tuple[int, Dict[int, Dict[str, object]]]:
    min_r, max_r, min_c, max_c = roi
    total_rows = len(grid)
    total_cols = len(grid[0])

    header_rows = grid[:min_r]
    top_bg = Counter(val for row in header_rows for val in row).most_common(1)[0][0]

    digit_colors = {
        grid[r][c]
        for r in range(min_r + 1, max_r)
        for c in range(min_c + 1, max_c)
        if grid[r][c] not in (5, top_bg)
    }

    block_limit = min(total_rows, min_r + block)
    patches: List[Tuple[Grid, set]] = []
    for r in range(block_limit - block + 1):
        for c in range(total_cols - block + 1):
            patch = [grid[r + dr][c : c + block] for dr in range(block)]
            colors = {val for row in patch for val in row}
            patches.append((patch, colors))

    info: Dict[int, Dict[str, object]] = {}
    for digit in digit_colors:
        mask_patch = None
        best = -1
        for patch, colors in patches:
            if colors == {digit, top_bg}:
                score = sum(cell == digit for row in patch for cell in row)
                if score > best:
                    best = score
                    mask_patch = patch
        if mask_patch is None:
            for patch, colors in patches:
                if digit in colors and top_bg in colors and len(colors) <= 3:
                    score = sum(cell == digit for row in patch for cell in row)
                    if score > best:
                        best = score
                        mask_patch = patch

        non_digit_counts: Counter[int] = Counter()
        digit_counts: Counter[int] = Counter()
        for patch, colors in patches:
            if digit in colors:
                for row in patch:
                    for value in row:
                        if value in (digit, top_bg, 5):
                            continue
                        if value in digit_colors:
                            digit_counts[value] += 1
                        else:
                            non_digit_counts[value] += 1

        if non_digit_counts:
            primary = non_digit_counts.most_common(1)[0][0]
        elif digit_counts:
            primary = digit_counts.most_common(1)[0][0]
        else:
            primary = digit

        info[digit] = {
            "mask": mask_patch,
            "primary": primary,
            "secondary": top_bg,
        }
    return top_bg, info


def render_roi(grid: Grid, roi: ROI, block: int, info: Dict[int, Dict[str, object]]) -> Grid:
    min_r, max_r, min_c, max_c = roi
    working = [row[:] for row in grid]
    masks = {
        digit: [[cell == digit for cell in row] for row in data["mask"]]
        for digit, data in info.items()
        if data["mask"] is not None
    }
    r = min_r + 1
    while r < max_r:
        inner = grid[r][min_c + 1 : max_c]
        if len(set(inner)) == 1:
            r += 1
            continue

        height = 1
        while r + height < max_r and grid[r + height][min_c + 1 : max_c] == inner:
            height += 1

        c = min_c + 1
        while c < max_c:
            digit = grid[r][c]
            if digit in masks:
                fits = True
                for dc in range(block):
                    if c + dc >= max_c:
                        fits = False
                        break
                    for dr in range(height):
                        if grid[r + dr][c + dc] != digit:
                            fits = False
                            break
                    if not fits:
                        break
                if fits:
                    mask = masks[digit]
                    primary = info[digit]["primary"]
                    secondary = info[digit]["secondary"]
                    for dr in range(height):
                        for dc in range(block):
                            rr = r + dr
                            cc = c + dc
                            if cc >= max_c:
                                continue
                            working[rr][cc] = primary if mask[dr % block][dc] else secondary
                    c += block
                    continue
            c += 1
        r += height
    return [row[min_c : max_c + 1] for row in working[min_r : max_r + 1]]


# ---------------------------------------------------------------------------
# Abstractions


def abstraction_primary_only(grid: Grid) -> Grid:
    """Map each digit block to a uniform primary colour (no mask)."""

    roi = bounding_box(grid, 5)
    top_rows = grid[: roi[0]]
    top_bg = Counter(val for row in top_rows for val in row).most_common(1)[0][0]
    block = detect_block_size(grid, roi, (top_bg, 5))
    _, info = collect_digit_metadata(grid, roi, block)

    # Overwrite mask info with full blocks so that rendering paints a solid colour.
    for data in info.values():
        mask = data["mask"]
        if mask is None:
            continue
        data["mask"] = [[True] * block for _ in range(block)]

    return render_roi(grid, roi, block, info)


def abstraction_template_fill(grid: Grid) -> Grid:
    """Full legend/template decoding used by the final solver."""

    roi = bounding_box(grid, 5)
    top_rows = grid[: roi[0]]
    top_bg = Counter(val for row in top_rows for val in row).most_common(1)[0][0]
    block = detect_block_size(grid, roi, (top_bg, 5))
    _, info = collect_digit_metadata(grid, roi, block)
    return render_roi(grid, roi, block, info)


# ---------------------------------------------------------------------------
# Harness


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "primary_only": abstraction_primary_only,
    "template_fill": abstraction_template_fill,
}


def evaluate():
    dataset = load_task()
    train = dataset.get("train", [])
    test = dataset.get("test", [])
    generated = dataset.get("arc_gen", [])

    for name, fn in ABSTRACTIONS.items():
        print(f"\n=== Abstraction: {name} ===")
        failures = []
        for idx, sample in enumerate(train):
            pred = fn(sample["input"])
            target = sample["output"]
            if pred != target:
                failures.append(idx)
        passed = len(train) - len(failures)
        pct = 100.0 * passed / max(1, len(train))
        first_fail = failures[0] if failures else None
        print(f"train: {passed}/{len(train)} ({pct:.1f}%)", end="")
        if first_fail is not None:
            print(f" first failure @ index {first_fail}")
        else:
            print(" all matched")

        if test:
            print("test predictions (no ground truth available):")
            for idx, sample in enumerate(test):
                pred = fn(sample["input"])
                print(f"  test[{idx}] -> {len(pred)}x{len(pred[0])}")

        if generated:
            matches = 0
            for sample in generated:
                pred = fn(sample["input"])
                if pred == sample.get("output"):
                    matches += 1
            print(f"arc-gen matched: {matches}/{len(generated)}")


if __name__ == "__main__":
    evaluate()
