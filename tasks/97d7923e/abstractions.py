"""Abstraction experiments for ARC task 97d7923e."""

from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Sequence, Tuple

Grid = List[List[int]]


@dataclass
class Sample:
    """Container for a single ARC sample."""

    input: Grid
    output: Grid | None


def _load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def _load_split(path: Path) -> dict:
    return _load_json(path) if path.exists() else {"train": [], "test": []}


def _load_samples() -> dict[str, Sequence[Sample]]:
    base_dir = Path(__file__).resolve().parent / "arc2_samples"
    main_path = base_dir / "97d7923e.json"
    aux_path = base_dir / "97d7923e_arcgen.json"

    primary = _load_split(main_path)
    arcgen = _load_split(aux_path)

    def to_samples(entries: Iterable[dict]) -> List[Sample]:
        samples: List[Sample] = []
        for entry in entries:
            samples.append(
                Sample(input=entry["input"], output=entry.get("output"))
            )
        return samples

    data = {
        "train": to_samples(primary.get("train", [])),
        "test": to_samples(primary.get("test", [])),
        "arcgen": to_samples(arcgen.get("arcgen", [])),
    }
    return data


def _deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def identity_baseline(grid: Grid) -> Grid:
    """Return the input unchanged."""

    return _deep_copy(grid)


def naive_column_cap_fill(grid: Grid) -> Grid:
    """Always fill sandwiched segments regardless of context."""

    height = len(grid)
    width = len(grid[0])
    result = _deep_copy(grid)

    for c in range(width):
        runs: List[Tuple[int, int, int]] = []
        current = grid[0][c]
        length = 1
        start = 0
        for r in range(1, height):
            value = grid[r][c]
            if value == current:
                length += 1
            else:
                runs.append((current, length, start))
                start += length
                current = value
                length = 1
        runs.append((current, length, start))

        for i in range(len(runs) - 2):
            top_color, _, top_start = runs[i]
            mid_color, mid_len, mid_start = runs[i + 1]
            bottom_color, _, _ = runs[i + 2]
            if top_color != 0 and mid_color != 0 and top_color == bottom_color:
                for row in range(mid_start, mid_start + mid_len):
                    result[row][c] = top_color

    return result


def _load_solver() -> Callable[[Grid], Grid]:
    solver_path = Path(__file__).resolve().parent / "arc2_samples" / "97d7923e.py"
    spec = importlib.util.spec_from_file_location("solver_97d7923e", solver_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module.solve_97d7923e  # type: ignore[attr-defined]


def selective_cap_fill(grid: Grid) -> Grid:
    """Wrapper around the tuned solver used for the final submission."""

    return _load_solver()(grid)


ABSTRACTIONS: Sequence[Tuple[str, Callable[[Grid], Grid]]] = (
    ("identity", identity_baseline),
    ("naive_column_fill", naive_column_cap_fill),
    ("selective_cap_fill", selective_cap_fill),
)


def _compare(a: Grid, b: Grid) -> bool:
    return a == b


def _evaluate_split(
    name: str, samples: Sequence[Sample], solver: Callable[[Grid], Grid]
) -> Tuple[int, int | None]:
    if not samples or samples[0].output is None:
        return len(samples), None

    matched = 0
    first_failure: int | None = None
    for idx, sample in enumerate(samples):
        prediction = solver(sample.input)
        if _compare(prediction, sample.output):
            matched += 1
        elif first_failure is None:
            first_failure = idx
    return matched, first_failure


def run_evaluations() -> None:
    data = _load_samples()

    for name, fn in ABSTRACTIONS:
        print(f"=== {name} ===")
        for split_name, samples in data.items():
            total = len(samples)
            matched, first_failure = _evaluate_split(split_name, samples, fn)
            if first_failure is None and total and samples[0].output is not None:
                summary = f"match {matched}/{total}"
            elif samples and samples[0].output is not None:
                summary = f"match {matched}/{total}, first_fail={first_failure}"
            else:
                summary = "no ground-truth outputs"
            print(f"  {split_name}: {summary}")
        print()


if __name__ == "__main__":
    run_evaluations()
