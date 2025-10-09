"""Solver for ARC-AGI-2 task 8b9c3697."""


def solve_8b9c3697(grid):
    """Move certain `2` clusters along clear corridors toward nearby structures."""

    from collections import Counter, deque

    height = len(grid)
    width = len(grid[0])

    orig = [row[:] for row in grid]
    result = [row[:] for row in grid]

    color_counts = Counter(color for row in grid for color in row)
    background = color_counts.most_common(1)[0][0]

    SHIFT_LIMIT = 8  # longest corridor observed in training examples

    # ------------------------------------------------------------------
    # Identify non-background, non-`2` structures as discrete objects.
    # ------------------------------------------------------------------
    object_id = [[-1] * width for _ in range(height)]
    objects = []

    def bfs_object(start_r, start_c, idx):
        queue = deque([(start_r, start_c)])
        object_id[start_r][start_c] = idx
        cells = []
        sum_r = 0
        sum_c = 0
        while queue:
            r, c = queue.popleft()
            cells.append((r, c))
            sum_r += r
            sum_c += c
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < height and 0 <= nc < width:
                    if object_id[nr][nc] == -1:
                        if orig[nr][nc] not in (background, 2):
                            object_id[nr][nc] = idx
                            queue.append((nr, nc))
        size = len(cells)
        center = (sum_r / size, sum_c / size)
        return {
            "id": idx,
            "cells": cells,
            "size": size,
            "center": center,
        }

    next_obj_id = 0
    for r in range(height):
        for c in range(width):
            if orig[r][c] in (background, 2) or object_id[r][c] != -1:
                continue
            objects.append(bfs_object(r, c, next_obj_id))
            next_obj_id += 1

    # ------------------------------------------------------------------
    # Locate connected components of color `2`.
    # ------------------------------------------------------------------
    visited = [[False] * width for _ in range(height)]
    components = []

    def bfs_two(start_r, start_c):
        queue = deque([(start_r, start_c)])
        visited[start_r][start_c] = True
        cells = []
        sum_r = 0
        sum_c = 0
        while queue:
            r, c = queue.popleft()
            cells.append((r, c))
            sum_r += r
            sum_c += c
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < height and 0 <= nc < width:
                    if not visited[nr][nc] and orig[nr][nc] == 2:
                        visited[nr][nc] = True
                        queue.append((nr, nc))
        size = len(cells)
        center = (sum_r / size, sum_c / size)
        return {
            "cells": cells,
            "size": size,
            "center": center,
        }

    for r in range(height):
        for c in range(width):
            if orig[r][c] == 2 and not visited[r][c]:
                components.append(bfs_two(r, c))

    if not components:
        return result

    # Pre-index objects for quick look-up.
    objects_by_id = {obj["id"]: obj for obj in objects}

    # ------------------------------------------------------------------
    # Enumerate corridor candidates linking `2` components to objects.
    # ------------------------------------------------------------------
    candidates_by_object = {obj["id"]: [] for obj in objects}

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for comp_idx, comp in enumerate(components):
        if not comp["cells"]:
            continue

        rows = [r for r, _ in comp["cells"]]
        cols = [c for _, c in comp["cells"]]
        min_r = min(rows)
        max_r = max(rows)
        min_c = min(cols)
        max_c = max(cols)

        for dr, dc in directions:
            if dr == -1:
                front = [(r, c) for r, c in comp["cells"] if r == min_r]
            elif dr == 1:
                front = [(r, c) for r, c in comp["cells"] if r == max_r]
            elif dc == -1:
                front = [(r, c) for r, c in comp["cells"] if c == min_c]
            else:  # dc == 1
                front = [(r, c) for r, c in comp["cells"] if c == max_c]

            if not front:
                continue

            shift = None
            target_pos = None
            valid = True

            for fr, fc in front:
                steps = 0
                nr, nc = fr + dr, fc + dc
                while 0 <= nr < height and 0 <= nc < width and orig[nr][nc] == background:
                    steps += 1
                    nr += dr
                    nc += dc

                if not (0 <= nr < height and 0 <= nc < width):
                    valid = False
                    break
                if orig[nr][nc] in (2, 0):
                    valid = False
                    break
                if steps == 0:
                    valid = False
                    break

                if shift is None:
                    shift = steps
                    target_pos = (nr, nc)
                elif steps != shift:
                    valid = False
                    break

            if not valid or shift is None or shift > SHIFT_LIMIT:
                continue

            target_r, target_c = target_pos
            target_object = object_id[target_r][target_c]
            if target_object == -1:
                continue

            path_cells = set()
            new_positions = set()
            for r, c in comp["cells"]:
                for step in range(shift):
                    path_cells.add((r + dr * step, c + dc * step))
                new_positions.add((r + dr * shift, c + dc * shift))

            obj_center = objects_by_id[target_object]["center"]
            comp_center = comp["center"]
            distance = abs(comp_center[0] - obj_center[0]) + abs(comp_center[1] - obj_center[1])

            candidates_by_object[target_object].append({
                "component": comp_idx,
                "shift": shift,
                "direction": (dr, dc),
                "path": path_cells,
                "new": new_positions,
                "component_size": comp["size"],
                "distance": distance,
            })

    # ------------------------------------------------------------------
    # Assign at most one corridor per object, preferring larger `2` blocks
    # and shorter corridors, then closer centroids for tie-breaking.
    # ------------------------------------------------------------------
    assigned_component = [None] * len(components)

    for obj in sorted(objects, key=lambda item: (item["size"], item["id"])):
        options = [cand for cand in candidates_by_object.get(obj["id"], []) if assigned_component[cand["component"]] is None]
        if not options:
            continue

        options.sort(key=lambda cand: (-cand["component_size"], cand["shift"], cand["distance"]))
        chosen = options[0]
        assigned_component[chosen["component"]] = chosen

    # ------------------------------------------------------------------
    # Apply moves or clean up unassigned components.
    # ------------------------------------------------------------------
    for idx, comp in enumerate(components):
        chosen = assigned_component[idx]
        if chosen is None:
            for r, c in comp["cells"]:
                result[r][c] = background
            continue

        for r, c in chosen["path"]:
            result[r][c] = 0
        for r, c in chosen["new"]:
            result[r][c] = 2

    return result


p = solve_8b9c3697
