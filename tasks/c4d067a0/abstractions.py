"""Abstraction experiments for ARC task c4d067a0."""

from __future__ import annotations

import importlib.util
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

Grid = List[List[int]]
Component = Tuple[int, List[Tuple[int, int]]]

ARC_SAMPLE_DIR = Path(__file__).with_name("arc2_samples")
DATA_PATH = ARC_SAMPLE_DIR / "c4d067a0.json"


def load_solver() -> Callable[[Grid], Grid]:
    solver_path = ARC_SAMPLE_DIR / "c4d067a0.py"
    spec = importlib.util.spec_from_file_location("task_c4d067a0_solver", solver_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module.solve_c4d067a0  # type: ignore[attr-defined]


def load_dataset() -> Dict[str, List[Dict[str, Grid]]]:
    with DATA_PATH.open() as fh:
        return json.load(fh)


def connected_components(grid: Grid) -> List[Component]:
    height = len(grid)
    width = len(grid[0]) if grid else 0
    visited = [[False] * width for _ in range(height)]
    comps: List[Component] = []
    for r in range(height):
        for c in range(width):
            if visited[r][c]:
                continue
            colour = grid[r][c]
            visited[r][c] = True
            queue = deque([(r, c)])
            cells = [(r, c)]
            while queue:
                cr, cc = queue.popleft()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[nr][nc] == colour:
                        visited[nr][nc] = True
                        queue.append((nr, nc))
                        cells.append((nr, nc))
            comps.append((colour, cells))
    return comps


def extract_structure(grid: Grid) -> Optional[Dict[str, object]]:
    height = len(grid)
    if height == 0:
        return None
    width = len(grid[0])
    background = Counter(cell for row in grid for cell in row).most_common(1)[0][0]
    comps = connected_components(grid)

    instruction_cols = sorted(
        {cells[0][1] for colour, cells in comps if colour != background and len(cells) == 1}
    )
    if not instruction_cols:
        return None

    sequences = [
        [grid[r][col] for r in range(height) if grid[r][col] != background]
        for col in instruction_cols
    ]

    template_components = [
        (colour, cells)
        for colour, cells in comps
        if colour != background and len(cells) > 1
    ]
    if not template_components:
        return None

    def comp_key(comp: Component) -> Tuple[int, int]:
        colour, cells = comp
        return (min(c for _, c in cells), min(r for r, _ in cells))

    template_components.sort(key=comp_key)

    # Establish the block mask from the first template component.
    _, base_cells = template_components[0]
    base_row = min(r for r, _ in base_cells)
    base_col = min(c for _, c in base_cells)
    mask = [(r - base_row, c - base_col) for r, c in base_cells]
    block_height = 1 + max(dr for dr, _ in mask)
    block_width = 1 + max(dc for _, dc in mask)

    existing_cols = sorted({min(c for _, c in cells) for _, cells in template_components})
    if len(existing_cols) >= 2:
        deltas = [existing_cols[i + 1] - existing_cols[i] for i in range(len(existing_cols) - 1)]
        spacing = Counter(deltas).most_common(1)[0][0]
    else:
        spacing = (
            abs(instruction_cols[1] - instruction_cols[0])
            if len(instruction_cols) >= 2
            else block_width
        )

    column_positions = [base_col + i * spacing for i in range(len(sequences))]

    grouped_components: Dict[int, List[Component]] = defaultdict(list)
    for colour, cells in template_components:
        col_start = min(c for _, c in cells)
        index = (col_start - base_col) // spacing if spacing else 0
        grouped_components[index].append((colour, cells))

    return {
        "height": height,
        "width": width,
        "mask": mask,
        "block_height": block_height,
        "spacing": spacing,
        "sequences": sequences,
        "column_positions": column_positions,
        "components_by_column": grouped_components,
    }


def paint_columns(grid: Grid, structure: Dict[str, object], top_rows: Sequence[int]) -> Grid:
    height = structure["height"]  # type: ignore[index]
    width = structure["width"]  # type: ignore[index]
    mask = structure["mask"]  # type: ignore[index]
    spacing = structure["spacing"]  # type: ignore[index]
    sequences = structure["sequences"]  # type: ignore[index]
    column_positions = structure["column_positions"]  # type: ignore[index]

    output = [row[:] for row in grid]
    for idx, sequence in enumerate(sequences):
        col = column_positions[idx]
        top = top_rows[idx]
        for offset, colour in enumerate(sequence):
            anchor = top + offset * spacing
            for dr, dc in mask:
                rr = anchor + dr
                cc = col + dc
                if 0 <= rr < height and 0 <= cc < width:
                    output[rr][cc] = colour
    return output


def abstraction_identity(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def abstraction_global_stack(grid: Grid) -> Grid:
    structure = extract_structure(grid)
    if structure is None:
        return [row[:] for row in grid]

    sequences: List[List[int]] = structure["sequences"]  # type: ignore[assignment]
    spacing: int = structure["spacing"]  # type: ignore[assignment]
    block_height: int = structure["block_height"]  # type: ignore[assignment]
    height: int = structure["height"]  # type: ignore[assignment]
    components_by_column: Dict[int, List[Component]] = structure["components_by_column"]  # type: ignore[assignment]

    candidates: List[int] = []
    for idx, comps in components_by_column.items():
        if not (0 <= idx < len(sequences)):
            continue
        sequence = sequences[idx]
        for colour, cells in comps:
            top = min(r for r, _ in cells)
            matches = [j for j, value in enumerate(sequence) if value == colour]
            candidates.extend(top - j * spacing for j in matches)

    if candidates:
        valid = [s for s in candidates if 0 <= s <= height - block_height]
        start_row = min(valid) if valid else min(candidates)
    else:
        start_row = 0

    for sequence in sequences:
        limit = height - block_height - (len(sequence) - 1) * spacing
        start_row = min(start_row, limit)

    top_rows = [start_row] * len(sequences)
    return paint_columns(grid, structure, top_rows)


def abstraction_column_aligned(grid: Grid) -> Grid:
    return SOLVER(grid)


SOLVER = load_solver()


ABSTRACTIONS: List[Tuple[str, Callable[[Grid], Grid]]] = [
    ("identity", abstraction_identity),
    ("global_stack", abstraction_global_stack),
    ("column_aligned", abstraction_column_aligned),
]


def evaluate_abstraction(name: str, fn: Callable[[Grid], Grid], cases: List[Dict[str, Grid]]) -> Tuple[int, Optional[int]]:
    matches = 0
    first_fail: Optional[int] = None
    for idx, case in enumerate(cases):
        prediction = fn(case["input"])
        if "output" not in case:
            continue
        if prediction == case["output"]:
            matches += 1
        elif first_fail is None:
            first_fail = idx
    return matches, first_fail


def main() -> None:
    data = load_dataset()
    for split_name, cases in data.items():
        has_outputs = cases and "output" in cases[0]
        total = len(cases)
        print(f"\nSplit: {split_name} (cases={total}, scored={has_outputs})")
        for name, fn in ABSTRACTIONS:
            matches, first_fail = evaluate_abstraction(name, fn, cases)
            if has_outputs:
                status = f"{matches}/{total}"
                detail = "all matched" if matches == total else f"first_fail={first_fail}"
            else:
                # For evaluation-only cases we simply show the prediction size.
                sample = fn(cases[0]["input"]) if cases else []
                status = f"prediction size {len(sample)}x{len(sample[0]) if sample else 0}"
                detail = "no ground truth"
            print(f"  {name:<15} -> {status:<18} {detail}")


if __name__ == "__main__":
    main()
