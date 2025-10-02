"""Abstractions explored for ARC-AGI-2 task f931b4a8."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from analysis.arc2_samples import f931b4a8 as solver


Grid = List[List[int]]
TaskCase = Dict[str, Grid]

TASK_PATH = Path("analysis/arc2_samples/f931b4a8.json")


def _load_json(path: Path) -> Dict[str, Sequence[TaskCase]]:
    with path.open() as handle:
        return json.load(handle)


def _load_arcgen_cases(base: Path) -> Sequence[TaskCase]:
    arcgen_path = base.with_name(base.stem + "_arcgen.json")
    if arcgen_path.exists():
        with arcgen_path.open() as handle:
            return json.load(handle)
    return []


def _reshape(tile: Grid, row_ids: Sequence[int], col_ids: Sequence[int], row_patterns: Sequence[Grid]) -> Grid:
    if not row_ids or not col_ids:
        return []
    row_index_lookup: Dict[int, int] = {}
    for idx, row in enumerate(tile):
        row_id = next((i for i, pat in enumerate(row_patterns) if pat == row), None)
        if row_id is not None and row_id not in row_index_lookup:
            row_index_lookup[row_id] = idx
    result: Grid = []
    for row_id in row_ids:
        src_idx = row_index_lookup.get(row_id, 0)
        tile_row = tile[src_idx]
        result.append([tile_row[col_idx] for col_idx in col_ids])
    return result


def abstraction_cycle(grid: Grid) -> Grid:
    """Cycle row and column patterns regardless of structure."""

    tile, _, _ = solver._compute_tile(grid)
    if not tile or not tile[0]:
        return []
    hh = len(tile)
    hw = len(tile[0])
    tl = [row[:hw] for row in grid[:hh]]
    tr = [row[hw:] for row in grid[:hh]]
    row_patterns, _ = solver._ensure_unique_patterns(tile)
    row_coords = solver._nonzero_positions_col_major(tl)
    col_coords = solver._nonzero_positions_row_major(tr)
    if not row_coords or not col_coords:
        return []
    row_ids = [idx % len(row_patterns) for idx, _ in enumerate(row_coords)]
    col_ids = [idx % hw for idx, _ in enumerate(col_coords)]
    return _reshape(tile, row_ids, col_ids, row_patterns)


def _row_ids_without_fallback(grid: Grid) -> Tuple[List[int], List[Grid]]:
    tile, _, br = solver._compute_tile(grid)
    hh = len(tile)
    if hh == 0:
        return [], []
    hw = len(tile[0])
    tl = [row[:hw] for row in grid[:hh]]
    row_patterns, row_to_id = solver._ensure_unique_patterns(tile)
    variant_orders = solver._build_variant_orders(tile, br)
    zero_groups = solver._collect_group_meta(br)
    coords = solver._nonzero_positions_col_major(tl)
    if not coords:
        return [], row_patterns

    full_sig = tuple(range(hw))
    borrow_default = solver._borrow_pool(variant_orders, full_sig)
    min_index_per_group = {sig: min(rows) for sig, rows in zero_groups.items()}

    row_ids: List[int] = []
    for r, c in coords:
        zero_sig = solver._zero_signature(br[r])
        order = variant_orders.get(zero_sig, [])
        if not order:
            variant_row = r
        elif zero_sig == full_sig:
            base_variant = order[0]
            if c % 2 == 0:
                variant_row = base_variant
            else:
                borrows = borrow_default or [base_variant]
                offset = (r - min_index_per_group.get(zero_sig, r)) % len(borrows)
                variant_row = borrows[offset]
        else:
            variant_row = order[c % len(order)]
        row_ids.append(row_to_id[tuple(tile[variant_row])])
    return row_ids, row_patterns


def abstraction_seqcols_origrow(grid: Grid) -> Grid:
    """Use original row heuristic with sequential columns (fails on train[4])."""

    row_ids, row_patterns = _row_ids_without_fallback(grid)
    if not row_ids:
        return []
    tile, _, _ = solver._compute_tile(grid)
    hh = len(tile)
    hw = len(tile[0]) if tile else 0
    tr = [row[hw:] for row in grid[:hh]]
    col_coords = solver._nonzero_positions_row_major(tr)
    if not col_coords:
        return []
    col_ids = [idx % hw for idx, _ in enumerate(col_coords)]
    return _reshape(tile, row_ids, col_ids, row_patterns)


def abstraction_final(grid: Grid) -> Grid:
    """Final solver shipped in analysis.arc2_samples.f931b4a8."""

    return solver.solve_f931b4a8(grid)


def _evaluate(abstractions: Iterable[Tuple[str, Callable[[Grid], Grid]]]) -> None:
    data = _load_json(TASK_PATH)
    arcgen_cases = _load_arcgen_cases(TASK_PATH)
    splits: List[Tuple[str, Sequence[TaskCase]]] = [
        ("train", data.get("train", [])),
        ("test", data.get("test", [])),
        ("arc-gen", arcgen_cases),
    ]

    for name, fn in abstractions:
        print(f"=== {name} ===")
        for split_name, cases in splits:
            if not cases:
                print(f"  {split_name}: no cases")
                continue
            matches = 0
            first_fail = None
            for idx, case in enumerate(cases):
                pred = fn(case["input"])
                expected = case.get("output")
                if expected is None:
                    continue
                if pred == expected:
                    matches += 1
                elif first_fail is None:
                    first_fail = idx
            total = sum(1 for case in cases if "output" in case)
            if total == 0:
                print(f"  {split_name}: no labeled cases")
            else:
                status = f"{matches}/{total} match"
                fail_note = "none" if first_fail is None else str(first_fail)
                print(f"  {split_name}: {status}; first fail: {fail_note}")
        print()


def main() -> None:
    abstractions = [
        ("cycle", abstraction_cycle),
        ("seqcols_origrow", abstraction_seqcols_origrow),
        ("final", abstraction_final),
    ]
    _evaluate(abstractions)


if __name__ == "__main__":
    main()
