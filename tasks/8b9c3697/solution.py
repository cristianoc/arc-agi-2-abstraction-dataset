"""Solver for ARC-AGI-2 task 8b9c3697, refactored to DSL-style main."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

Grid = List[List[int]]
Cell = Tuple[int, int]


def _copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _background(grid: Grid) -> int:
    counts = [0] * 10
    for row in grid:
        for v in row:
            counts[v] += 1
    return max(range(10), key=lambda c: (counts[c], c))


def _neighbors(r: int, c: int) -> Iterable[Cell]:
    yield r - 1, c
    yield r + 1, c
    yield r, c - 1
    yield r, c + 1


# --- DSL helpers (pure) ---

def extractObjects(grid: Grid) -> List[Dict[str, Any]]:
    """Non-background, non-2 connected objects with ids, cells, size, center."""
    bg = _background(grid)
    h = len(grid)
    w = len(grid[0]) if h else 0
    obj_id = [[-1] * w for _ in range(h)]
    objects: List[Dict[str, Any]] = []
    next_id = 0
    for r in range(h):
        for c in range(w):
            if grid[r][c] in (bg, 2) or obj_id[r][c] != -1:
                continue
            stack = [(r, c)]
            obj_id[r][c] = next_id
            cells: List[Cell] = []
            sum_r = 0
            sum_c = 0
            while stack:
                cr, cc = stack.pop()
                cells.append((cr, cc))
                sum_r += cr
                sum_c += cc
                for nr, nc in _neighbors(cr, cc):
                    if 0 <= nr < h and 0 <= nc < w and obj_id[nr][nc] == -1:
                        if grid[nr][nc] not in (bg, 2):
                            obj_id[nr][nc] = next_id
                            stack.append((nr, nc))
            size = len(cells)
            center = (sum_r / size, sum_c / size)
            objects.append({"id": next_id, "cells": cells, "size": size, "center": center})
            next_id += 1
    return objects


def extractTwoComponents(grid: Grid) -> List[Dict[str, Any]]:
    """Connected components of color 2 with cells, size, center."""
    h = len(grid)
    w = len(grid[0]) if h else 0
    seen = [[False] * w for _ in range(h)]
    out: List[Dict[str, Any]] = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] != 2 or seen[r][c]:
                continue
            stack = [(r, c)]
            seen[r][c] = True
            cells: List[Cell] = []
            sum_r = 0
            sum_c = 0
            while stack:
                cr, cc = stack.pop()
                cells.append((cr, cc))
                sum_r += cr
                sum_c += cc
                for nr, nc in _neighbors(cr, cc):
                    if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc] and grid[nr][nc] == 2:
                        seen[nr][nc] = True
                        stack.append((nr, nc))
            size = len(cells)
            center = (sum_r / size, sum_c / size)
            out.append({"cells": cells, "size": size, "center": center})
    return out


def _front_cells(cells: Sequence[Cell], dr: int, dc: int) -> List[Cell]:
    if dr == -1:
        key = min(r for r, _ in cells)
        return [(r, c) for r, c in cells if r == key]
    if dr == 1:
        key = max(r for r, _ in cells)
        return [(r, c) for r, c in cells if r == key]
    if dc == -1:
        key = min(c for _, c in cells)
        return [(r, c) for r, c in cells if c == key]
    key = max(c for _, c in cells)
    return [(r, c) for r, c in cells if c == key]


def enumerateCorridorCandidates(
    grid: Grid,
    two_components: Sequence[Dict[str, Any]],
    objects: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    """Enumerate valid straight corridors from each 2-component to objects.

    Returns a structure with:
      - components: the input components (for later application)
      - by_object: mapping object id -> list of candidate dicts
      - objects_by_id: id -> object dict
    """
    bg = _background(grid)
    h = len(grid)
    w = len(grid[0]) if h else 0

    # Build object id grid from objects' cells
    obj_id = [[-1] * w for _ in range(h)]
    for obj in objects:
        oid = obj["id"]  # type: ignore[index]
        for r, c in obj["cells"]:  # type: ignore[index]
            obj_id[r][c] = oid  # type: ignore[assignment]

    by_object: Dict[int, List[Dict[str, Any]]] = {}
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for comp_idx, comp in enumerate(two_components):
        cells: Sequence[Cell] = comp["cells"]  # type: ignore[assignment]
        if not cells:
            continue
        for dr, dc in directions:
            front = _front_cells(cells, dr, dc)
            if not front:
                continue
            shift: Optional[int] = None
            target: Optional[Cell] = None
            valid = True
            for fr, fc in front:
                steps = 0
                nr, nc = fr + dr, fc + dc
                while 0 <= nr < h and 0 <= nc < w and grid[nr][nc] == bg:
                    steps += 1
                    nr += dr
                    nc += dc
                if not (0 <= nr < h and 0 <= nc < w):
                    valid = False
                    break
                if grid[nr][nc] in (2, 0):
                    valid = False
                    break
                if steps == 0:
                    valid = False
                    break
                if shift is None:
                    shift = steps
                    target = (nr, nc)
                elif steps != shift:
                    valid = False
                    break
            if not valid or shift is None or shift > 8:
                continue
            tr, tc = target  # type: ignore[misc]
            oid = obj_id[tr][tc]
            if oid == -1:
                continue
            path_cells: set[Cell] = set()
            new_cells: set[Cell] = set()
            for r, c in cells:
                for step in range(shift):
                    path_cells.add((r + dr * step, c + dc * step))
                new_cells.add((r + dr * shift, c + dc * shift))
            cand: Dict[str, Any] = {
                "component": comp_idx,
                "shift": shift,
                "direction": (dr, dc),
                "path": path_cells,
                "new": new_cells,
                "component_size": comp["size"],
            }
            by_object.setdefault(oid, []).append(cand)

    objects_by_id = {obj["id"]: obj for obj in objects}  # type: ignore[index]
    return {"components": list(two_components), "by_object": by_object, "objects_by_id": objects_by_id}


def assignCorridors(candidates: Dict[str, Any]) -> Dict[str, Any]:
    """Choose at most one corridor per object using size/shift/distance tiebreaks."""
    components: Sequence[Dict[str, Any]] = candidates["components"]
    by_object: Dict[int, List[Dict[str, Any]]] = candidates["by_object"]
    objects_by_id: Dict[int, Dict[str, Any]] = candidates["objects_by_id"]

    # Sort objects by size, then id for stability
    objects_sorted = sorted(objects_by_id.values(), key=lambda o: (o["size"], o["id"]))

    assigned: Dict[int, Dict[str, Any]] = {}
    for obj in objects_sorted:
        opts = [cand for cand in by_object.get(obj["id"], []) if cand["component"] not in assigned]
        if not opts:
            continue
        for cand in opts:
            comp = components[cand["component"]]
            comp_center = comp["center"]
            obj_center = obj["center"]
            cand["distance"] = abs(comp_center[0] - obj_center[0]) + abs(comp_center[1] - obj_center[1])
        opts.sort(key=lambda c: (-c["component_size"], c["shift"], c["distance"]))
        best = opts[0]
        assigned[best["component"]] = best

    return {"components": list(components), "assigned": assigned}


def applyCorridorMoves(grid: Grid, assignments: Dict[str, Any]) -> Grid:
    """Apply chosen corridors; erase unassigned 2-components to background."""
    result = _copy(grid)
    bg = _background(grid)
    components: Sequence[Dict[str, Any]] = assignments["components"]
    assigned: Dict[int, Dict[str, Any]] = assignments["assigned"]

    for idx, comp in enumerate(components):
        chosen = assigned.get(idx)
        if chosen is None:
            for r, c in comp["cells"]:  # type: ignore[index]
                result[r][c] = bg
            continue
        for r, c in chosen["path"]:  # type: ignore[index]
            result[r][c] = 0
        for r, c in chosen["new"]:  # type: ignore[index]
            result[r][c] = 2
    return result


# --- Main (must match abstractions.md Lambda Representation) ---
def solve_8b9c3697(grid: Grid) -> Grid:
    objects = extractObjects(grid)
    two_components = extractTwoComponents(grid)
    candidates = enumerateCorridorCandidates(grid, two_components, objects)
    assignments = assignCorridors(candidates)
    return applyCorridorMoves(grid, assignments)


p = solve_8b9c3697
