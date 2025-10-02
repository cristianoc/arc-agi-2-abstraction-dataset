"""Solver for ARC-AGI-2 task 581f7754 (split: evaluation)."""

from collections import Counter, deque, defaultdict


def most_common_color(grid):
    counts = Counter()
    for row in grid:
        counts.update(row)
    return counts.most_common(1)[0][0]


def extract_components(grid, background):
    height, width = len(grid), len(grid[0])
    visited = [[False] * width for _ in range(height)]
    components = []

    for r in range(height):
        for c in range(width):
            if grid[r][c] == background or visited[r][c]:
                continue
            queue = deque([(r, c)])
            visited[r][c] = True
            cells = []
            color_positions = defaultdict(list)
            min_r = max_r = r
            min_c = max_c = c
            while queue:
                x, y = queue.popleft()
                cells.append((x, y))
                color_positions[grid[x][y]].append((x, y))
                min_r = min(min_r, x)
                max_r = max(max_r, x)
                min_c = min(min_c, y)
                max_c = max(max_c, y)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < height and 0 <= ny < width:
                        if not visited[nx][ny] and grid[nx][ny] != background:
                            visited[nx][ny] = True
                            queue.append((nx, ny))
            components.append(
                {
                    "cells": cells,
                    "color_positions": color_positions,
                    "bbox": (min_r, max_r, min_c, max_c),
                }
            )
    return components


def choose_anchor(anchors, height, width):
    def score(rc):
        r, c = rc
        margin_row = min(r, height - 1 - r)
        margin_col = min(c, width - 1 - c)
        return (margin_row + margin_col, margin_row, margin_col, -r, -c)

    return max(anchors, key=score)


def determine_color_targets(grid, components, background):
    height, width = len(grid), len(grid[0])
    anchors = defaultdict(list)
    for comp in components:
        if len(comp["cells"]) == 1:
            r, c = comp["cells"][0]
            color = grid[r][c]
            anchors[color].append((r, c))

    # map color -> (axis, target)
    targets = {}
    anchor_coords = {}
    color_comp_positions = defaultdict(list)
    for idx, comp in enumerate(components):
        for color, positions in comp["color_positions"].items():
            rows = {r for r, _ in positions}
            cols = {c for _, c in positions}
            color_comp_positions[color].append((idx, rows, cols))

    for color, anchor_positions in anchors.items():
        anchor_r, anchor_c = choose_anchor(anchor_positions, height, width)
        anchor_coords[color] = (anchor_r, anchor_c)
        entries = color_comp_positions.get(color, [])
        if len(entries) <= 1:
            # Nothing to align if the color only appears in the anchor component.
            continue

        row_offsets = []
        col_offsets = []
        feasible_row = True
        feasible_col = True
        for _, rows, cols in entries:
            if len(rows) != 1:
                feasible_row = False
            else:
                row_offsets.append(next(iter(rows)))
            if len(cols) != 1:
                feasible_col = False
            else:
                col_offsets.append(next(iter(cols)))

        cost_row = None
        cost_col = None
        if feasible_row and row_offsets:
            cost_row = sum(abs(anchor_r - r) for r in row_offsets)
        if feasible_col and col_offsets:
            cost_col = sum(abs(anchor_c - c) for c in col_offsets)

        if cost_row is None and cost_col is None:
            continue
        if cost_row is not None and cost_col is not None:
            if cost_col < cost_row:
                axis = "col"
            elif cost_row < cost_col:
                axis = "row"
            else:
                margin_row = min(anchor_r, height - 1 - anchor_r)
                margin_col = min(anchor_c, width - 1 - anchor_c)
                if margin_col > margin_row:
                    axis = "col"
                elif margin_row > margin_col:
                    axis = "row"
                else:
                    max_shift_row = max(abs(anchor_r - r) for r in row_offsets) if row_offsets else 0
                    max_shift_col = max(abs(anchor_c - c) for c in col_offsets) if col_offsets else 0
                    if max_shift_col < max_shift_row:
                        axis = "col"
                    elif max_shift_row < max_shift_col:
                        axis = "row"
                    else:
                        axis = "row"
        elif cost_col is not None:
            axis = "col"
        else:
            axis = "row"

        target = anchor_c if axis == "col" else anchor_r
        targets[color] = (axis, target)

    return targets, anchor_coords


