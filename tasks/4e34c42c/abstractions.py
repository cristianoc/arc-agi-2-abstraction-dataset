"""Abstraction experiments for ARC task 4e34c42c."""

from __future__ import annotations

import json
from collections import Counter, deque
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

Grid = List[List[int]]
Block = List[List[int]]


# ---------------------------------------------------------------------------
# Shared geometry helpers
# ---------------------------------------------------------------------------


def deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def most_frequent_color(grid: Grid) -> int:
    cnt: Counter[int] = Counter()
    for row in grid:
        cnt.update(row)
    color, _ = max(cnt.items(), key=lambda item: (item[1], item[0]))
    return color


def pad_vertical(block: Block, background: int, height: int = 5) -> Block:
    current = len(block)
    if current == height:
        return deep_copy(block)
    if current > height:
        if current == 1:
            idxs = [0] * height
        else:
            idxs = [round(i * (current - 1) / (height - 1)) for i in range(height)]
        return [block[i][:] for i in idxs]
    top_pad = (height - current) // 2
    bottom_pad = height - current - top_pad
    width = len(block[0]) if block else 0
    pad_row = [background] * width
    result: Block = []
    result.extend(pad_row[:] for _ in range(top_pad))
    result.extend(row[:] for row in block)
    result.extend(pad_row[:] for _ in range(bottom_pad))
    return result


def extract_components(grid: Grid, background: int):
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    comps = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] == background or seen[r][c]:
                continue
            q: deque[Tuple[int, int]] = deque([(r, c)])
            seen[r][c] = True
            cells: List[Tuple[int, int]] = []
            min_r = max_r = r
            min_c = max_c = c
            while q:
                rr, cc = q.popleft()
                cells.append((rr, cc))
                if rr < min_r:
                    min_r = rr
                if rr > max_r:
                    max_r = rr
                if cc < min_c:
                    min_c = cc
                if cc > max_c:
                    max_c = cc
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc] and grid[nr][nc] != background:
                        seen[nr][nc] = True
                        q.append((nr, nc))
            block = [grid[row][min_c : max_c + 1] for row in range(min_r, max_r + 1)]
            comps.append(
                {
                    "bbox": (min_r, max_r, min_c, max_c),
                    "block": [row[:] for row in block],
                }
            )
    return comps


def classify(block: Block) -> str:
    height = len(block)
    width = len(block[0]) if block else 0
    if height < 5:
        return "wide_short" if width > 3 else "small_short"
    return "tall"


def dominant_color(block: Block, background: int) -> int:
    cnt: Counter[int] = Counter()
    for row in block:
        for value in row:
            if value != background:
                cnt[value] += 1
    if not cnt:
        return background
    return max(cnt.items(), key=lambda item: (item[1], item[0]))[0]


def normalize_block(block: Block, block_type: str, background: int) -> Block:
    if block_type == "wide_short":
        dom = dominant_color(block, background)
        height = len(block)
        width = len(block[0]) if block else 0
        valid_cols: List[int] = []
        for col in range(width):
            column = [block[row][col] for row in range(height)]
            if dom not in column:
                continue
            if any(val not in (background, dom) for val in column):
                continue
            valid_cols.append(col)
        if valid_cols:
            block = [row[valid_cols[0] : valid_cols[-1] + 1] for row in block]
        filtered = [
            [val if val == dom else background for val in row]
            for row in block
        ]
        return pad_vertical(filtered, background)
    return pad_vertical(block, background)


def column_set(block: Block):
    return {tuple(row[col] for row in block) for col in range(len(block[0]))}


def merge_blocks(left: Block, right: Block) -> Block:
    if not right or not right[0]:
        return deep_copy(left)
    if not left or not left[0]:
        return deep_copy(right)
    height = len(left)
    overlap = min(len(left[0]), len(right[0]))
    best = 0
    for k in range(1, overlap + 1):
        if all(left[row][-k:] == right[row][:k] for row in range(height)):
            best = k
    return [left[row][:] + right[row][best:] for row in range(height)]


