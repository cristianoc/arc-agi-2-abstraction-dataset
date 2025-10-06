"""Abstractions explored for ARC task de809cff."""

import json
import sys
from pathlib import Path
from typing import Callable, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from analysis.arc2_samples.de809cff import solve_de809cff

DATA_PATH = (Path(__file__).resolve().parent.parent / "analysis" / "arc2_samples" / "de809cff.json")

Grid = List[List[int]]


def _copy_grid(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def _solve_with_options(grid: Grid, *, apply_secondary_rule: bool, apply_pruning: bool) -> Grid:
    colours = sorted({value for row in grid for value in row if value != 0})
    if len(colours) != 2:
        return _copy_grid(grid)

    primary, secondary = colours
    other = {primary: secondary, secondary: primary}
    height = len(grid)
    width = len(grid[0])
    orth = ((1, 0), (-1, 0), (0, 1), (0, -1))

    def in_bounds(r: int, c: int) -> bool:
        return 0 <= r < height and 0 <= c < width

    seeds: List[Tuple[int, int, int]] = []
    for r in range(height):
        for c in range(width):
            if grid[r][c] != 0:
                continue
            neighbours = [
                grid[nr][nc]
                for dr, dc in orth
                if in_bounds(nr := r + dr, nc := c + dc) and grid[nr][nc] != 0
            ]
            if len(neighbours) >= 3 and len(set(neighbours)) == 1:
                seeds.append((r, c, neighbours[0]))

    out = _copy_grid(grid)
    for r, c, _ in seeds:
        out[r][c] = 8

    for r, c, colour in seeds:
        halo_colour = other[colour]
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if not in_bounds(nr, nc) or (nr, nc) == (r, c):
                    continue
                if out[nr][nc] == 8:
                    continue
                original = grid[nr][nc]
                if original == colour or original == 0:
                    out[nr][nc] = halo_colour

    if apply_secondary_rule:
        for r in range(height):
            for c in range(width):
                if grid[r][c] != secondary or out[r][c] != grid[r][c]:
                    continue
                primary_neighbours = sum(
                    1
                    for dr, dc in orth
                    if in_bounds(r + dr, c + dc) and grid[r + dr][c + dc] == primary
                )
                if primary_neighbours >= 3:
                    out[r][c] = primary

    if apply_pruning:
        for r in range(height):
            for c in range(width):
                if grid[r][c] == 0 or out[r][c] != grid[r][c]:
                    continue
                zero_neighbours = sum(
                    1
                    for dr, dc in orth
                    if not in_bounds(r + dr, c + dc) or grid[r + dr][c + dc] == 0
                )
                if zero_neighbours >= 3:
                    out[r][c] = 0

    return out


def identity_abstraction(grid: Grid) -> Grid:
    """Baseline: leave the grid untouched."""
    return _copy_grid(grid)


def seed_halo_abstraction(grid: Grid) -> Grid:
    """Seed-driven halo without clean-up."""
    return _solve_with_options(grid, apply_secondary_rule=False, apply_pruning=False)


def halo_with_pruning_abstraction(grid: Grid) -> Grid:
    """Halo expansion followed by pruning of stranded pixels."""
    return _solve_with_options(grid, apply_secondary_rule=False, apply_pruning=True)


def final_abstraction(grid: Grid) -> Grid:
    """Halo expansion, secondary realignment, and pruning."""
    return _solve_with_options(grid, apply_secondary_rule=True, apply_pruning=True)


def final_solver(grid: Grid) -> Grid:
    """Wrapper so the harness can evaluate the refined solution."""
    return solve_de809cff(grid)


ABSTRACTIONS: Dict[str, Callable[[Grid], Grid]] = {
    "identity": identity_abstraction,
    "seed_halo": seed_halo_abstraction,
    "halo_plus_pruning": halo_with_pruning_abstraction,
    "final_abstraction": final_abstraction,
    "final_solver": final_solver,
}


def _load_dataset():
    with DATA_PATH.open() as fp:
        return json.load(fp)


def _evaluate(abstraction, samples):
    if not samples:
        return None, 0, None
    if "output" not in samples[0]:
        for sample in samples:
            abstraction(sample["input"])
        return None, len(samples), None

    matches = 0
    first_failure = None
    for idx, sample in enumerate(samples):
        prediction = abstraction(sample["input"])
        if prediction == sample["output"]:
            matches += 1
        elif first_failure is None:
            first_failure = idx
    return matches, len(samples), first_failure


def run_harness():
    data = _load_dataset()
    splits = ("train", "test", "arc_gen")
    for name, fn in ABSTRACTIONS.items():
        print(f"=== {name} ===")
        for split in splits:
            samples = data.get(split, [])
            if not samples:
                print(f"  {split}: n/a")
                continue
            matched, total, first_failure = _evaluate(fn, samples)
            if matched is None:
                status = "no ground truth"
            elif first_failure is None:
                status = "all matched"
            else:
                status = f"first failure at {first_failure}"
            prefix = matched if matched is not None else "—"
            denom = total if total is not None else "—"
            print(f"  {split}: {prefix}/{denom} ({status})")
        print()


if __name__ == "__main__":
    run_harness()
