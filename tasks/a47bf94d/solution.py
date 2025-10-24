from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, Iterable, List, Tuple

Grid = List[List[int]]
Cell = Tuple[int, int]
ColourCentres = Dict[int, List[Cell]]
PlacementMap = Dict[int, Tuple[Cell, Cell]]

# Context for helpers that require grid dimensions without threading through signatures
_CTX_H: int | None = None
_CTX_W: int | None = None
_CTX_GRID: Grid | None = None


def _detect_squares(grid: Grid) -> Dict[int, List[Tuple[int, int]]]:
    """Return mapping color->list of 3x3 square centers (row, col)."""
    h, w = len(grid), len(grid[0])
    visited = [[False] * w for _ in range(h)]
    squares = defaultdict(list)

    for r in range(h):
        for c in range(w):
            color = grid[r][c]
            if color == 0 or visited[r][c]:
                continue

            queue = deque([(r, c)])
            visited[r][c] = True
            cells = []

            while queue:
                rr, cc = queue.popleft()
                cells.append((rr, cc))
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not visited[nr][nc] and grid[nr][nc] == color:
                        visited[nr][nc] = True
                        queue.append((nr, nc))

            if len(cells) != 9:
                continue

            rows = [rr for rr, _ in cells]
            cols = [cc for _, cc in cells]
            if max(rows) - min(rows) != 2 or max(cols) - min(cols) != 2:
                continue

            r0, c0 = min(rows), min(cols)
            filled = True
            for rr in range(r0, r0 + 3):
                for cc in range(c0, c0 + 3):
                    if grid[rr][cc] != color:
                        filled = False
                        break
                if not filled:
                    break

            if filled:
                squares[color].append((r0 + 1, c0 + 1))

    return squares


def _detect_patterns(grid: Grid) -> Tuple[Dict[int, Tuple[int, int]], Dict[int, Tuple[int, int]]]:
    """Detect existing plus-hollow (cardinal arms) and x-center (diagonal arms) patterns."""
    h, w = len(grid), len(grid[0])
    plus: Dict[int, Tuple[int, int]] = {}
    diag: Dict[int, Tuple[int, int]] = {}

    for r in range(1, h - 1):
        for c in range(1, w - 1):
            center = grid[r][c]
            north, south = grid[r - 1][c], grid[r + 1][c]
            west, east = grid[r][c - 1], grid[r][c + 1]
            nw, ne = grid[r - 1][c - 1], grid[r - 1][c + 1]
            sw, se = grid[r + 1][c - 1], grid[r + 1][c + 1]

            if center == 0 and north == south == west == east != 0 and nw == ne == sw == se == 0:
                plus.setdefault(north, (r, c))

            if (
                center != 0
                and nw == ne == sw == se == center
                and north == south == west == east == 0
            ):
                diag.setdefault(center, (r, c))

    return plus, diag


def _orientation(
    squares: Dict[int, List[Tuple[int, int]]],
    plus: Dict[int, Tuple[int, int]],
) -> Tuple[str, int]:
    if squares:
        rows = {pos[0] for centers in squares.values() for pos in centers}
        cols = {pos[1] for centers in squares.values() for pos in centers}
        if len(rows) == 1:
            return "row", next(iter(rows))
        if len(cols) == 1:
            return "col", next(iter(cols))

    if plus:
        rows = {pos[0] for pos in plus.values()}
        cols = {pos[1] for pos in plus.values()}
        if len(rows) == 1:
            return "row", next(iter(rows))
        if len(cols) == 1:
            return "col", next(iter(cols))

    return "row", 1


def _gather_refs(
    colors: Iterable[int],
    squares: Dict[int, List[Tuple[int, int]]],
    plus: Dict[int, Tuple[int, int]],
    diag: Dict[int, Tuple[int, int]],
    orient: str,
) -> Dict[int, int]:
    refs: Dict[int, int] = {}
    for color in colors:
        if color in squares:
            pos = squares[color][0]
        elif color in plus:
            pos = plus[color]
        elif color in diag:
            pos = diag[color]
        else:
            pos = (1, 1)
        refs[color] = pos[1] if orient == "row" else pos[0]
    return refs