def compute_component_shift(comp, color_targets):
    row_shifts = []
    col_shifts = []
    for color, positions in comp["color_positions"].items():
        if color not in color_targets:
            continue
        axis, target = color_targets[color]
        if axis == "row":
            rows = {r for r, _ in positions}
            if len(rows) != 1:
                continue
            row_shifts.append(target - next(iter(rows)))
        else:
            cols = {c for _, c in positions}
            if len(cols) != 1:
                continue
            col_shifts.append(target - next(iter(cols)))

    dr = row_shifts[0] if row_shifts else 0
    dc = col_shifts[0] if col_shifts else 0
    if any(shift != dr for shift in row_shifts):
        dr = 0
    if any(shift != dc for shift in col_shifts):
        dc = 0
    return dr, dc


def compute_shifts(components, color_targets):
    return [compute_component_shift(comp, color_targets) for comp in components]


def refine_row_targets(components, shifts, color_targets, anchor_coords, width):
    for color, (axis, target) in color_targets.items():
        if axis != "row" or color not in anchor_coords:
            continue
        anchor_r, anchor_c = anchor_coords[color]
        entries = []
        for idx, comp in enumerate(components):
            if color not in comp["color_positions"]:
                continue
            positions = comp["color_positions"][color]
            rows = {r for r, _ in positions}
            if len(rows) != 1:
                continue
            row_origin = next(iter(rows))
            dr, dc = shifts[idx]
            min_r, max_r, min_c, max_c = comp["bbox"]
            comp_width = max_c - min_c + 1
            cur_left = min_c + dc
            cur_right = max_c + dc
            is_anchor_component = any((r, c) == (anchor_r, anchor_c) for r, c in comp["cells"])
            has_col_constraint = any(
                other != color and other in color_targets and color_targets[other][0] == "col"
                for other in comp["color_positions"]
            )
            entries.append(
                {
                    "idx": idx,
                    "row_origin": row_origin,
                    "dr": dr,
                    "min_c": min_c,
                    "width": comp_width,
                    "cur_left": cur_left,
                    "cur_right": cur_right,
                    "is_anchor": is_anchor_component,
                    "col_constrained": has_col_constraint,
                }
            )

        entries.sort(key=lambda item: item["cur_left"])
        last_right = -2
        for info in entries:
            idx = info["idx"]
            cur_left = info["cur_left"]
            cur_right = info["cur_right"]
            comp_width = info["width"]
            min_c = info["min_c"]
            dr = info["dr"]
            row_origin = info["row_origin"]

            # Keep anchor and constrained components fixed.
            if info["is_anchor"] or info["col_constrained"]:
                last_right = cur_right
                continue

            expected_dr = target - row_origin
            if expected_dr != dr:
                last_right = cur_right
                continue

            if expected_dr <= 0:
                last_right = cur_right
                continue

            # Slide towards the anchor while keeping at least one column gap from the previous component.
            target_left = max(last_right + 2, 0)
            target_left = min(target_left, width - comp_width)

            new_left = target_left if target_left <= cur_left else cur_left
            if new_left < 0:
                new_left = 0
            if new_left > width - comp_width:
                new_left = width - comp_width

            if new_left != cur_left:
                shifts[idx] = (dr, new_left - min_c)
                cur_right = new_left + comp_width - 1
            else:
                cur_right = cur_right

            last_right = cur_right


def apply_transforms(grid, components, shifts, background):
    height, width = len(grid), len(grid[0])
    output = [[background for _ in range(width)] for _ in range(height)]

    for comp, (dr, dc) in zip(components, shifts):
        min_r, max_r, min_c, max_c = comp["bbox"]
        if not (0 <= min_r + dr and max_r + dr < height):
            dr = 0
        if not (0 <= min_c + dc and max_c + dc < width):
            dc = 0
        for r, c in comp["cells"]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < height and 0 <= nc < width:
                output[nr][nc] = grid[r][c]
    return output


def solve_581f7754(grid):
    background = most_common_color(grid)
    components = extract_components(grid, background)
    color_targets, anchor_coords = determine_color_targets(grid, components, background)
    shifts = compute_shifts(components, color_targets)
    refine_row_targets(components, shifts, color_targets, anchor_coords, len(grid[0]))
    return apply_transforms(grid, components, shifts, background)


p = solve_581f7754
