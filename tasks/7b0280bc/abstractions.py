"""Abstraction experiments for ARC task 7b0280bc."""

from __future__ import annotations

import json
from collections import Counter, deque
from pathlib import Path
from typing import Callable, Iterable, List, Sequence


DATA_PATH = Path(__file__).resolve().parents[1] / "arc2_samples" / "7b0280bc.json"


def load_pairs(split: str) -> List[dict]:
    with DATA_PATH.open() as fh:
        data = json.load(fh)
    return data.get(split, [])


Grid = List[List[int]]


def deepcopy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def union_component_tree(grid: Grid) -> Grid:
    """Prototype: decision tree over union components (initial attempt)."""

    h, w = len(grid), len(grid[0])
    counts = Counter(cell for row in grid for cell in row)
    background, _ = counts.most_common(1)[0]
    colors = [c for c, _ in counts.most_common() if c != background][:2]
    if len(colors) < 2:
        return deepcopy_grid(grid)
    major, minor = colors[0], colors[1]

    visited = [[False] * w for _ in range(h)]
    target = set()

    def classify(color: int, size: int, row_min: int, row_max: int, col_min: int) -> bool:
        if row_min <= 1:
            return color > 0
        if color == 0:
            if row_max <= 9:
                return False
            return size <= 10
        return row_max <= 3

    for r in range(h):
        for c in range(w):
            if visited[r][c] or grid[r][c] not in colors:
                continue
            color = grid[r][c]
            q = deque([(r, c)])
            visited[r][c] = True
            cells = []
            while q:
                y, x = q.popleft()
                cells.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and not visited[ny][nx] and grid[ny][nx] in colors:
                        visited[ny][nx] = True
                        q.append((ny, nx))
            rows = [y for y, _ in cells]
            cols = [x for _, x in cells]
            if classify(color, len(cells), min(rows), max(rows), min(cols)):
                target.update(cells)

    result = deepcopy_grid(grid)
    for y, x in target:
        result[y][x] = 5 if grid[y][x] == major else 3
    return result


def color_component_tree(grid: Grid) -> Grid:
    """Final abstraction: decision tree over monochrome components."""

    h, w = len(grid), len(grid[0])
    counts = Counter(cell for row in grid for cell in row)
    background, _ = counts.most_common(1)[0]
    colors = [c for c, _ in counts.most_common() if c != background][:2]
    if len(colors) < 2:
        return deepcopy_grid(grid)
    major, minor = colors[0], colors[1]

    visited = [[False] * w for _ in range(h)]
    target = set()

    def classify(color: int, size: int, row_min: int, row_max: int, col_min: int) -> bool:
        if row_min <= 1:
            if color <= 3:
                return col_min <= 4
            return True
        if color <= 3:
            if row_max <= 9:
                return False
            if size <= 3:
                return True
            if color <= 1:
                return size > 6
            return True
        if row_min <= 3:
            if color <= 5:
                return col_min <= 4
            return True
        return False

    for r in range(h):
        for c in range(w):
            if visited[r][c] or grid[r][c] not in colors:
                continue
            color = grid[r][c]
            q = deque([(r, c)])
            visited[r][c] = True
            cells = []
            while q:
                y, x = q.popleft()
                cells.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and not visited[ny][nx] and grid[ny][nx] == color:
                        visited[ny][nx] = True
                        q.append((ny, nx))
            rows = [y for y, _ in cells]
            cols = [x for _, x in cells]
            if classify(color, len(cells), min(rows), max(rows), min(cols)):
                target.update(cells)

    result = deepcopy_grid(grid)
    for y, x in target:
        result[y][x] = 5 if grid[y][x] == major else 3
    return result


ABSTRACTIONS: Sequence[tuple[str, Callable[[Grid], Grid]]] = (
    ("union_component_tree", union_component_tree),
    ("color_component_tree", color_component_tree),
)


def evaluate(split: str, pairs: Iterable[dict]) -> dict:
    stats = {}
    for name, fn in ABSTRACTIONS:
        total = 0
        ok = 0
        first_fail = None
        for idx, pair in enumerate(pairs):
            inp = pair["input"]
            out = pair.get("output")
            pred = fn(inp)
            if out is None:
                continue
            total += 1
            if pred == out:
                ok += 1
            elif first_fail is None:
                first_fail = idx
        stats[name] = {
            "total": total,
            "ok": ok,
            "first_fail": first_fail,
        }
    return stats


def main() -> None:
    for split in ("train", "test", "arc_gen"):
        pairs = load_pairs(split)
        if not pairs:
            print(f"[{split}] no pairs found")
            continue
        stats = evaluate(split, pairs)
        print(f"[{split}]")
        for name, info in stats.items():
            total = info["total"]
            ok = info["ok"]
            first = info["first_fail"]
            if total:
                ratio = ok / total
                print(f"  {name:25s} {ok:2d}/{total:<2d} match {ratio:.2f} first_fail={first}")
            else:
                print(f"  {name:25s} no labelled pairs")

        # For test split, echo the predicted grid from the current best abstraction.
        if split == "test":
            best_name, best_fn = ABSTRACTIONS[-1]
            pred = best_fn(pairs[0]["input"])
            print(f"  sample prediction by {best_name}:")
            for row in pred:
                print("   ", row)


if __name__ == "__main__":
    main()
