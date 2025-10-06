"""Abstraction experiments for ARC task dfadab01."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from analysis.arc2_samples.dfadab01 import solve_dfadab01

Grid = List[List[int]]

BASE_JSON = Path(__file__).resolve().parent / "arc2_samples" / "dfadab01.json"
ARC_GEN_JSON = Path(__file__).resolve().parent / "arc2_samples" / "dfadab01_arcgen.json"


@dataclass(frozen=True)
class Dataset:
    name: str
    pairs: Sequence[Tuple[Grid, Grid]]


def load_pairs(path: Path, split: str) -> Sequence[Tuple[Grid, Grid]]:
    if not path.exists():
        return ()
    data = json.loads(path.read_text())
    return [(item["input"], item["output"]) for item in data.get(split, [])]


def load_datasets() -> List[Dataset]:
    base = json.loads(BASE_JSON.read_text())
    datasets = [
        Dataset("train", [(item["input"], item["output"]) for item in base.get("train", [])]),
        Dataset("test", [(item["input"], item.get("output")) for item in base.get("test", []) if item.get("output") is not None]),
    ]
    if ARC_GEN_JSON.exists():
        gen = json.loads(ARC_GEN_JSON.read_text())
        datasets.append(
            Dataset("arc-gen", [(item["input"], item["output"]) for item in gen.get("train", [])])
        )
    return datasets


# --- Abstractions -----------------------------------------------------------------


def identity_solver(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def simple_tile_solver(grid: Grid) -> Grid:
    """Early attempt: paint fixed motifs per colour without context awareness."""

    rows = len(grid)
    cols = len(grid[0])
    out = [[0 for _ in range(cols)] for _ in range(rows)]

    tile_2 = [[4, 4, 4, 4], [4, 0, 0, 4], [4, 0, 0, 4], [4, 4, 4, 4]]
    tile_3 = [[0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 1], [0, 1, 1, 0]]
    tile_5 = [[6, 6, 0, 0], [6, 6, 0, 0], [0, 0, 6, 6], [0, 0, 6, 6]]
    tile_8 = [[7, 0, 0, 7], [0, 7, 7, 0], [0, 7, 7, 0], [7, 0, 0, 7]]

    def stamp(tile: Sequence[Sequence[int]], r: int, c: int) -> None:
        for dr, row_vals in enumerate(tile):
            rr = r + dr
            if rr >= rows:
                break
            for dc, val in enumerate(row_vals):
                if val == 0:
                    continue
                cc = c + dc
                if cc >= cols:
                    continue
                out[rr][cc] = val

    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            if val == 2:
                stamp(tile_2, r, c)
            elif val == 3:
                stamp(tile_3, r, c)
            elif val == 5:
                stamp(tile_5, r, c)
            elif val == 8:
                stamp(tile_8, r, c)
    return out


def patch_dictionary_solver(grid: Grid) -> Grid:
    return solve_dfadab01(grid)


# --- Evaluation -------------------------------------------------------------------


@dataclass
class EvalResult:
    matches: int
    total: int
    first_failure: Optional[str]

    def summary(self) -> str:
        percent = 100.0 * self.matches / self.total if self.total else 0.0
        status = f"{self.matches}/{self.total} ({percent:.2f}%)"
        if self.first_failure is None:
            return status
        return f"{status}, first fail = {self.first_failure}"


def evaluate(solver: Callable[[Grid], Grid], dataset: Dataset) -> EvalResult:
    first_failure: Optional[str] = None
    matches = 0
    for idx, (grid_in, grid_out) in enumerate(dataset.pairs):
        pred = solver(grid_in)
        if pred == grid_out:
            matches += 1
        elif first_failure is None:
            first_failure = f"{dataset.name}[{idx}]"
    return EvalResult(matches, len(dataset.pairs), first_failure)


def main() -> None:
    datasets = load_datasets()
    abstractions: Dict[str, Callable[[Grid], Grid]] = {
        "identity": identity_solver,
        "simple_tiles": simple_tile_solver,
        "patch_dictionary": patch_dictionary_solver,
    }

    for name, solver in abstractions.items():
        print(f"=== {name} ===")
        for dataset in datasets:
            if not dataset.pairs:
                print(f"  {dataset.name}: no samples")
                continue
            result = evaluate(solver, dataset)
            print(f"  {dataset.name}: {result.summary()}")
        print()


if __name__ == "__main__":  # pragma: no cover
    main()
