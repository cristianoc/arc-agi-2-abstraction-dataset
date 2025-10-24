"""Solver for ARC-AGI-2 task c4d067a0 (split: evaluation)."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from typing import DefaultDict, Dict, Iterable, List, Sequence, Tuple, cast

Grid = List[List[int]]
Component = Tuple[int, List[Tuple[int, int]]]
ComponentSet = List[Component]


def _connected_components(grid: Grid) -> ComponentSet:
    h = len(grid)
    w = len(grid[0]) if grid else 0
    seen = [[False] * w for _ in range(h)]
    comps: ComponentSet = []
    for r in range(h):
        for c in range(w):
            if seen[r][c]:
                continue
            colour = grid[r][c]
            seen[r][c] = True
            q = deque([(r, c)])
            cells = [(r, c)]
            while q:
                cr, cc = q.popleft()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < h and 0 <= nc < w and not seen[nr][nc] and grid[nr][nc] == colour:
                        seen[nr][nc] = True
                        q.append((nr, nc))
                        cells.append((nr, nc))
            comps.append((colour, cells))
    return comps


def extractComponents(grid: Grid) -> ComponentSet:
    return _connected_components(grid)


def _grid_size_from_components(components: ComponentSet) -> Tuple[int, int]:
    max_r = 0
    max_c = 0
    for _, cells in components:
        for r, c in cells:
            if r > max_r:
                max_r = r
            if c > max_c:
                max_c = c
    return max_r + 1, max_c + 1


def _background_from_components(components: ComponentSet) -> int:
    colour_counts: Dict[int, int] = {}
    for colour, cells in components:
        colour_counts[colour] = colour_counts.get(colour, 0) + len(cells)
    return max(colour_counts.items(), key=lambda kv: kv[1])[0]


def decodeInstructionSequences(grid: Grid, components: ComponentSet) -> Tuple[List[int], List[List[int]]]:
    h = len(grid)
    background = Counter(cell for row in grid for cell in row).most_common(1)[0][0]
    instruction_cols = sorted(
        {cells[0][1] for colour, cells in components if colour != background and len(cells) == 1}
    )
    sequences: List[List[int]] = [
        [grid[r][col] for r in range(h) if grid[r][col] != background]
        for col in instruction_cols
    ]
    return instruction_cols, sequences


def inferColumnGeometry(components: ComponentSet) -> Dict[str, object]:
    # Derive canvas size and background purely from components.
    height, width = _grid_size_from_components(components)
    background = _background_from_components(components)

    # Template components are non-background and larger than one cell.
    template_components: ComponentSet = [
        (colour, cells)
        for colour, cells in components
        if colour != background and len(cells) > 1
    ]
    if not template_components:
        # Fallback minimal geometry
        return {
            "height": height,
            "width": width,
            "mask": [],
            "block_height": 0,
            "spacing": 0,
            "base_col": 0,
            "grouped": defaultdict(list),
            "base_grid": _reconstruct_grid(components, height, width),
        }

    def comp_key(comp: Component) -> Tuple[int, int]:
        _, cells = comp
        return (min(c for _, c in cells), min(r for r, _ in cells))

    template_components.sort(key=comp_key)

    # Establish the block mask from the first template component.
    _, base_cells = template_components[0]
    base_row = min(r for r, _ in base_cells)
    base_col = min(c for _, c in base_cells)
    mask = [(r - base_row, c - base_col) for r, c in base_cells]
    block_height = 1 + max(dr for dr, _ in mask)
    block_width = 1 + max(dc for _, dc in mask)

    # Horizontal spacing learned from existing template columns; fallback to block_width.
    existing_cols = sorted({min(c for _, c in cells) for _, cells in template_components})
    if len(existing_cols) >= 2:
        deltas = [existing_cols[i + 1] - existing_cols[i] for i in range(len(existing_cols) - 1)]
        spacing = Counter(deltas).most_common(1)[0][0]
    else:
        # If only one template column exists, we cannot infer spacing robustly here;
        # default to block_width (the main solver previously also allowed an alt fallback).
        spacing = block_width

    grouped: DefaultDict[int, ComponentSet] = defaultdict(list)
    for colour, cells in template_components:
        col_start = min(c for _, c in cells)
        index = (col_start - base_col) // spacing if spacing else 0
        grouped[index].append((colour, cells))

    return {
        "height": height,
        "width": width,
        "mask": mask,
        "block_height": block_height,
        "spacing": spacing,
        "base_col": base_col,
        "grouped": grouped,
        "base_grid": _reconstruct_grid(components, height, width),
    }


def _reconstruct_grid(components: ComponentSet, height: int, width: int) -> Grid:
    out = [[0] * width for _ in range(height)]
    for colour, cells in components:
        for r, c in cells:
            out[r][c] = colour
    return out


def stackColumns(geometry: Dict[str, object], sequences: List[List[int]]) -> Grid:
    height: int = cast(int, geometry["height"])  # type: ignore[index]
    width: int = cast(int, geometry["width"])  # type: ignore[index]
    mask: List[Tuple[int, int]] = cast(List[Tuple[int, int]], geometry["mask"])  # type: ignore[index]
    block_height: int = cast(int, geometry["block_height"])  # type: ignore[index]
    spacing: int = cast(int, geometry["spacing"])  # type: ignore[index]
    base_col: int = cast(int, geometry["base_col"])  # type: ignore[index]
    grouped: DefaultDict[int, ComponentSet] = cast(DefaultDict[int, ComponentSet], geometry["grouped"])  # type: ignore[index]
    base_grid: Grid = cast(Grid, geometry["base_grid"])  # type: ignore[index]

    column_count = len(sequences)

    # Determine the common bottom row so that all columns align at their final block.
    candidate_last_rows: List[int] = []
    for index, comps in grouped.items():
        if not (0 <= index < column_count):
            continue
        sequence = sequences[index]
        for colour, cells in comps:
            top_row = min(r for r, _ in cells)
            for seq_index, value in enumerate(sequence):
                if value == colour:
                    last_row = top_row + (len(sequence) - 1 - seq_index) * spacing
                    candidate_last_rows.append(last_row)

    def fits(last_row: int) -> bool:
        if not (0 <= last_row <= height - block_height):
            return False
        for sequence in sequences:
            top_row = last_row - (len(sequence) - 1) * spacing
            if top_row < 0:
                return False
        return True

    feasible_last_rows = [row for row in candidate_last_rows if fits(row)]
    if feasible_last_rows:
        last_row = min(feasible_last_rows)
    else:
        last_row = 0
        for row in range(height - block_height, -1, -1):
            if fits(row):
                last_row = row
                break

    # Paint onto a reconstruction of the original grid to preserve other content.
    output = [row[:] for row in base_grid]
    for idx, sequence in enumerate(sequences):
        col_start = base_col + idx * spacing
        top_row = last_row - (len(sequence) - 1) * spacing
        for offset, colour in enumerate(sequence):
            anchor_row = top_row + offset * spacing
            for dr, dc in mask:
                rr = anchor_row + dr
                cc = col_start + dc
                if 0 <= rr < height and 0 <= cc < width:
                    output[rr][cc] = colour
    return output


def solve_c4d067a0(grid: Grid) -> Grid:
    components = extractComponents(grid)
    instruction_columns, sequences = decodeInstructionSequences(grid, components)
    geometry = inferColumnGeometry(components)
    return stackColumns(geometry, sequences)


p = solve_c4d067a0
