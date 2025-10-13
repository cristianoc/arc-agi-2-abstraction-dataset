"""Abstractions explored for ARC task 3dc255db."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

Grid = List[List[int]]


def _deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _nonzero_colors(grid: Grid) -> List[int]:
    return sorted({cell for row in grid for cell in row if cell})


def _bbox(coords: Sequence[Tuple[int, int]]) -> Tuple[int, int, int, int]:
    rows = [r for r, _ in coords]
    cols = [c for _, c in coords]
    return min(rows), max(rows), min(cols), max(cols)


def _components(grid: Grid, color: int) -> List[List[Tuple[int, int]]]:
    height = len(grid)
    width = len(grid[0])
    seen = set()
    comps: List[List[Tuple[int, int]]] = []
    for r in range(height):
        for c in range(width):
            if grid[r][c] != color or (r, c) in seen:
                continue
            queue = deque([(r, c)])
            seen.add((r, c))
            comp: List[Tuple[int, int]] = []
            while queue:
                x, y = queue.popleft()
                comp.append((x, y))
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if (
                        0 <= nx < height
                        and 0 <= ny < width
                        and grid[nx][ny] == color
                        and (nx, ny) not in seen
                    ):
                        seen.add((nx, ny))
                        queue.append((nx, ny))
            comps.append(comp)
    return comps


def _collect_metadata(grid: Grid) -> Tuple[
    List[int],
    Dict[int, List[Tuple[int, int]]],
    Dict[int, Tuple[int, int, int, int]],
    Dict[int, int],
    Dict[int, List[List[Tuple[int, int]]]],
]:
    colors = _nonzero_colors(grid)
    color_cells = {
        color: [(r, c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] == color]
        for color in colors
    }
    bboxes = {color: _bbox(coords) for color, coords in color_cells.items()}
    areas = {color: len(coords) for color, coords in color_cells.items()}
    components = {color: _components(grid, color) for color in colors}
    return colors, color_cells, bboxes, areas, components


def abstraction_identity(grid: Grid) -> Grid:
    """Baseline identity mapping."""
    return _deep_copy(grid)


def abstraction_normalized_axis(grid: Grid) -> Grid:
    """Early attempt that pushes intruders using normalized offsets (fails on train[0])."""

    height = len(grid)
    width = len(grid[0])
    output = _deep_copy(grid)
    colors, _, bboxes, areas, components = _collect_metadata(grid)

    processed = set()
    for host in colors:
        hr0, hr1, hc0, hc1 = bboxes[host]
        host_height = hr1 - hr0 + 1
        host_width = hc1 - hc0 + 1

        for color in colors:
            if color == host or areas[host] <= areas[color]:
                continue

            to_move: List[Tuple[int, int]] = []
            for comp in components[color]:
                key = (color, tuple(sorted(comp)))
                if key in processed:
                    continue
                rows = [r for r, _ in comp]
                cols = [c for _, c in comp]
                cr0, cr1 = min(rows), max(rows)
                cc0, cc1 = min(cols), max(cols)
                if hr0 <= cr0 and cr1 <= hr1 and hc0 <= cc0 and cc1 <= hc1:
                    to_move.extend(comp)
                    processed.add(key)

            if not to_move:
                continue

            for r, c in to_move:
                output[r][c] = 0

            avg_row = sum(r for r, _ in to_move) / len(to_move)
            avg_col = sum(c for _, c in to_move) / len(to_move)
            center_row = (hr0 + hr1) / 2
            center_col = (hc0 + hc1) / 2
            height_span = max(1, host_height)
            width_span = max(1, host_width)
            norm_row = (avg_row - center_row) / height_span
            norm_col = (avg_col - center_col) / width_span

            horizontal = abs(norm_col) >= abs(norm_row)

            if horizontal:
                direction = "east" if norm_col < 0 else "west"
                unique_cols = sorted({c for _, c in to_move})
                row_line = int(round(avg_row))
                row_line = max(hr0, min(hr1, row_line))
                if direction == "east":
                    start_col = hc1 + 1
                    for idx, _ in enumerate(unique_cols):
                        col = start_col + idx
                        if 0 <= col < width:
                            output[row_line][col] = color
                else:
                    start_col = hc0 - len(unique_cols)
                    for idx, _ in enumerate(unique_cols):
                        col = start_col + idx
                        if 0 <= col < width:
                            output[row_line][col] = color
            else:
                direction = "south" if norm_row < 0 else "north"
                unique_rows = sorted({r for r, _ in to_move})
                sorted_cols = sorted(c for _, c in to_move)
                col_line = sorted_cols[len(sorted_cols) // 2]
                col_line = max(hc0, min(hc1, col_line))
                if direction == "north":
                    start_row = hr0 - len(unique_rows)
                    for idx, _ in enumerate(unique_rows):
                        row = start_row + idx
                        if 0 <= row < height:
                            output[row][col_line] = color
                else:
                    start_row = hr1 + 1
                    for idx, _ in enumerate(unique_rows):
                        row = start_row + idx
                        if 0 <= row < height:
                            output[row][col_line] = color

    return output


def abstraction_intruder_edge_push(grid: Grid) -> Grid:
    """Final abstraction: push intruders opposite their dominant offset."""

    height = len(grid)
    width = len(grid[0])
    output = _deep_copy(grid)
    colors, _, bboxes, areas, components = _collect_metadata(grid)

    processed = set()
    for host in colors:
        hr0, hr1, hc0, hc1 = bboxes[host]
        host_height = hr1 - hr0 + 1
        host_width = hc1 - hc0 + 1

        for color in colors:
            if color == host or areas[host] <= areas[color]:
                continue

            to_move: List[Tuple[int, int]] = []
            for comp in components[color]:
                key = (color, tuple(sorted(comp)))
                if key in processed:
                    continue
                rows = [r for r, _ in comp]
                cols = [c for _, c in comp]
                cr0, cr1 = min(rows), max(rows)
                cc0, cc1 = min(cols), max(cols)
                if hr0 <= cr0 and cr1 <= hr1 and hc0 <= cc0 and cc1 <= hc1:
                    to_move.extend(comp)
                    processed.add(key)

            if not to_move:
                continue

            for r, c in to_move:
                output[r][c] = 0

            avg_row = sum(r for r, _ in to_move) / len(to_move)
            avg_col = sum(c for _, c in to_move) / len(to_move)
            center_row = (hr0 + hr1) / 2
            center_col = (hc0 + hc1) / 2
            delta_row = avg_row - center_row
            delta_col = avg_col - center_col
            abs_row = abs(delta_row)
            abs_col = abs(delta_col)

            if abs_col > abs_row:
                axis = "horizontal"
            elif abs_col < abs_row:
                axis = "vertical"
            else:
                axis = "horizontal" if host_width >= host_height else "vertical"

            if axis == "horizontal":
                direction = "east" if delta_col < 0 else "west"
                unique_cols = sorted({c for _, c in to_move})
                row_line = hr1 - 1 if host_height > 1 else hr1
                row_line = max(hr0, min(hr1, row_line))
                if direction == "east":
                    start_col = hc1 + 1
                    for idx, _ in enumerate(unique_cols):
                        col = start_col + idx
                        if 0 <= col < width:
                            output[row_line][col] = color
                else:
                    start_col = hc0 - len(unique_cols)
                    for idx, _ in enumerate(unique_cols):
                        col = start_col + idx
                        if 0 <= col < width:
                            output[row_line][col] = color
            else:
                direction = "north" if delta_row > 0 else "south"
                unique_rows = sorted({r for r, _ in to_move})
                sorted_cols = sorted(c for _, c in to_move)
                col_line = sorted_cols[len(sorted_cols) // 2]
                col_line = max(hc0, min(hc1, col_line))
                if direction == "north":
                    start_row = hr0 - len(unique_rows)
                    for idx, _ in enumerate(unique_rows):
                        row = start_row + idx
                        if 0 <= row < height:
                            output[row][col_line] = color
                else:
                    start_row = hr1 + 1
                    for idx, _ in enumerate(unique_rows):
                        row = start_row + idx
                        if 0 <= row < height:
                            output[row][col_line] = color

    return output


ABSTRACTIONS: Sequence[Tuple[str, Callable[[Grid], Grid]]] = (
    ("identity", abstraction_identity),
    ("normalized_axis", abstraction_normalized_axis),
    ("intruder_edge_push", abstraction_intruder_edge_push),
)


def _format_grid(grid: Grid) -> str:
    return "\n".join("".join(str(cell) for cell in row) for row in grid)


def _evaluate(abstraction: Callable[[Grid], Grid], samples: Sequence[Dict[str, Grid]]) -> Tuple[int, int, Optional[int]]:
    correct = 0
    first_fail: Optional[int] = None
    for idx, pair in enumerate(samples):
        predicted = abstraction(pair["input"])
        if predicted == pair["output"]:
            correct += 1
        elif first_fail is None:
            first_fail = idx
    return correct, len(samples), first_fail


def _load_arcgen() -> Optional[List[Dict[str, Grid]]]:
    base_dir = Path(__file__).parent
    candidates = [
        base_dir / "arc2_samples" / "3dc255db_arcgen.json",
        base_dir / "arc2_arcgen" / "3dc255db.json",
        base_dir / "3dc255db_arcgen.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return json.loads(candidate.read_text())
    return None


def main() -> None:
    base_dir = Path(__file__).parent
    task_path = base_dir / "arc2_samples" / "3dc255db.json"
    task = json.loads(task_path.read_text())
    train_pairs = task.get("train", [])
    test_pairs = task.get("test", [])
    arcgen_pairs = _load_arcgen()

    for name, abstraction in ABSTRACTIONS:
        print(f"=== {name} ===")
        if train_pairs:
            correct, total, first_fail = _evaluate(abstraction, train_pairs)
            fail_str = "None" if first_fail is None else str(first_fail)
            print(f"train: {correct}/{total} correct, first_fail={fail_str}")
        if arcgen_pairs:
            correct, total, first_fail = _evaluate(abstraction, arcgen_pairs)
            fail_str = "None" if first_fail is None else str(first_fail)
            print(f"arc-gen: {correct}/{total} correct, first_fail={fail_str}")
        elif arcgen_pairs is None:
            print("arc-gen: not available")

        if test_pairs:
            print("test predictions:")
            for idx, pair in enumerate(test_pairs):
                predicted = abstraction(pair["input"])
                print(f"test[{idx}]\n{_format_grid(predicted)}")
        print()


if __name__ == "__main__":
    main()
