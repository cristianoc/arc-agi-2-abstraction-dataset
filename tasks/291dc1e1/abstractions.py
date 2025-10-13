"""Abstractions explored for ARC-AGI-2 task 291dc1e1."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence


BACKGROUND = 8
HEADER_COLORS = {0, 1, 2}
DATA_PATH = Path(__file__).resolve().parent / "arc2_samples" / "291dc1e1.json"
ARCGEN_PATH = DATA_PATH.with_name("291dc1e1_arcgen.json")


def _transpose(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    return [list(col) for col in zip(*grid)]


def _trim_header_column(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    return [list(row[1:]) for row in grid]


def _extract_segments(row: Sequence[int]) -> List[List[int]]:
    segments: List[List[int]] = []
    current: List[int] = []
    for value in row:
        if value == BACKGROUND:
            if current and not all(v in HEADER_COLORS for v in current):
                segments.append(current[:])
            current.clear()
        else:
            current.append(value)
    if current and not all(v in HEADER_COLORS for v in current):
        segments.append(current)
    return segments


def _contiguous_groups(flags: Sequence[bool]) -> List[range]:
    groups: List[range] = []
    start: Optional[int] = None
    for idx, active in enumerate(flags):
        if active:
            if start is None:
                start = idx
        else:
            if start is not None:
                groups.append(range(start, idx))
                start = None
    if start is not None:
        groups.append(range(start, len(flags)))
    return groups


def _inflate(segment: Sequence[int], width: int) -> List[int]:
    remaining = width - len(segment)
    if remaining <= 0:
        return list(segment[:width])
    left = remaining // 2
    right = remaining - left
    return [BACKGROUND] * left + list(segment) + [BACKGROUND] * right


def _segment_pipeline(
    grid: Sequence[Sequence[int]],
    *,
    transpose_input: bool,
    reverse_row_order: bool,
    force_reverse_segments: bool,
    dynamic_reverse: bool,
) -> List[List[int]]:
    oriented = _transpose(grid) if transpose_input else [list(row) for row in grid]
    cores = _trim_header_column(oriented)
    segments_per_row = [_extract_segments(row) for row in cores]
    max_width = max((len(seg) for segs in segments_per_row for seg in segs), default=0)
    if max_width == 0:
        return []

    groups = _contiguous_groups([bool(segs) for segs in segments_per_row])
    result: List[List[int]] = []

    for group in groups:
        row_indices = list(group)
        if reverse_row_order:
            row_indices.reverse()

        if dynamic_reverse:
            reverse_segments = any(cores[idx] and cores[idx][-1] != BACKGROUND for idx in row_indices)
        else:
            reverse_segments = force_reverse_segments

        ordered_lists = [
            list(reversed(segments_per_row[idx])) if reverse_segments else segments_per_row[idx]
            for idx in row_indices
        ]
        if not ordered_lists:
            continue

        max_segments = max(len(lst) for lst in ordered_lists)
        for position in range(max_segments):
            for segs in ordered_lists:
                if position < len(segs):
                    result.append(_inflate(segs[position], max_width))

    return result


def abstraction_row_left_to_right(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    """Row-wise segmentation without directional heuristics."""

    return _segment_pipeline(
        grid,
        transpose_input=False,
        reverse_row_order=False,
        force_reverse_segments=False,
        dynamic_reverse=False,
    )


def abstraction_column_left_to_right(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    """Column-wise segmentation with natural column ordering."""

    return _segment_pipeline(
        grid,
        transpose_input=True,
        reverse_row_order=False,
        force_reverse_segments=False,
        dynamic_reverse=False,
    )


def abstraction_directional(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    """Directional hybrid that mirrors the final solver behaviour."""

    transpose_input = len(grid[0]) <= len(grid)
    return _segment_pipeline(
        grid,
        transpose_input=transpose_input,
        reverse_row_order=transpose_input,
        force_reverse_segments=False,
        dynamic_reverse=True,
    )


ABSTRACTIONS: dict[str, Callable[[Sequence[Sequence[int]]], List[List[int]]]] = {
    "row_ltr": abstraction_row_left_to_right,
    "column_ltr": abstraction_column_left_to_right,
    "directional": abstraction_directional,
}


@dataclass
class EvalResult:
    matches: int
    total: int
    first_fail: Optional[int]


def _evaluate_split(
    samples: Iterable[dict],
    predict: Callable[[Sequence[Sequence[int]]], List[List[int]]],
) -> EvalResult:
    matches = 0
    total = 0
    first_fail: Optional[int] = None
    for idx, sample in enumerate(samples):
        total += 1
        pred = predict(sample["input"])
        if sample.get("output") is None:
            continue
        if pred == sample["output"]:
            matches += 1
        elif first_fail is None:
            first_fail = idx
    return EvalResult(matches, total, first_fail)


def _load_optional(path: Path) -> Optional[dict]:
    if path.exists():
        with path.open() as fh:
            return json.load(fh)
    return None


def main() -> None:
    with DATA_PATH.open() as fh:
        data = json.load(fh)
    arcgen_data = _load_optional(ARCGEN_PATH)

    for name, fn in ABSTRACTIONS.items():
        print(f"{name} abstraction")
        train_res = _evaluate_split(data.get("train", []), fn)
        print(
            f"  train: {train_res.matches}/{train_res.total} solved",
            end="",
        )
        if train_res.first_fail is not None:
            print(f" (first fail at {train_res.first_fail})")
        else:
            print()

        test_samples = data.get("test", [])
        if test_samples:
            pred = fn(test_samples[0]["input"])
            print(
                f"  test: produced {len(pred)}x{len(pred[0]) if pred else 0} grid",
                "(no reference)",
            )

        if arcgen_data:
            arcgen_res = _evaluate_split(arcgen_data.get("samples", []), fn)
            print(
                f"  arc-gen: {arcgen_res.matches}/{arcgen_res.total} solved",
                end="",
            )
            if arcgen_res.first_fail is not None:
                print(f" (first fail at {arcgen_res.first_fail})")
            else:
                print()
        print()


if __name__ == "__main__":
    main()
