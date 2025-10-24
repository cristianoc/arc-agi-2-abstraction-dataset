"""Typed-DSL refactor for ARC-AGI-2 task b5ca7ac4 (evaluation split)."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Callable, TypedDict, cast
from dataclasses import dataclass


Grid = List[List[int]]


class Ring(TypedDict):
    outer: int
    bbox: Tuple[int, int, int, int]  # top, bottom, left, right
    pattern: Grid


@dataclass(frozen=True)
class LanePlan:
    background: int
    left_lanes: List[int]
    right_lanes: List[int]
    span: int
    right_avg_left: Optional[float] = None


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def detectRingObjects(grid: Grid) -> List[Ring]:
    h = len(grid)
    w = len(grid[0]) if h else 0
    rings: List[Ring] = []
    seen: set[Tuple[int, int, int, int]] = set()
    for r in range(h - 2):
        for c in range(w - 2):
            inner = grid[r][c]
            if inner == 0:
                continue
            if any(grid[r + dr][c + dc] != inner for dr in range(3) for dc in range(3)):
                continue
            if r > 0 and grid[r - 1][c] == inner:
                continue
            if c > 0 and grid[r][c - 1] == inner:
                continue
            if not (0 < r and 0 < c and r + 2 < h - 1 and c + 2 < w - 1):
                continue
            top, bottom = r - 1, r + 3
            left, right = c - 1, c + 3
            border: set[int] = set()
            for x in range(left, right + 1):
                border.add(grid[top][x])
                border.add(grid[bottom][x])
            for y in range(top, bottom + 1):
                border.add(grid[y][left])
                border.add(grid[y][right])
            border.discard(inner)
            if len(border) != 1:
                continue
            outer = next(iter(border))
            if outer == 0:
                continue
            bbox = (top, bottom, left, right)
            if bbox in seen:
                continue
            seen.add(bbox)
            pat = [grid[y][left : right + 1] for y in range(top, bottom + 1)]
            rings.append(cast(Ring, {"outer": outer, "bbox": bbox, "pattern": [row[:] for row in pat]}))
    rings.sort(key=lambda obj: (obj["bbox"][0], obj["bbox"][2]))
    return rings


def _background_color(grid: Grid) -> int:
    counts = [0] * 10
    for row in grid:
        for v in row:
            counts[v] += 1
    return max(range(10), key=lambda c: (counts[c], c))


def _build_lanes(start: int, step: int, width: int, span: int) -> List[int]:
    lanes: List[int] = []
    pos = start
    if step > 0:
        while pos <= width - span:
            lanes.append(pos)
            pos += step
    else:
        while pos >= 0:
            lanes.append(pos)
            pos += step
    if not lanes:
        lanes.append(max(0, min(start, width - span)))
    return lanes


def constructLanes(grid: Grid, rings: List[Ring]) -> LanePlan:
    h = len(grid)
    w = len(grid[0]) if h else 0
    span = 5
    left_lanes = _build_lanes(0, span, w, span)
    right_lanes = _build_lanes(w - span, -span, w, span)
    colors = sorted({r["outer"] for r in rings})
    right_avg_left: Optional[float]
    if len(colors) == 2:
        right_color = min(colors)
        right_objs = [r for r in rings if r["outer"] == right_color]
        right_avg_left = (
            sum(r["bbox"][2] for r in right_objs) / len(right_objs) if right_objs else None
        )
    else:
        right_avg_left = None
    return LanePlan(
        background=_background_color(grid),
        left_lanes=left_lanes,
        right_lanes=right_lanes,
        span=span,
        right_avg_left=float(right_avg_left) if right_avg_left is not None else None,
    )


def _place_group(
    objs: Sequence[Ring],
    lanes: Sequence[int],
    order_fn: Callable[[Ring, Sequence[int]], Iterable[int]],
) -> List[Tuple[Ring, int]]:
    usage: Dict[int, List[Tuple[int, int]]]= {lane: [] for lane in lanes}  # vertical spans per lane
    placements: List[Tuple[Ring, int]] = []
    for obj in objs:
        top, bottom, _, _ = obj["bbox"]
        ordered = order_fn(obj, lanes)
        chosen: Optional[int] = None
        for lane in ordered:
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


def assignRingLanes(rings: List[Ring], lane_plan: LanePlan) -> List[Tuple[Ring, int]]:
    colors = sorted({r["outer"] for r in rings})
    # If not exactly two outer colors, preserve original positions (identity).
    if len(colors) != 2:
        return [(r, r["bbox"][2]) for r in rings]

    left_color = max(colors)
    right_color = min(colors)
    left_objs = [r for r in rings if r["outer"] == left_color]
    right_objs = [r for r in rings if r["outer"] == right_color]

    # If either side empty, keep identity.
    if not left_objs or not right_objs:
        return [(r, r["bbox"][2]) for r in rings]

    left_lanes = lane_plan.left_lanes
    right_lanes = lane_plan.right_lanes
    avg_left = lane_plan.right_avg_left

    def left_order(_obj: Ring, lanes: Sequence[int]) -> Sequence[int]:
        return list(lanes)

    def right_order(obj: Ring, lanes: Sequence[int]) -> Sequence[int]:
        if avg_left is not None and lanes:
            primary = lanes[0] if obj["bbox"][2] >= avg_left else (lanes[1] if len(lanes) > 1 else lanes[0])
        else:
            primary = lanes[0] if lanes else 0
        ordered: List[int] = [primary]
        for lane in lanes:
            if lane not in ordered:
                ordered.append(lane)
        return ordered

    placed_left = _place_group(left_objs, left_lanes, left_order)
    placed_right = _place_group(right_objs, right_lanes, right_order)
    return placed_left + placed_right


def renderRingPlacements(grid: Grid, placements: Sequence[Tuple[Ring, int]], background: int) -> Grid:
    # Preserve the original canvas size.
    h = len(grid)
    w = len(grid[0]) if h else 0
    out = [[background] * w for _ in range(h)]
    for obj, lane in placements:
        top, _, _, _ = obj["bbox"]
        pat = obj["pattern"]
        span = len(pat)
        for dy in range(span):
            for dx in range(span):
                out[top + dy][lane + dx] = pat[dy][dx]
    return out


def solve_b5ca7ac4(grid: Grid) -> Grid:
    rings = detectRingObjects(grid)
    lane_plan = constructLanes(grid, rings)
    placements = assignRingLanes(rings, lane_plan)
    return renderRingPlacements(grid, placements, lane_plan.background)


p = solve_b5ca7ac4