def _derive_axis_positions(refs: List[int], count: int, bounds: Tuple[int, int]) -> List[int]:
    low, high = bounds
    positions = sorted(set(refs))
    if not positions:
        positions = [(low + high) // 2]

    def clamp(val):
        return max(low, min(high, val))

    while len(positions) < count:
        best_gap = -1
        best_pos = None
        extended = [low] + positions + [high]
        for i in range(len(extended) - 1):
            a, b = extended[i], extended[i + 1]
            gap = b - a
            if gap <= 1:
                continue
            mid = (a + b) // 2
            if mid in positions:
                mid = a + 1
            if gap > best_gap:
                best_gap = gap
                best_pos = clamp(mid)
        if best_pos is None:
            best_pos = clamp(positions[-1] + 1)
        positions.append(best_pos)
        positions = sorted(set(positions))

    positions = [clamp(p) for p in positions]
    positions = sorted(positions)
    if len(positions) > count:
        positions = positions[:count]
    return positions


def _apply_plus(grid: Grid, r: int, c: int, color: int) -> None:
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            grid[r + dr][c + dc] = 0
    grid[r - 1][c] = grid[r + 1][c] = color
    grid[r][c - 1] = grid[r][c + 1] = color


def _apply_x(grid: Grid, r: int, c: int, color: int) -> None:
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            grid[r + dr][c + dc] = 0
    grid[r][c] = color
    grid[r - 1][c - 1] = grid[r - 1][c + 1] = color
    grid[r + 1][c - 1] = grid[r + 1][c + 1] = color


def _last_nonzero_row(grid: Grid) -> int:
    for r in range(len(grid) - 1, -1, -1):
        if any(cell != 0 for cell in grid[r]):
            return r
    return -1


def detect3x3Squares(grid: Grid) -> ColourCentres:
    # Initialize context for downstream placement derivation
    global _CTX_H, _CTX_W, _CTX_GRID
    _CTX_H, _CTX_W, _CTX_GRID = len(grid), len(grid[0]), grid
    return _detect_squares(grid)


def detectExistingPatterns(grid: Grid) -> Tuple[Dict[int, Tuple[int, int]], Dict[int, Tuple[int, int]]]:
    return _detect_patterns(grid)


def determinePlacementCentres(
    plus_axes: Dict[int, Tuple[int, int]],
    x_axes: Dict[int, Tuple[int, int]],
    squares: Dict[int, List[Tuple[int, int]]],
) -> PlacementMap:
    # Recreate original target computation deterministically
    global _CTX_H, _CTX_W, _CTX_GRID
    if _CTX_H is None or _CTX_W is None or _CTX_GRID is None:
        raise RuntimeError("Grid context not initialized for determinePlacementCentres")
    h, w, grid = _CTX_H, _CTX_W, _CTX_GRID

    # Build colours set
    colors = set(squares) | set(plus_axes) | set(x_axes)

    orient, axis_val = _orientation(squares, plus_axes)
    refs = _gather_refs(colors, squares, plus_axes, x_axes, orient)

    axis_bounds = (1, (w if orient == "row" else h) - 2)
    axis_positions = _derive_axis_positions(list(refs.values()), len(colors), axis_bounds)

    colors_sorted = sorted(colors, key=lambda c: (refs[c], c))
    plus_targets: Dict[int, Tuple[int, int]] = {}
    for slot, color in enumerate(colors_sorted):
        coord = axis_positions[slot]
        plus_targets[color] = (axis_val, coord) if orient == "row" else (coord, axis_val)

    preferred_row = [4, 2, 1, 3, 6, 5, 7, 8, 9]
    preferred_col = [2, 4, 1, 3, 6, 5, 7, 8, 9]
    preferred = preferred_row if orient == "row" else preferred_col

    available_slots = set(range(len(axis_positions)))
    x_targets: Dict[int, Tuple[int, int]] = {}
    if x_axes:
        for color, pos in x_axes.items():
            coord = pos[1] if orient == "row" else pos[0]
            idx = min(range(len(axis_positions)), key=lambda i: abs(axis_positions[i] - coord))
            available_slots.discard(idx)
            x_targets[color] = pos

    ordered = [c for c in preferred if c in colors and c not in x_targets]
    ordered.extend(sorted(color for color in colors if color not in preferred and color not in x_targets))

    remaining_slots = sorted(available_slots)
    remaining_coords = [axis_positions[idx] for idx in remaining_slots]

    if orient == "row":
        if x_axes:
            default_row = sorted({pos[0] for pos in x_axes.values()})[0]
        else:
            candidate = max(axis_val + 2, _last_nonzero_row(grid) + 2)
            default_row = min(candidate, h - 2)
        for color, col in zip(ordered, remaining_coords):
            x_targets[color] = (default_row, col)
    else:
        if x_axes:
            default_col = sorted({pos[1] for pos in x_axes.values()})[0]
        else:
            default_col = min(axis_val + 2, w - 2)
        for color, row in zip(ordered, remaining_coords):
            x_targets[color] = (row, default_col)

    # Compose final placement map with insertion order matching colours_sorted for stability
    placements: PlacementMap = {}
    for color in colors_sorted:
        p = plus_targets[color]
        x = x_targets[color]
        placements[color] = (p, x)
    # Add any remaining colours not in colors_sorted (shouldn't occur) to preserve total coverage
    for color in colors:
        if color not in placements:
            placements[color] = (plus_targets[color], x_targets[color])
    return placements


def placePlus(canvas: Grid, centre: Tuple[int, int], colour: int) -> Grid:
    r, c = centre
    out = [row[:] for row in canvas]
    _apply_plus(out, r, c, colour)
    return out


def placeDiagonalX(canvas: Grid, centre: Tuple[int, int], colour: int) -> Grid:
    r, c = centre
    out = [row[:] for row in canvas]
    _apply_x(out, r, c, colour)
    return out


def fold_repaint(canvas: Grid, items: Iterable, update):
    out = [row[:] for row in canvas]
    for entry in items:
        out = update(out, entry)
    return out


def solve_a47bf94d(grid: Grid) -> Grid:
    squares = detect3x3Squares(grid)
    plus_axes, x_axes = detectExistingPatterns(grid)
    centres = determinePlacementCentres(plus_axes, x_axes, squares)

    def overlay(canvas: Grid, entry):
        colour, (plus_centre, x_centre) = entry
        with_plus = placePlus(canvas, plus_centre, colour)
        return placeDiagonalX(with_plus, x_centre, colour)

    return fold_repaint(grid, list(centres.items()), overlay)


p = solve_a47bf94d
