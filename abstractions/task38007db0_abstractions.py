"""Abstraction experiments for ARC-AGI-2 task 38007db0."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


Grid = List[List[int]]


def _load_task() -> Dict[str, List[Dict[str, Grid]]]:
    path = Path("analysis/arc2_samples/38007db0.json")
    return json.loads(path.read_text())


def _split_segments(row: Sequence[int]) -> Tuple[int, List[Tuple[int, ...]]]:
    delim = row[0]
    segments: List[Tuple[int, ...]] = []
    current: List[int] = []
    for value in row[1:]:
        if value == delim:
            if current:
                segments.append(tuple(current))
                current = []
        else:
            current.append(value)
    if current:
        segments.append(tuple(current))
    return delim, segments


def _choose_central_segment(segments: Sequence[Tuple[int, ...]]) -> Tuple[int, ...]:
    """Naive abstraction: take the middle repeated block regardless of uniqueness."""
    if not segments:
        return tuple()
    mid_index = (len(segments) - 1) // 2
    return segments[mid_index]


def abstraction_middle_segment(grid: Grid) -> Grid:
    """Keep only the central interior stripe for each row."""

    parsed = [_split_segments(row) for row in grid]
    lengths = [len(seg) for _, segs in parsed for seg in segs]
    segment_length = lengths[0] if lengths else 0
    width = segment_length + 2 if segment_length else len(grid[0])

    result: Grid = []
    for delim, segments in parsed:
        chosen = _choose_central_segment(segments)
        if chosen:
            row = [delim, *chosen, delim]
        else:
            row = [delim] * width
        result.append(row)
    return result


def _choose_unique_segment(segments: Sequence[Tuple[int, ...]]) -> Tuple[int, ...]:
    if not segments:
        return tuple()

    counts = Counter(segments)
    min_count = min(counts.values())
    candidates = [seg for seg, count in counts.items() if count == min_count]
    if len(candidates) == 1:
        return candidates[0]

    mid = (len(segments) - 1) / 2.0
    first_occurrence: Dict[Tuple[int, ...], int] = {}
    for idx, seg in enumerate(segments):
        first_occurrence.setdefault(seg, idx)
    return min(
        candidates,
        key=lambda seg: (abs(first_occurrence[seg] - mid), first_occurrence[seg]),
    )


def abstraction_unique_segment(grid: Grid) -> Grid:
    """Keep the interior stripe that deviates from the repeated pattern."""

    parsed = [_split_segments(row) for row in grid]
    lengths = [len(seg) for _, segs in parsed for seg in segs]
    if lengths:
        segment_length = max(lengths, key=lengths.count)
        width = segment_length + 2
    else:
        segment_length = 0
        width = len(grid[0])

    result: Grid = []
    for delim, segments in parsed:
        chosen = _choose_unique_segment(segments)
        if chosen:
            row = [delim, *chosen, delim]
        else:
            row = [delim] * width
        if len(row) != width:
            if len(row) < width:
                row = row + [delim] * (width - len(row))
            else:
                row = row[:width]
        result.append(row)
    return result


def _non_border_row_segments(grid: Grid, border_color: int) -> List[Tuple[int, int]]:
    segments: List[Tuple[int, int]] = []
    start = None
    for idx, row in enumerate(grid):
        is_border_row = all(value == border_color for value in row)
        if is_border_row:
            if start is not None:
                segments.append((start, idx))
                start = None
            continue
        if start is None:
            start = idx
    if start is not None:
        segments.append((start, len(grid)))
    return segments


def _non_border_col_segments(grid: Grid, border_color: int) -> List[Tuple[int, int]]:
    segments: List[Tuple[int, int]] = []
    start = None
    width = len(grid[0])
    for idx in range(width):
        is_border_col = all(row[idx] == border_color for row in grid)
        if is_border_col:
            if start is not None:
                segments.append((start, idx))
                start = None
            continue
        if start is None:
            start = idx
    if start is not None:
        segments.append((start, width))
    return segments


def abstraction_unique_block_column(grid: Grid) -> Grid:
    """Collapse each block-row to its unique interior block."""

    if not grid or not grid[0]:
        return [row[:] for row in grid]

    border_color = grid[0][0]
    row_segments = _non_border_row_segments(grid, border_color)
    col_segments = _non_border_col_segments(grid, border_color)
    if not row_segments or not col_segments:
        return [row[:] for row in grid]

    width_counts = Counter(end - start for start, end in col_segments)
    block_width = max(width_counts, key=width_counts.get)
    output_width = block_width + 2

    result: Grid = [[border_color] * output_width for _ in grid]

    for row_start, row_end in row_segments:
        blocks: List[Tuple[Tuple[int, ...], ...]] = []
        for col_start, col_end in col_segments:
            block = tuple(
                tuple(grid[r][c] for c in range(col_start, col_end))
                for r in range(row_start, row_end)
            )
            blocks.append(block)

        counts = Counter(blocks)
        min_count = min(counts.values())
        candidates = [idx for idx, block in enumerate(blocks) if counts[block] == min_count]
        if len(candidates) == 1:
            chosen_idx = candidates[0]
        else:
            mid = (len(blocks) - 1) / 2.0
            chosen_idx = min(candidates, key=lambda idx: (abs(idx - mid), idx))
        chosen_block = blocks[chosen_idx]

        for offset, source_row in enumerate(chosen_block):
            target_row = row_start + offset
            row_values = list(source_row)
            if len(row_values) < block_width:
                row_values.extend([border_color] * (block_width - len(row_values)))
            elif len(row_values) > block_width:
                row_values = row_values[:block_width]
            result[target_row][1 : 1 + block_width] = row_values

    return result


ABSTRACTIONS = {
    "middle_segment": abstraction_middle_segment,
    "unique_segment": abstraction_unique_segment,
    "unique_block_column": abstraction_unique_block_column,
}


def _evaluate_abstraction(name: str, fn, samples: Dict[str, List[Dict[str, Grid]]]) -> None:
    print(f"[{name}]")
    for section in ("train", "test", "arc-gen"):
        pairs = samples.get(section, [])
        pairs_with_output = [pair for pair in pairs if "output" in pair]
        total = len(pairs_with_output)
        if total == 0:
            print(f"  {section:<7} : n/a")
            continue

        correct = 0
        first_fail = None
        for idx, pair in enumerate(pairs_with_output):
            pred = fn(pair["input"])
            if pred == pair["output"]:
                correct += 1
            elif first_fail is None:
                first_fail = idx
        status = f"{correct}/{total}"
        fail_str = f", first fail @ {first_fail}" if first_fail is not None else ""
        print(f"  {section:<7} : {status}{fail_str}")


def run_evaluation() -> None:
    samples = _load_task()
    for name, fn in ABSTRACTIONS.items():
        _evaluate_abstraction(name, fn, samples)


if __name__ == "__main__":
    run_evaluation()
