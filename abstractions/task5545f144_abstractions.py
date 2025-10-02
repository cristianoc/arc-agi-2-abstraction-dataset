"""Abstraction experiments for ARC-AGI-2 task 5545f144."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Set, Tuple


TASK_PATH = Path(__file__).with_name("arc2_samples") / "5545f144.json"


def load_task() -> Dict[str, List[Dict[str, Sequence[Sequence[int]]]]]:
    return json.loads(TASK_PATH.read_text())


def clone(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    return [list(row) for row in grid]


def analyze(grid: Sequence[Sequence[int]]) -> Dict[str, object]:
    height = len(grid)
    width = len(grid[0])
    background = Counter(val for row in grid for val in row).most_common(1)[0][0]

    separator_cols: List[int] = [
        c
        for c in range(width)
        if len({grid[r][c] for r in range(height)}) == 1 and grid[0][c] != background
    ]

    segments: List[Tuple[int, int]] = []
    start = 0
    for c in range(width + 1):
        if c == width or c in separator_cols:
            if start < c:
                segments.append((start, c))
            start = c + 1
    if not segments:
        segments = [(0, width)]

    segment_width = segments[0][1] - segments[0][0]
    if segment_width <= 0 or any((end - begin) != segment_width for begin, end in segments):
        segment_width = width
        segments = [(0, width)]

    highlight_counts = Counter(
        grid[r][c]
        for r in range(height)
        for c in range(width)
        if c not in set(separator_cols) and grid[r][c] != background
    )
    highlight = highlight_counts.most_common(1)[0][0] if highlight_counts else background

    n_segments = len(segments)
    counts: List[List[int]] = [[0] * segment_width for _ in range(height)]
    segments_with_highlight: List[Set[int]] = [set() for _ in range(height)]
    for seg_idx, (begin, end) in enumerate(segments):
        for r in range(height):
            row = grid[r]
            for offset in range(segment_width):
                c = begin + offset
                if c >= end:
                    break
                if row[c] == highlight:
                    counts[r][offset] += 1
                    segments_with_highlight[r].add(seg_idx)

    positive_cols = [[j for j, val in enumerate(row) if val > 0] for row in counts]
    full_cols = [[j for j, val in enumerate(row) if val == n_segments] for row in counts]
    has_partial = [any(0 < val < n_segments for val in row) for row in counts]

    return {
        "height": height,
        "width": width,
        "segment_width": segment_width,
        "background": background,
        "highlight": highlight,
        "n_segments": n_segments,
        "counts": counts,
        "positive": positive_cols,
        "full": full_cols,
        "partial": has_partial,
        "segments_with_highlight": segments_with_highlight,
    }


def intersection_abstraction(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    data = analyze(grid)
    height = data["height"]
    segment_width = data["segment_width"]
    background = data["background"]
    highlight = data["highlight"]
    full = data["full"]
    partial = data["partial"]

    result = [[background] * segment_width for _ in range(height)]
    for r, cols in enumerate(full):
        if cols and partial[r]:
            for j in cols:
                result[r][j] = highlight
    return result


def first_segment_shift_abstraction(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    data = analyze(grid)
    height = data["height"]
    segment_width = data["segment_width"]
    background = data["background"]
    highlight = data["highlight"]
    positive = data["positive"]
    segs = data["segments_with_highlight"]

    result = [[background] * segment_width for _ in range(height)]
    for r in range(height):
        if segs[r] == {0}:
            pos = positive[r]
            if not pos:
                continue
            shift = min(pos)
            for j in pos:
                nj = j - shift
                if 0 <= nj < segment_width:
                    result[r][nj] = highlight
    return result


def combined_abstraction(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    data = analyze(grid)
    height = data["height"]
    segment_width = data["segment_width"]
    background = data["background"]
    highlight = data["highlight"]
    n_segments = data["n_segments"]
    positive = data["positive"]
    full = data["full"]
    partial = data["partial"]
    segs = data["segments_with_highlight"]
    counts = data["counts"]

    result = [[background] * segment_width for _ in range(height)]
    highlight_cells: Set[Tuple[int, int]] = set()

    if n_segments == 2:
        center_col = None
        for cols in full:
            if cols:
                center_col = cols[0]
                break
        if center_col is None:
            center_col = segment_width // 2
        used_close = False
        for r in range(height):
            pos = positive[r]
            if center_col < segment_width and counts[r][center_col] == n_segments:
                highlight_cells.add((r, center_col))
                continue
            if not pos:
                break
            close = [j for j in pos if abs(j - center_col) <= 2]
            if close:
                mapped = set()
                for j in close:
                    delta = j - center_col
                    if delta > 1:
                        delta = 1
                    elif delta < -1:
                        delta = -1
                    mapped.add(center_col + delta)
                for j in mapped:
                    if 0 <= j < segment_width:
                        highlight_cells.add((r, j))
                used_close = True
            else:
                if used_close:
                    break
                if 0 <= center_col < segment_width:
                    highlight_cells.add((r, center_col))
    else:
        for r, cols in enumerate(full):
            if cols and partial[r]:
                for j in cols:
                    highlight_cells.add((r, j))

        for r in range(height):
            if segs[r] == {0}:
                pos = positive[r]
                if len(pos) >= 2:
                    shift = min(pos)
                    for j in pos:
                        nj = j - shift
                        if 0 <= nj < segment_width:
                            highlight_cells.add((r, nj))

        for r, cols in enumerate(full):
            if not cols or not partial[r]:
                continue
            prev = r - 1
            if prev < 0:
                continue
            if segs[prev] == {0} and len(positive[prev]) == 1:
                length = n_segments - 1
                for j in cols:
                    start = max(0, min(segment_width - length, j - (length - 1) // 2))
                    for offset in range(length):
                        highlight_cells.add((prev, start + offset))

    for r, c in highlight_cells:
        if 0 <= r < height and 0 <= c < segment_width:
            result[r][c] = highlight

    return result


ABSTRACTIONS: Sequence[Tuple[str, Callable[[Sequence[Sequence[int]]], List[List[int]]]]] = (
    ("intersection", intersection_abstraction),
    ("first_segment_shift", first_segment_shift_abstraction),
    ("combined", combined_abstraction),
)


def evaluate_split(records: Iterable[dict], fn: Callable[[Sequence[Sequence[int]]], List[List[int]]]) -> Tuple[int, int, int]:
    total = 0
    matches = 0
    first_failure = -1
    for idx, item in enumerate(records):
        total += 1
        prediction = fn(item["input"])
        if "output" in item:
            if prediction == item["output"]:
                matches += 1
            elif first_failure == -1:
                first_failure = idx
    return total, matches, first_failure


def main() -> None:
    task = load_task()
    train = task.get("train", [])
    test = task.get("test", [])
    print("Loaded 5545f144 samples: train=%d, test=%d" % (len(train), len(test)))
    for name, fn in ABSTRACTIONS:
        total, matches, first_failure = evaluate_split(train, fn)
        status = "PASS" if matches == total else f"{matches}/{total}"
        failure_info = first_failure if first_failure != -1 else "-"
        print(f"[train] {name:>18}: {status} (first miss: {failure_info})")
        if test:
            for item in test:
                _ = fn(item["input"])
            print(f"[test ] {name:>18}: evaluated {len(test)} inputs")


if __name__ == "__main__":
    main()
