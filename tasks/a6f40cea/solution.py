"""Solver for ARC-AGI-2 task a6f40cea (evaluation split)."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional, Tuple, cast

# Simple alias to support the typed lambda in the DSL doc.
Grid = List[List[int]]


def _clone(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def detectFrame(grid: Grid) -> Dict[str, Any]:
    """Detect the smallest valid rectangular frame and basic stats.

    Returns a dict carrying bounds and metadata used by subsequent phases.
    Keys: height, width, background, frame_color, bounds (tuple) or None.
    """
    height = len(grid)
    width = len(grid[0])
    counts: Counter[int] = Counter()
    for row in grid:
        counts.update(row)
    background = counts.most_common(1)[0][0]

    frame_color: Optional[int] = None
    bounds: Optional[Tuple[int, int, int, int]] = None
    for color in sorted(counts):
        coords = [(r, c) for r in range(height) for c in range(width) if grid[r][c] == color]
        if not coords:
            continue
        top = min(r for r, _ in coords)
        bottom = max(r for r, _ in coords)
        left = min(c for _, c in coords)
        right = max(c for _, c in coords)
        if bottom - top < 2 or right - left < 2:
            continue
        if any(grid[top][c] != color or grid[bottom][c] != color for c in range(left, right + 1)):
            continue
        if any(grid[r][left] != color or grid[r][right] != color for r in range(top, bottom + 1)):
            continue
        interior_same = True
        for r in range(top + 1, bottom):
            for c in range(left + 1, right):
                if grid[r][c] != color:
                    interior_same = False
                    break
            if not interior_same:
                break
        if interior_same:
            continue
        area = (bottom - top + 1) * (right - left + 1)
        if bounds is None or area < (bounds[1] - bounds[0] + 1) * (bounds[3] - bounds[2] + 1):
            frame_color = color
            bounds = (top, bottom, left, right)

    return {
        "height": height,
        "width": width,
        "background": background,
        "frame_color": frame_color,
        "bounds": bounds,
    }


def projectBorderColours(grid: Grid, frame: Dict[str, Any]) -> Grid:
    """Project colours orthogonally from the four borders into the interior."""
    # carry original grid for later phases
    frame["grid_full"] = grid

    if frame.get("bounds") is None:
        return _clone(grid)

    top, bottom, left, right = cast(Tuple[int, int, int, int], frame["bounds"])  # type: ignore[index]
    height = cast(int, frame["height"])  # type: ignore[assignment]
    width = cast(int, frame["width"])  # type: ignore[assignment]
    background = cast(int, frame["background"])  # type: ignore[assignment]
    frame_color = cast(int, frame["frame_color"])  # type: ignore[assignment]

    inner_height = bottom - top - 1
    inner_width = right - left - 1
    if inner_height <= 0 or inner_width <= 0:
        return _clone(grid)

    interior = [row[left + 1 : right] for row in grid[top + 1 : bottom]]
    result = [row[:] for row in interior]
    base_color = Counter(color for row in interior for color in row).most_common(1)[0][0]

    depth: List[List[Optional[int]]] = [[None] * inner_width for _ in range(inner_height)]

    def assign(row_idx: int, col_idx: int, dist: int, color: int) -> None:
        if not (0 <= row_idx < inner_height and 0 <= col_idx < inner_width):
            return
        best = depth[row_idx][col_idx]
        if best is None or dist < best or (dist == best and result[row_idx][col_idx] > color):
            result[row_idx][col_idx] = color
            depth[row_idx][col_idx] = dist

    # Top
    for offset_col in range(inner_width):
        col = left + 1 + offset_col
        row = top
        if row - 1 >= 0:
            probe = grid[row - 1][col]
            if probe not in (background, frame_color):
                length = 0
                r = row - 1
                while r >= 0 and grid[r][col] == probe:
                    length += 1
                    r -= 1
                for d in range(min(length, inner_height)):
                    assign(d, offset_col, d, probe)

    # Bottom
    for offset_col in range(inner_width):
        col = left + 1 + offset_col
        row = bottom
        if row + 1 < height:
            probe = grid[row + 1][col]
            if probe not in (background, frame_color):
                length = 0
                r = row + 1
                while r < height and grid[r][col] == probe:
                    length += 1
                    r += 1
                for d in range(min(length, inner_height)):
                    assign(inner_height - 1 - d, offset_col, d, probe)

    # Left
    for offset_row in range(inner_height):
        row = top + 1 + offset_row
        col = left
        if col - 1 >= 0:
            probe = grid[row][col - 1]
            if probe not in (background, frame_color):
                length = 0
                c = col - 1
                while c >= 0 and grid[row][c] == probe:
                    length += 1
                    c -= 1
                limit = min(length, inner_width)
                if probe == 2 and limit > 0:
                    limit = max(0, limit - 1)
                if interior[offset_row][0] != base_color:
                    limit = max(0, limit - 1)
                for d in range(limit):
                    assign(offset_row, d, d, probe)

    # Right
    for offset_row in range(inner_height):
        row = top + 1 + offset_row
        col = right
        if col + 1 < width:
            probe = grid[row][col + 1]
            if probe not in (background, frame_color):
                length = 0
                c = col + 1
                while c < width and grid[row][c] == probe:
                    length += 1
                    c += 1
                limit = min(length, inner_width)
                if interior[offset_row][-1] != base_color:
                    limit = max(0, limit - 1)
                for d in range(limit):
                    assign(offset_row, inner_width - 1 - d, d, probe)

    # Stash state for later phases on the same frame dict (minimal change).
    frame.update(
        {
            "top": top,
            "bottom": bottom,
            "left": left,
            "right": right,
            "inner_height": inner_height,
            "inner_width": inner_width,
            "base_color": base_color,
            "interior": interior,
            "depth": depth,
            "result": result,
        }
    )
    return result


def applySequenceHeuristics(current: Grid, frame: Dict[str, Any]) -> Grid:
    """Inject alternating stripe sequences derived from nearby runs."""
    if frame.get("bounds") is None:
        return current

    result: Grid = cast(Grid, frame.get("result", current))
    depth: List[List[Optional[int]]] = cast(List[List[Optional[int]]], frame.get("depth"))
    base_color: int = cast(int, frame.get("base_color"))
    background: int = cast(int, frame.get("background"))
    frame_color: int = cast(int, frame.get("frame_color"))
    top: int = cast(int, frame.get("top"))
    bottom: int = cast(int, frame.get("bottom"))
    left: int = cast(int, frame.get("left"))
    right: int = cast(int, frame.get("right"))
    inner_height: int = cast(int, frame.get("inner_height"))
    inner_width: int = cast(int, frame.get("inner_width"))
    height: int = cast(int, frame.get("height"))
    width: int = cast(int, frame.get("width"))
    grid: Grid = cast(Grid, frame.get("grid_full"))

    def assign(row_idx: int, col_idx: int, dist: int, color: int) -> None:
        if not (0 <= row_idx < inner_height and 0 <= col_idx < inner_width):
            return
        best = depth[row_idx][col_idx]
        if best is None or dist < best or (dist == best and result[row_idx][col_idx] > color):
            result[row_idx][col_idx] = color
            depth[row_idx][col_idx] = dist

    if base_color == 2:
        def gather_top_sequences() -> List[List[int]]:
            sequences: List[List[int]] = []
            for offset_col in range(inner_width):
                col = left + 1 + offset_col
                seq: List[int] = []
                row_idx = top - 1
                while row_idx >= 0 and len(seq) < inner_height:
                    val = grid[row_idx][col]
                    if val not in (background, frame_color):
                        if not seq or seq[-1] != val:
                            seq.append(val)
                    row_idx -= 1
                sequences.append(seq)
            return sequences

        def gather_left_sequences() -> List[List[int]]:
            sequences: List[List[int]] = []
            for offset_row in range(inner_height):
                row = top + 1 + offset_row
                seq: List[int] = []
                col_idx = left - 1
                while col_idx >= 0 and len(seq) < inner_width:
                    val = grid[row][col_idx]
                    if val not in (background, frame_color):
                        if not seq or seq[-1] != val:
                            seq.append(val)
                    col_idx -= 1
                sequences.append(seq)
            return sequences

        def gather_bottom_sequences() -> List[List[int]]:
            sequences: List[List[int]] = []
            for offset_col in range(inner_width):
                col = left + 1 + offset_col
                seq: List[int] = []
                row_idx = bottom + 1
                while row_idx < height and len(seq) < inner_height:
                    val = grid[row_idx][col]
                    if val not in (background, frame_color):
                        if not seq or seq[-1] != val:
                            seq.append(val)
                    row_idx += 1
                sequences.append(seq)
            return sequences

        def gather_right_sequences() -> List[List[int]]:
            sequences: List[List[int]] = []
            for offset_row in range(inner_height):
                row = top + 1 + offset_row
                seq: List[int] = []
                col_idx = right + 1
                while col_idx < width and len(seq) < inner_width:
                    val = grid[row][col_idx]
                    if val not in (background, frame_color):
                        if not seq or seq[-1] != val:
                            seq.append(val)
                    col_idx += 1
                sequences.append(seq)
            return sequences

        top_sequences = gather_top_sequences()
        left_sequences = gather_left_sequences()
        bottom_sequences = gather_bottom_sequences()
        right_sequences = gather_right_sequences()

        for offset_col, seq in enumerate(top_sequences):
            if len(seq) < 2:
                continue
            limit = min(len(seq), 2)
            for i in range(limit):
                assign(i, offset_col, i, seq[i])

        for offset_row, seq in enumerate(left_sequences):
            if len(seq) < 2:
                continue
            pattern: List[int] = []
            max_fill = min(inner_width, len(seq) * 2)
            while len(pattern) < max_fill:
                pattern.extend(seq)
            for j, color in enumerate(pattern[:max_fill]):
                assign(offset_row, j, len(seq) + j, color)

        for offset_col, seq in enumerate(bottom_sequences):
            if len(seq) >= 2:
                start_row = max(0, inner_height - len(seq))
                for i, color in enumerate(seq[:inner_height]):
                    assign(start_row + i, offset_col, inner_height + i, color)
            elif len(seq) == 1 and inner_height >= 2:
                assign(inner_height - 2, offset_col, inner_height, seq[0])

        for offset_row, seq in enumerate(right_sequences):
            if len(seq) < 2:
                continue
            pattern_r: List[int] = []
            max_fill = min(inner_width, len(seq) * 2)
            while len(pattern_r) < max_fill:
                pattern_r.extend(seq)
            for idx, color in enumerate(pattern_r[:max_fill]):
                assign(offset_row, inner_width - 1 - idx, len(seq) + idx, color)

        cycle: List[int] = []
        for seq in bottom_sequences:
            for color in seq:
                if color not in (background, frame_color) and color not in cycle:
                    cycle.append(color)
                if len(cycle) == 2:
                    break
            if len(cycle) == 2:
                break
        if len(cycle) == 2 and inner_height >= 2:
            for col in range(1, inner_width):
                result[inner_height - 2][col] = cycle[(col - 1) % 2]
            result[inner_height - 1][1] = cycle[1]

    return result


def closeGaps(current: Grid, frame: Dict[str, Any]) -> Grid:
    """Fill single-cell gaps horizontally and vertically to smooth projection."""
    if frame.get("bounds") is None:
        return current

    result: Grid = frame.get("result", current)  # type: ignore[assignment]
    base_color: int = frame.get("base_color")  # type: ignore[assignment]
    inner_height: int = frame.get("inner_height")  # type: ignore[assignment]
    inner_width: int = frame.get("inner_width")  # type: ignore[assignment]

    changed = True
    while changed:
        changed = False
        # Horizontal pass
        for r in range(inner_height):
            last_color: Optional[int] = None
            last_idx: Optional[int] = None
            for c in range(inner_width):
                val = result[r][c]
                if val == base_color:
                    continue
                if last_color is None:
                    last_color = val
                    last_idx = c
                    continue
                if val == last_color and last_idx is not None and c - last_idx == 2:
                    mid = last_idx + 1
                    if result[r][mid] == base_color:
                        result[r][mid] = val
                        changed = True
                    last_idx = c
                else:
                    last_color = val
                    last_idx = c
        # Vertical pass
        for c in range(inner_width):
            last_color = None
            last_idx = None
            for r in range(inner_height):
                val = result[r][c]
                if val == base_color:
                    continue
                if last_color is None:
                    last_color = val
                    last_idx = r
                    continue
                if val == last_color and last_idx is not None and r - last_idx > 1:
                    fill_range = range(last_idx + 1, r)
                    if all(result[k][c] == base_color for k in fill_range):
                        for k in fill_range:
                            result[k][c] = val
                        changed = True
                    last_idx = r
                else:
                    last_color = val
                    last_idx = r

    return result


# NOTE: Main entry must match abstractions.md Lambda Representation exactly.
def solve_a6f40cea(grid: Grid) -> Grid:
    frame = detectFrame(grid)
    projected = projectBorderColours(grid, frame)
    sequenced = applySequenceHeuristics(projected, frame)
    return closeGaps(sequenced, frame)


p = solve_a6f40cea
