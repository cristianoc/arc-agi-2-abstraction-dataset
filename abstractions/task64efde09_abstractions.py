"""Abstraction experiments for ARC-AGI-2 task 64efde09."""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Sequence, Tuple


BACKGROUND = 8
TASK_PATH = Path(__file__).with_name("arc2_samples") / "64efde09.json"


@dataclass(frozen=True)
class ComponentInfo:
    cells: Sequence[Tuple[int, int]]
    bbox: Tuple[int, int, int, int]


def load_task() -> dict:
    return json.loads(TASK_PATH.read_text())


def find_components(grid: Sequence[Sequence[int]]) -> List[ComponentInfo]:
    height = len(grid)
    width = len(grid[0])
    seen = [[False] * width for _ in range(height)]
    comps: List[ComponentInfo] = []
    for r in range(height):
        for c in range(width):
            if grid[r][c] == BACKGROUND or seen[r][c]:
                continue
            q = deque([(r, c)])
            seen[r][c] = True
            cells: List[Tuple[int, int]] = []
            while q:
                x, y = q.popleft()
                cells.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < height and 0 <= ny < width:
                        if not seen[nx][ny] and grid[nx][ny] != BACKGROUND:
                            seen[nx][ny] = True
                            q.append((nx, ny))
            rows = [r for r, _ in cells]
            cols = [c for _, c in cells]
            bbox = (min(rows), min(cols), max(rows), max(cols))
            comps.append(ComponentInfo(cells, bbox))
    return comps


def vertical_offsets(height: int) -> List[int]:
    if height >= 9:
        return [1, 3, 5]
    if height >= 7:
        return [1, height - 3, height - 2]
    if height >= 5:
        return [1, height - 2, height - 1]
    return [min(1, height - 1)] * 3


def clone(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    return [list(row) for row in grid]


def apply_vertical_shadows(grid: Sequence[Sequence[int]], accent: Sequence[int], components: Sequence[ComponentInfo]) -> List[List[int]]:
    out = clone(grid)
    vertical_indices = [
        idx
        for idx, comp in enumerate(components)
        if (comp.bbox[2] - comp.bbox[0]) > (comp.bbox[3] - comp.bbox[1])
    ]
    vertical_indices.sort(key=lambda idx: (components[idx].bbox[1] + components[idx].bbox[3]) / 2)
    height = len(out)
    width = len(out[0])

    for order, idx in enumerate(vertical_indices):
        top, left, bottom, right = components[idx].bbox
        span = bottom - top + 1
        offsets = [off for off in vertical_offsets(span) if 0 <= off < span]
        palette = accent if span >= 9 else list(reversed(accent))
        extend_left = order % 2 == 0
        for tone, offset in zip(palette, offsets):
            row = top + offset
            if extend_left:
                col = left - 1
                while col >= 0 and out[row][col] == BACKGROUND:
                    out[row][col] = tone
                    col -= 1
            else:
                col = right + 1
                while col < width and out[row][col] == BACKGROUND:
                    out[row][col] = tone
                    col += 1
    return out


def apply_horizontal_shadows(grid: Sequence[Sequence[int]], accent: Sequence[int], components: Sequence[ComponentInfo]) -> List[List[int]]:
    out = clone(grid)
    height = len(out)
    width = len(out[0])
    for comp in components:
        top, left, bottom, right = comp.bbox
        span_rows = bottom - top + 1
        span_cols = right - left + 1
        if span_rows > span_cols:
            continue
        if top <= 2:
            below_top = top - 1
            two_above = top - 2
            target_cols = [right - 5, right - 3, right - 1]
            if below_top >= 0:
                for col, tone in zip(target_cols, sorted(accent, reverse=True)):
                    if 0 <= col < width and out[below_top][col] == BACKGROUND:
                        out[below_top][col] = tone
            if two_above >= 0:
                for col, tone in zip((right - 5, right - 1), (accent[-1], accent[0])):
                    if 0 <= col < width and out[two_above][col] == BACKGROUND:
                        out[two_above][col] = tone
        else:
            columns = sorted({left + 1, left + 2, right - 1})
            for col, tone in zip(columns, accent):
                if not (left <= col <= right):
                    continue
                row = bottom + 1
                while row < height and out[row][col] == BACKGROUND:
                    out[row][col] = tone
                    row += 1
    return out


def identity(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    return clone(grid)


def vertical_only(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    comps = find_components(grid)
    accent = sorted(grid[r][c] for comp in comps if len(comp.cells) == 1 for (r, c) in comp.cells)
    return apply_vertical_shadows(grid, accent, comps)


def full_shadow_pipeline(grid: Sequence[Sequence[int]]) -> List[List[int]]:
    comps = find_components(grid)
    accent = sorted(grid[r][c] for comp in comps if len(comp.cells) == 1 for (r, c) in comp.cells)
    vertical = apply_vertical_shadows(grid, accent, comps)
    return apply_horizontal_shadows(vertical, accent, comps)


ABSTRACTIONS: Sequence[Tuple[str, Callable[[Sequence[Sequence[int]]], List[List[int]]]]] = (
    ("identity", identity),
    ("vertical_only", vertical_only),
    ("full_shadow", full_shadow_pipeline),
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
    print("Loaded 64efde09 samples: train=%d, test=%d" % (len(train), len(test)))
    for name, fn in ABSTRACTIONS:
        total, matches, first_failure = evaluate_split(train, fn)
        status = "PASS" if matches == total else f"{matches}/{total}"
        failure_info = first_failure if first_failure != -1 else "-"
        print(f"[train] {name:>13}: {status} (first miss: {failure_info})")
        if test:
            # We cannot score against hidden outputs; we just ensure the pipeline runs.
            for idx, item in enumerate(test):
                _ = fn(item["input"])
            print(f"[test ] {name:>13}: evaluated {len(test)} inputs")


if __name__ == "__main__":
    main()