def enrich_components(grid: Grid):
    background = most_frequent_color(grid)
    components = extract_components(grid, background)
    enriched = []
    for comp in components:
        y0, y1, x0, x1 = comp["bbox"]
        block = comp["block"]
        comp_type = classify(block)
        normalized = normalize_block(block, comp_type, background)
        enriched.append(
            {
                "type": comp_type,
                "normalized": normalized,
                "bbox": comp["bbox"],
                "y0": y0,
                "min_col": x0,
                "columns": column_set(normalized),
                "background": background,
            }
        )
    return background, enriched


# ---------------------------------------------------------------------------
# Abstractions
# ---------------------------------------------------------------------------


def abstraction_descending_min_col(grid: Grid) -> Grid:
    background, comps = enrich_components(grid)
    ordered = sorted(comps, key=lambda comp: -comp["min_col"])
    if not ordered:
        return deep_copy(grid)
    stack = ordered[0]["normalized"]
    for comp in ordered[1:]:
        stack = merge_blocks(stack, comp["normalized"])
    return [row[:] for row in stack]


def abstraction_type_priority(grid: Grid) -> Grid:
    background, comps = enrich_components(grid)
    if not comps:
        return deep_copy(grid)

    small_unique = []
    small_redundant = []
    wide = []
    tall = []
    for idx, comp in enumerate(comps):
        c_type = comp["type"]
        if c_type == "wide_short":
            wide.append(comp)
        elif c_type == "tall":
            tall.append(comp)
        else:
            other_cols = set().union(
                *(comps[j]["columns"] for j in range(len(comps)) if j != idx)
            )
            if comp["columns"].issubset(other_cols):
                small_redundant.append(comp)
            else:
                small_unique.append(comp)

    ordered = []
    ordered.extend(sorted(small_unique, key=lambda comp: comp["min_col"]))
    ordered.extend(sorted(wide, key=lambda comp: comp["y0"]))
    ordered.extend(sorted(tall, key=lambda comp: -comp["y0"]))
    ordered.extend(sorted(small_redundant, key=lambda comp: comp["min_col"]))

    if not ordered:
        return deep_copy(grid)
    stack = ordered[0]["normalized"]
    for comp in ordered[1:]:
        stack = merge_blocks(stack, comp["normalized"])
    return [row[:] for row in stack]


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "desc_min_col": abstraction_descending_min_col,
    "type_priority": abstraction_type_priority,
}


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------


def load_task() -> Dict[str, Sequence[Dict[str, Grid]]]:
    task_path = Path(__file__).resolve().parents[1] / "arc2_samples" / "4e34c42c.json"
    return json.loads(task_path.read_text())


def evaluate_split(name: str, pairs: Sequence[Dict[str, Grid]], fn: Callable[[Grid], Grid]):
    if not pairs or "output" not in pairs[0]:
        # No reference output available (e.g. evaluation split).
        return None, None
    for idx, pair in enumerate(pairs):
        pred = fn(pair["input"])
        if pred != pair["output"]:
            return False, idx
    return True, None


def run():
    task = load_task()
    splits = {
        "train": task.get("train", []),
        "test": task.get("test", []),
        "arc-gen": task.get("arc-gen", []),
    }
    for name, fn in ABSTRACTIONS.items():
        print(f"Abstraction: {name}")
        for split_name, pairs in splits.items():
            if not pairs:
                print(f"  {split_name:7s}: n/a (no samples)")
                continue
            ok, first_fail = evaluate_split(split_name, pairs, fn)
            if ok is None:
                print(f"  {split_name:7s}: ? (no ground truth)")
            else:
                status = "OK" if ok else f"fail@{first_fail}"
                print(f"  {split_name:7s}: {status}")
        print()


if __name__ == "__main__":
    run()
