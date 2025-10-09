"""Abstraction experiments for ARC task 8b9c3697."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

Grid = List[List[int]]
Cell = Tuple[int, int]

DATA_PATH = Path("arc2_samples/8b9c3697.json")


def copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def background_color(grid: Grid) -> int:
    counts = [0] * 10
    for row in grid:
        for val in row:
            counts[val] += 1
    return max(range(10), key=lambda color: (counts[color], color))


def neighbors(r: int, c: int) -> Iterable[Cell]:
    yield r - 1, c
    yield r + 1, c
    yield r, c - 1
    yield r, c + 1


def extract_two_components(grid: Grid) -> List[Dict[str, object]]:
    height = len(grid)
    width = len(grid[0]) if height else 0
    seen = [[False] * width for _ in range(height)]
    out: List[Dict[str, object]] = []
    for r in range(height):
        for c in range(width):
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
                for nr, nc in neighbors(cr, cc):
                    if 0 <= nr < height and 0 <= nc < width and not seen[nr][nc] and grid[nr][nc] == 2:
                        seen[nr][nc] = True
                        stack.append((nr, nc))
            size = len(cells)
            center = (sum_r / size, sum_c / size)
            out.append({"cells": cells, "size": size, "center": center})
    return out


def extract_objects(grid: Grid, background: int) -> Tuple[List[Dict[str, object]], List[List[int]]]:
    height = len(grid)
    width = len(grid[0]) if height else 0
    object_id = [[-1] * width for _ in range(height)]
    objects: List[Dict[str, object]] = []
    next_id = 0
    for r in range(height):
        for c in range(width):
            if grid[r][c] in (background, 2) or object_id[r][c] != -1:
                continue
            stack = [(r, c)]
            object_id[r][c] = next_id
            cells: List[Cell] = []
            sum_r = 0
            sum_c = 0
            while stack:
                cr, cc = stack.pop()
                cells.append((cr, cc))
                sum_r += cr
                sum_c += cc
                for nr, nc in neighbors(cr, cc):
                    if 0 <= nr < height and 0 <= nc < width and object_id[nr][nc] == -1:
                        if grid[nr][nc] not in (background, 2):
                            object_id[nr][nc] = next_id
                            stack.append((nr, nc))
            size = len(cells)
            center = (sum_r / size, sum_c / size)
            objects.append({"id": next_id, "cells": cells, "size": size, "center": center})
            next_id += 1
    return objects, object_id


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


def scan_corridors(
    grid: Grid,
    background: int,
    components: Sequence[Dict[str, object]],
    object_id: Sequence[Sequence[int]],
    shift_limit: Optional[int],
) -> Dict[int, List[Dict[str, object]]]:
    height = len(grid)
    width = len(grid[0]) if height else 0
    by_object: Dict[int, List[Dict[str, object]]] = {}
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for comp_idx, comp in enumerate(components):
        cells: Sequence[Cell] = comp["cells"]  # type: ignore[assignment]
        for dr, dc in directions:
            front = _front_cells(cells, dr, dc)
            if not front:
                continue

            shift = None
            target_cell: Optional[Cell] = None
            valid = True
            for fr, fc in front:
                steps = 0
                nr, nc = fr + dr, fc + dc
                while 0 <= nr < height and 0 <= nc < width and grid[nr][nc] == background:
                    steps += 1
                    nr += dr
                    nc += dc
                if not (0 <= nr < height and 0 <= nc < width):
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
                    target_cell = (nr, nc)
                elif steps != shift:
                    valid = False
                    break

            if not valid or shift is None:
                continue
            if shift_limit is not None and shift > shift_limit:
                continue

            tr, tc = target_cell  # type: ignore[misc]
            obj_idx = object_id[tr][tc]
            if obj_idx == -1:
                continue

            path: List[Cell] = []
            new_positions: List[Cell] = []
            for r, c in cells:
                for step in range(shift):
                    path.append((r + dr * step, c + dc * step))
                new_positions.append((r + dr * shift, c + dc * shift))

            cand = {
                "component": comp_idx,
                "shift": shift,
                "direction": (dr, dc),
                "path": path,
                "new": new_positions,
            }
            by_object.setdefault(obj_idx, []).append(cand)

    return by_object


def apply_candidate(result: Grid, cand: Dict[str, object]) -> None:
    for r, c in cand["path"]:  # type: ignore[index]
        result[r][c] = 0
    for r, c in cand["new"]:  # type: ignore[index]
        result[r][c] = 2


# ---------------------------------------------------------------------------
# Abstractions
# ---------------------------------------------------------------------------


def abstraction_identity(grid: Grid) -> Grid:
    return copy_grid(grid)


def abstraction_greedy_slide(grid: Grid) -> Grid:
    """Initial attempt: slide along the first valid corridor per component."""

    bg = background_color(grid)
    result = copy_grid(grid)
    components = extract_two_components(grid)

    for idx, comp in enumerate(components):
        candidate = find_first_corridor(grid, bg, comp)
        if candidate is None:
            for r, c in comp["cells"]:  # type: ignore[index]
                result[r][c] = bg
        else:
            apply_candidate(result, candidate)
    return result


def find_first_corridor(grid: Grid, background: int, comp: Dict[str, object]) -> Optional[Dict[str, object]]:
    height = len(grid)
    width = len(grid[0]) if height else 0
    cells: Sequence[Cell] = comp["cells"]  # type: ignore[assignment]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        front = _front_cells(cells, dr, dc)
        if not front:
            continue
        shift = None
        valid = True
        for fr, fc in front:
            steps = 0
            nr, nc = fr + dr, fc + dc
            while 0 <= nr < height and 0 <= nc < width and grid[nr][nc] == background:
                steps += 1
                nr += dr
                nc += dc
            if not (0 <= nr < height and 0 <= nc < width):
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
            elif steps != shift:
                valid = False
                break
        if not valid or shift is None:
            continue

        path: List[Cell] = []
        new_positions: List[Cell] = []
        for r, c in cells:
            for step in range(shift):
                path.append((r + dr * step, c + dc * step))
            new_positions.append((r + dr * shift, c + dc * shift))
        return {
            "path": path,
            "new": new_positions,
        }
    return None


def abstraction_matched_corridors(grid: Grid) -> Grid:
    """Final heuristic: match `2` components to objects with scoring."""

    bg = background_color(grid)
    result = copy_grid(grid)

    objects, object_id = extract_objects(grid, bg)
    components = extract_two_components(grid)
    if not components:
        return result

    corridors = scan_corridors(grid, bg, components, object_id, shift_limit=8)

    objects_by_id = {obj["id"]: obj for obj in objects}
    assigned: Dict[int, Dict[str, object]] = {}

    for obj in sorted(objects, key=lambda item: (item["size"], item["id"])):
        candidates = [cand for cand in corridors.get(obj["id"], []) if cand["component"] not in assigned]
        if not candidates:
            continue
        for cand in candidates:
            comp = components[cand["component"]]
            cand["component_size"] = comp["size"]
            comp_center = comp["center"]
            obj_center = obj["center"]
            cand["distance"] = abs(comp_center[0] - obj_center[0]) + abs(comp_center[1] - obj_center[1])
        candidates.sort(key=lambda cand: (-cand["component_size"], cand["shift"], cand["distance"]))
        best = candidates[0]
        assigned[best["component"]] = best

    for idx, comp in enumerate(components):
        if idx not in assigned:
            for r, c in comp["cells"]:  # type: ignore[index]
                result[r][c] = bg
            continue
        apply_candidate(result, assigned[idx])

    return result


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": abstraction_identity,
    "greedy_slide": abstraction_greedy_slide,
    "matched_corridors": abstraction_matched_corridors,
}


def _load_cases(split: str) -> List[Dict[str, Grid]]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open() as fh:
        data = json.load(fh)
    return data.get(split, [])


def _load_arc_gen() -> List[Dict[str, Grid]]:
    candidate = Path("analysis/arc_gen/8b9c3697.json")
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
                total = 0
                first_fail: Optional[int] = None
                for idx, sample in enumerate(cases):
                    if "output" not in sample:
                        continue
                    total += 1
                    pred = fn(sample["input"])
                    if pred == sample["output"]:
                        matches += 1
                    elif first_fail is None:
                        first_fail = idx
                status = "ok" if matches == total else f"{matches}/{total}"
                extra = "" if first_fail is None else f" first_fail={first_fail}"
                print(f"  {split}: {status}{extra}")
            else:
                shapes = []
                for sample in cases[:3]:
                    pred = fn(sample["input"])
                    shapes.append((len(pred), len(pred[0]) if pred else 0))
                shape_str = ", ".join(f"{h}x{w}" for h, w in shapes)
                print(f"  {split}: predicted shapes {shape_str}")
        print()


if __name__ == "__main__":
    evaluate()
