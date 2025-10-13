"""Abstraction experiments for ARC task b5ca7ac4."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

Grid = List[List[int]]
Object = Dict[str, object]

DATA_PATH = Path("arc2_samples/b5ca7ac4.json")


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def detect_objects(grid: Grid) -> List[Object]:
    height = len(grid)
    width = len(grid[0]) if height else 0
    found: List[Object] = []
    seen = set()
    for r in range(height - 2):
        for c in range(width - 2):
            inner = grid[r][c]
            if inner == 0:
                continue
            if any(grid[r + dr][c + dc] != inner for dr in range(3) for dc in range(3)):
                continue
            if r > 0 and grid[r - 1][c] == inner:
                continue
            if c > 0 and grid[r][c - 1] == inner:
                continue
            if not (0 < r and 0 < c and r + 2 < height - 1 and c + 2 < width - 1):
                continue
            top, bottom = r - 1, r + 3
            left, right = c - 1, c + 3
            border = set()
            for x in range(left, right + 1):
                border.add(grid[top][x])
                border.add(grid[bottom][x])
            for y in range(top, bottom + 1):
                border.add(grid[y][left])
                border.add(grid[y][right])
            border.discard(inner)
            if len(border) != 1:
                continue
            outer = border.pop()
            if outer == 0:
                continue
            bbox = (top, bottom, left, right)
            if bbox in seen:
                continue
            seen.add(bbox)
            pattern = [grid[y][left : right + 1] for y in range(top, bottom + 1)]
            found.append({
                "outer": outer,
                "bbox": bbox,
                "pattern": [row[:] for row in pattern],
            })
    found.sort(key=lambda obj: (obj["bbox"][0], obj["bbox"][2]))
    return found


def background_color(grid: Grid) -> int:
    counts = [0] * 10
    for row in grid:
        for val in row:
            counts[val] += 1
    return max(range(10), key=lambda color: (counts[color], color))


def build_lanes(start: int, step: int, width: int, span: int) -> List[int]:
    lanes: List[int] = []
    position = start
    if step > 0:
        while position <= width - span:
            lanes.append(position)
            position += step
    else:
        while position >= 0:
            lanes.append(position)
            position += step
    if not lanes:
        lanes.append(max(0, min(start, width - span)))
    return lanes


def place_group(
    objects: Sequence[Object],
    lanes: Sequence[int],
    order_fn: Callable[[Object, Sequence[int]], Iterable[int]],
) -> List[Tuple[Object, int]]:
    usage = {lane: [] for lane in lanes}
    placements: List[Tuple[Object, int]] = []
    for obj in objects:
        top, bottom, _, _ = obj["bbox"]  # type: ignore[misc]
        chosen = None
        for lane in order_fn(obj, lanes):
            if lane not in usage:
                continue
            overlap = any(not (bottom < u_top or top > u_bottom) for u_top, u_bottom in usage[lane])
            if overlap:
                continue
            chosen = lane
            break
        if chosen is None:
            chosen = lanes[0]
        usage.setdefault(chosen, []).append((top, bottom))
        placements.append((obj, chosen))
    return placements


def render(grid: Grid, placements: Sequence[Tuple[Object, int]], span: int, fill: int) -> Grid:
    height = len(grid)
    width = len(grid[0]) if height else 0
    out = [[fill] * width for _ in range(height)]
    for obj, lane in placements:
        top, _, _, _ = obj["bbox"]  # type: ignore[misc]
        pattern: Grid = obj["pattern"]  # type: ignore[assignment]
        for dy in range(span):
            for dx in range(span):
                out[top + dy][lane + dx] = pattern[dy][dx]
    return out


def reposition(grid: Grid, right_strategy: str) -> Grid:
    objects = detect_objects(grid)
    if not objects:
        return copy_grid(grid)
    colors = sorted({obj["outer"] for obj in objects})
    if len(colors) != 2:
        return copy_grid(grid)

    left_color = max(colors)
    right_color = min(colors)
    left_objs = [obj for obj in objects if obj["outer"] == left_color]
    right_objs = [obj for obj in objects if obj["outer"] == right_color]
    if not left_objs or not right_objs:
        return copy_grid(grid)

    span = 5
    height = len(grid)
    width = len(grid[0]) if height else 0
    left_lanes = build_lanes(0, span, width, span)
    right_lanes = build_lanes(width - span, -span, width, span)

    def left_order(_obj: Object, lanes: Sequence[int]) -> Sequence[int]:
        return lanes

    if right_strategy == "threshold":
        avg_left = sum(obj["bbox"][2] for obj in right_objs) / len(right_objs)  # type: ignore[index]
    else:
        avg_left = None

    def right_order(obj: Object, lanes: Sequence[int]) -> Sequence[int]:
        if avg_left is not None and lanes:
            primary = lanes[0] if obj["bbox"][2] >= avg_left else (lanes[1] if len(lanes) > 1 else lanes[0])  # type: ignore[index]
        else:
            primary = lanes[0]
        ordered = [primary]
        for lane in lanes:
            if lane not in ordered:
                ordered.append(lane)
        return ordered

    placed_left = place_group(left_objs, left_lanes, left_order)
    placed_right = place_group(right_objs, right_lanes, right_order if right_strategy == "threshold" else lambda obj, lanes: lanes)
    all_placements = placed_left + placed_right

    return render(grid, all_placements, span, background_color(grid))


def abstraction_identity(grid: Grid) -> Grid:
    return copy_grid(grid)


def abstraction_lane_pack_naive(grid: Grid) -> Grid:
    return reposition(grid, right_strategy="naive")


def abstraction_lane_pack_threshold(grid: Grid) -> Grid:
    return reposition(grid, right_strategy="threshold")


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": abstraction_identity,
    "lane_pack_naive": abstraction_lane_pack_naive,
    "lane_pack_threshold": abstraction_lane_pack_threshold,
}


def _load_cases(split: str) -> List[Dict[str, Grid]]:
    with DATA_PATH.open() as fh:
        data = json.load(fh)
    return data.get(split, [])


def _load_arc_gen() -> List[Dict[str, Grid]]:
    candidate = Path("analysis/arc_gen/b5ca7ac4.json")
    if candidate.exists():
        with candidate.open() as fh:
            return json.load(fh)
    return []


def evaluate() -> None:
    splits = {
        "train": _load_cases("train"),
        "test": _load_cases("test"),
        "arc_gen": _load_arc_gen(),
    }
    for name, fn in ABSTRACTIONS.items():
        print(f"=== {name} ===")
        for split, cases in splits.items():
            if not cases:
                print(f"  {split}: 0 cases")
                continue
            if split == "train":
                matches = 0
                first_fail = None
                for idx, sample in enumerate(cases):
                    pred = fn(sample["input"])
                    if "output" not in sample:
                        continue
                    if pred == sample["output"]:
                        matches += 1
                    elif first_fail is None:
                        first_fail = idx
                total = len([c for c in cases if "output" in c])
                status = "ok" if matches == total else f"{matches}/{total}"
                extra = "" if first_fail is None else f" first_fail={first_fail}"
                print(f"  {split}: {status}{extra}")
            else:
                # No ground truth: show shape of prediction for sanity.
                shape_samples = []
                for sample in cases:
                    pred = fn(sample["input"])
                    shape_samples.append((len(pred), len(pred[0]) if pred else 0))
                shapes = ", ".join(f"{h}x{w}" for h, w in shape_samples[:3])
                print(f"  {split}: predicted shapes {shapes}")
        print()


if __name__ == "__main__":
    evaluate()
