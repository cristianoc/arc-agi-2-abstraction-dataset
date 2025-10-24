"""Solver for ARC-AGI-2 task d35bdbdc, refactored to match the DSL lambda."""

from typing import Dict, List, Tuple, Optional, cast

Grid = List[List[int]]


def extractRingGadgets(grid: Grid) -> List[Dict[str, int]]:
    rings: List[Dict[str, int]] = []
    height = len(grid)
    width = len(grid[0])
    for r in range(1, height - 1):
        for c in range(1, width - 1):
            center = grid[r][c]
            ring_value: Optional[int] = None
            uniform = True
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    value = grid[r + dr][c + dc]
                    if ring_value is None:
                        ring_value = value
                    elif value != ring_value:
                        uniform = False
                        break
                if not uniform:
                    break
            if not uniform or ring_value is None or ring_value == center:
                continue
            rings.append({
                "center": center,
                "ring": ring_value,
                "row": r,
                "col": c,
            })
    return rings


def countBorderOccurrences(rings: List[Dict[str, int]]) -> Dict[int, int]:
    counts: Dict[int, int] = {}
    for info in rings:
        color = info["ring"]
        counts[color] = counts.get(color, 0) + 1
    return counts


def selectSinkPairs(
    rings: List[Dict[str, int]],
    _border_counts: Dict[int, int],
) -> List[Tuple[int, int]]:
    if not rings:
        return []

    ring_by_color: Dict[int, List[int]] = {}
    for idx, info in enumerate(rings):
        ring_by_color.setdefault(info["ring"], []).append(idx)

    status: List[str] = ["unknown"] * len(rings)
    partner: List[Optional[int]] = [None] * len(rings)

    while True:
        centers = {rings[i]["center"] for i in range(len(rings)) if status[i] == "unknown"}
        updated = False
        for idx, info in enumerate(rings):
            if status[idx] != "unknown":
                continue
            if info["ring"] in centers:
                continue
            updated = True
            candidates = ring_by_color.get(info["center"], [])
            match: Optional[int] = None
            for cid in candidates:
                if cid != idx and status[cid] == "unknown":
                    match = cid
                    break
            if match is not None:
                status[idx] = "keep"
                status[match] = "remove"
                partner[idx] = match
            else:
                status[idx] = "remove"
        if not updated:
            break

    for idx in range(len(rings)):
        if status[idx] == "unknown":
            status[idx] = "remove"

    pairs: List[Tuple[int, int]] = [
        (idx, cast(int, partner[idx]))
        for idx in range(len(rings))
        if status[idx] == "keep" and partner[idx] is not None
    ]
    return pairs


def pruneRings(grid: Grid, rings: List[Dict[str, int]], pairs: List[Tuple[int, int]]) -> Grid:
    out: Grid = [row[:] for row in grid]
    keep_map: Dict[int, int] = {k: v for (k, v) in pairs}
    for idx, info in enumerate(rings):
        r = info["row"]
        c = info["col"]
        if idx in keep_map:
            donor = keep_map[idx]
            out[r][c] = rings[donor]["center"]
        else:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    out[r + dr][c + dc] = 0
    return out


def solve_d35bdbdc(grid: Grid) -> Grid:
    rings = extractRingGadgets(grid)
    border_counts = countBorderOccurrences(rings)
    pairs = selectSinkPairs(rings, border_counts)
    return pruneRings(grid, rings, pairs)


p = solve_d35bdbdc
