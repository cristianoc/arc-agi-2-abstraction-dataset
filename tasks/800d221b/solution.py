"""Solver for ARC-AGI-2 task 800d221b (evaluation split).

The task features a dominant background colour and a secondary colour that
acts as a "transition" palette between two other colours.  On the training
examples, the transition colour forms one or more connected components that
sit between a "left" colour and a "right" colour.  The goal is to recolour
the transition pixels so that regions nearer the left colour adopt it, regions
nearer the right colour adopt that colour, while deeply interior pixels remain
unchanged.  The notion of "nearness" is learned from the training pairs by a
simple feature-based kNN classifier operating on normalised geometric
features.

The training pairs from `800d221b.json` are embedded directly below so that
the solver remains self contained even when imported via `exec`.  They are
used to build a tiny dataset of labelled examples which, in turn, powers a
lightweight kNN classifier reused at inference time.
"""

from __future__ import annotations

from collections import Counter, deque
from functools import lru_cache
from typing import Dict, Iterable, List, Sequence, Tuple

Grid = List[List[int]]
Coord = Tuple[int, int]
Component = List[Coord]
Label = str
Feature = Tuple[float, float, float, float, float, float]


TRAINING_DATA = {'train': [{'input': [[3, 4, 3, 4, 8, 9, 9, 9, 9, 9, 9, 8, 4, 4, 4, 4], [4, 3, 4, 3, 8, 9, 9, 9, 9, 9, 9, 8, 4, 4, 3, 4], [3, 3, 3, 4, 8, 8, 8, 9, 9, 9, 9, 8, 3, 3, 4, 4], [3, 4, 3, 3, 8, 9, 8, 9, 9, 9, 9, 8, 8, 8, 8, 8], [8, 8, 8, 8, 8, 9, 8, 9, 9, 9, 9, 9, 8, 9, 9, 9], [9, 8, 9, 9, 9, 9, 8, 9, 9, 9, 9, 9, 8, 9, 9, 9], [9, 8, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9], [9, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9], [9, 9, 9, 9, 9, 9, 8, 9, 9, 9, 9, 9, 9, 9, 8, 9], [9, 9, 9, 9, 9, 9, 8, 9, 9, 9, 9, 9, 9, 9, 8, 9], [9, 9, 9, 9, 9, 9, 8, 9, 9, 9, 9, 9, 9, 9, 8, 9], [9, 9, 9, 9, 9, 9, 8, 9, 9, 9, 9, 9, 9, 9, 8, 9], [9, 9, 9, 9, 9, 8, 8, 8, 8, 9, 9, 9, 9, 8, 8, 8], [9, 9, 9, 9, 9, 8, 4, 4, 8, 9, 9, 9, 9, 8, 3, 4], [9, 9, 9, 9, 9, 8, 4, 3, 8, 9, 9, 9, 9, 8, 4, 4]], 'output': [[3, 4, 3, 4, 3, 9, 9, 9, 9, 9, 9, 4, 4, 4, 4, 4], [4, 3, 4, 3, 3, 9, 9, 9, 9, 9, 9, 4, 4, 4, 3, 4], [3, 3, 3, 4, 3, 3, 3, 9, 9, 9, 9, 4, 3, 3, 4, 4], [3, 4, 3, 3, 3, 9, 3, 9, 9, 9, 9, 4, 4, 4, 4, 4], [3, 3, 3, 3, 3, 9, 3, 9, 9, 9, 9, 9, 4, 9, 9, 9], [9, 3, 9, 9, 9, 9, 3, 9, 9, 9, 9, 9, 4, 9, 9, 9], [9, 3, 9, 9, 9, 8, 8, 8, 4, 4, 4, 4, 4, 9, 9, 9], [9, 3, 3, 3, 3, 8, 4, 8, 9, 9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9, 9, 8, 8, 8, 4, 4, 4, 4, 4, 4, 4, 9], [9, 9, 9, 9, 9, 9, 4, 9, 9, 9, 9, 9, 9, 9, 4, 9], [9, 9, 9, 9, 9, 9, 4, 9, 9, 9, 9, 9, 9, 9, 4, 9], [9, 9, 9, 9, 9, 9, 4, 9, 9, 9, 9, 9, 9, 9, 4, 9], [9, 9, 9, 9, 9, 9, 4, 9, 9, 9, 9, 9, 9, 9, 4, 9], [9, 9, 9, 9, 9, 4, 4, 4, 4, 9, 9, 9, 9, 4, 4, 4], [9, 9, 9, 9, 9, 4, 4, 4, 4, 9, 9, 9, 9, 4, 3, 4], [9, 9, 9, 9, 9, 4, 4, 3, 4, 9, 9, 9, 9, 4, 4, 4]]}, {'input': [[0, 0, 0, 0, 0, 0, 0, 5, 2, 2], [0, 0, 0, 0, 5, 5, 5, 5, 2, 1], [0, 0, 0, 0, 5, 0, 0, 5, 5, 5], [0, 0, 0, 5, 5, 5, 0, 0, 0, 0], [0, 5, 5, 5, 5, 5, 5, 5, 5, 0], [0, 5, 0, 5, 5, 5, 0, 0, 5, 0], [0, 5, 0, 0, 0, 0, 0, 0, 5, 0], [5, 5, 5, 5, 0, 0, 0, 5, 5, 5], [2, 1, 1, 5, 0, 0, 0, 5, 2, 2], [1, 2, 1, 5, 0, 0, 0, 5, 1, 2]], 'output': [[0, 0, 0, 0, 0, 0, 0, 2, 2, 2], [0, 0, 0, 0, 2, 2, 2, 2, 2, 1], [0, 0, 0, 0, 2, 0, 0, 2, 2, 2], [0, 0, 0, 5, 5, 5, 0, 0, 0, 0], [0, 1, 1, 5, 2, 5, 2, 2, 2, 0], [0, 1, 0, 5, 5, 5, 0, 0, 2, 0], [0, 1, 0, 0, 0, 0, 0, 0, 2, 0], [1, 1, 1, 1, 0, 0, 0, 2, 2, 2], [2, 1, 1, 1, 0, 0, 0, 2, 2, 2], [1, 2, 1, 1, 0, 0, 0, 2, 1, 2]]}, {'input': [[6, 6, 6, 6, 6, 7, 8, 8, 8, 8, 7, 5, 6, 5, 7, 8, 8, 8, 8, 8], [6, 6, 5, 6, 6, 7, 8, 8, 8, 8, 7, 6, 5, 5, 7, 8, 8, 8, 8, 8], [5, 6, 6, 6, 6, 7, 7, 7, 8, 8, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8], [6, 6, 6, 6, 6, 7, 8, 7, 8, 8, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8], [6, 6, 6, 6, 6, 7, 8, 7, 7, 8, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8], [7, 7, 7, 7, 7, 7, 8, 8, 7, 8, 7, 7, 8, 8, 8, 8, 8, 7, 7, 7], [8, 8, 8, 7, 8, 8, 8, 8, 7, 8, 7, 8, 8, 8, 8, 8, 8, 7, 5, 6], [8, 8, 8, 7, 8, 8, 8, 8, 7, 8, 7, 8, 8, 7, 7, 7, 7, 7, 5, 5], [8, 8, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 7, 5, 6], [8, 8, 8, 8, 8, 8, 8, 8, 7, 7, 7, 8, 8, 8, 8, 8, 8, 7, 6, 5], [8, 8, 8, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 7, 7, 7], [8, 8, 8, 7, 8, 8, 8, 8, 7, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8], [8, 8, 8, 7, 8, 8, 8, 8, 7, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8], [7, 7, 7, 7, 7, 7, 7, 8, 7, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8], [6, 5, 6, 6, 6, 6, 7, 7, 7, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8], [6, 6, 6, 6, 6, 6, 7, 8, 8, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8], [6, 6, 6, 6, 6, 6, 7, 8, 8, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8], [6, 6, 6, 6, 6, 5, 7, 8, 8, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8], [6, 5, 6, 6, 5, 6, 7, 8, 8, 7, 6, 5, 5, 6, 5, 7, 8, 8, 8, 8], [6, 6, 6, 6, 6, 6, 7, 8, 8, 7, 6, 5, 5, 6, 5, 7, 8, 8, 8, 8]], 'output': [[6, 6, 6, 6, 6, 6, 8, 8, 8, 8, 5, 5, 6, 5, 5, 8, 8, 8, 8, 8], [6, 6, 5, 6, 6, 6, 8, 8, 8, 8, 5, 6, 5, 5, 5, 8, 8, 8, 8, 8], [5, 6, 6, 6, 6, 6, 6, 6, 8, 8, 5, 5, 5, 5, 5, 8, 8, 8, 8, 8], [6, 6, 6, 6, 6, 6, 8, 6, 8, 8, 8, 5, 8, 8, 8, 8, 8, 8, 8, 8], [6, 6, 6, 6, 6, 6, 8, 6, 6, 8, 8, 5, 8, 8, 8, 8, 8, 8, 8, 8], [6, 6, 6, 6, 6, 6, 8, 8, 6, 8, 5, 5, 8, 8, 8, 8, 8, 5, 5, 5], [8, 8, 8, 6, 8, 8, 8, 8, 6, 8, 5, 8, 8, 8, 8, 8, 8, 5, 5, 6], [8, 8, 8, 6, 8, 8, 8, 8, 6, 8, 5, 8, 8, 5, 5, 5, 5, 5, 5, 5], [8, 8, 8, 6, 6, 6, 6, 6, 7, 7, 7, 5, 5, 5, 8, 8, 8, 5, 5, 6], [8, 8, 8, 8, 8, 8, 8, 8, 7, 6, 7, 8, 8, 8, 8, 8, 8, 5, 6, 5], [8, 8, 8, 6, 6, 6, 6, 6, 7, 7, 7, 8, 8, 8, 8, 8, 8, 5, 5, 5], [8, 8, 8, 6, 8, 8, 8, 8, 6, 8, 5, 8, 8, 8, 8, 8, 8, 8, 8, 8], [8, 8, 8, 6, 8, 8, 8, 8, 6, 8, 5, 8, 8, 8, 8, 8, 8, 8, 8, 8], [6, 6, 6, 6, 6, 6, 6, 8, 6, 8, 5, 8, 8, 8, 8, 8, 8, 8, 8, 8], [6, 5, 6, 6, 6, 6, 6, 6, 6, 8, 5, 8, 8, 8, 8, 8, 8, 8, 8, 8], [6, 6, 6, 6, 6, 6, 6, 8, 8, 8, 5, 8, 8, 8, 8, 8, 8, 8, 8, 8], [6, 6, 6, 6, 6, 6, 6, 8, 8, 8, 5, 8, 8, 8, 8, 8, 8, 8, 8, 8], [6, 6, 6, 6, 6, 5, 6, 8, 8, 5, 5, 5, 5, 5, 5, 5, 8, 8, 8, 8], [6, 5, 6, 6, 5, 6, 6, 8, 8, 5, 6, 5, 5, 6, 5, 5, 8, 8, 8, 8], [6, 6, 6, 6, 6, 6, 6, 8, 8, 5, 6, 5, 5, 6, 5, 5, 8, 8, 8, 8]]}], 'test': [{'input': [[3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], [3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], [3, 3, 3, 3, 2, 3, 3, 3, 3, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], [3, 3, 2, 2, 3, 3, 3, 3, 3, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 4, 4, 4], [2, 2, 3, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 3, 2], [2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 6, 6, 6, 6, 4, 6, 6, 6, 6, 6, 6, 6, 4, 4, 4, 4, 4, 2, 3, 2], [3, 3, 3, 3, 3, 3, 2, 3, 3, 4, 6, 6, 6, 6, 4, 6, 6, 6, 6, 6, 6, 6, 4, 6, 6, 6, 4, 4, 4, 4], [2, 2, 3, 3, 3, 3, 3, 2, 3, 4, 4, 4, 4, 6, 4, 6, 6, 6, 6, 6, 6, 6, 4, 6, 6, 6, 6, 6, 6, 6], [3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 6, 6, 4, 6, 4, 6, 6, 6, 6, 6, 6, 4, 4, 6, 6, 6, 6, 6, 6, 6], [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 6, 6, 4, 6, 4, 6, 6, 6, 6, 6, 6, 4, 6, 6, 6, 6, 6, 6, 6, 6], [6, 6, 6, 6, 6, 4, 6, 6, 6, 6, 6, 6, 4, 6, 4, 6, 6, 6, 6, 6, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6], [6, 6, 6, 6, 6, 4, 6, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6], [6, 6, 6, 6, 6, 4, 4, 4, 6, 6, 6, 6, 4, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], [6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], [6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 6, 6, 4, 6, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], [6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 6, 6, 4, 6, 4, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], [6, 6, 6, 6, 6, 6, 4, 4, 4, 4, 6, 6, 4, 6, 6, 6, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], [6, 6, 6, 6, 6, 6, 4, 6, 6, 6, 6, 6, 4, 6, 6, 6, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], [6, 6, 6, 6, 6, 6, 4, 6, 6, 6, 6, 6, 4, 6, 6, 6, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], [6, 6, 6, 6, 6, 6, 4, 6, 6, 6, 6, 6, 4, 6, 6, 6, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], [6, 6, 6, 6, 6, 6, 4, 6, 6, 6, 6, 6, 4, 6, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4], [4, 4, 4, 6, 6, 6, 4, 6, 6, 6, 6, 6, 4, 6, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [3, 3, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 4, 4, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [3, 2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 2, 2, 3, 2], [3, 2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 2, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 3, 3, 2], [4, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2], [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2, 2, 2, 3, 2], [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]}]}


def _load_training_samples() -> List[Tuple[Feature, str]]:
    payload = TRAINING_DATA
    samples: List[Tuple[Feature, str]] = []
    for example in payload["train"]:
        samples.extend(_extract_labelled_samples(example["input"], example["output"]))
    return samples


@lru_cache(maxsize=1)
def _training_samples() -> List[Tuple[Feature, str]]:
    return _load_training_samples()


def _extract_labelled_samples(inp: Grid, out: Grid) -> List[Tuple[Feature, str]]:
    target = _find_target_colour(inp, out)
    samples: List[Tuple[Feature, str]] = []
    for component in _components(inp, target):
        samples.extend(_extract_component_samples(component, inp, out, target))
    return samples


def _find_target_colour(inp: Grid, out: Grid) -> int:
    diff_colours = {inp[r][c] for r in range(len(inp)) for c in range(len(inp[0])) if inp[r][c] != out[r][c]}
    if len(diff_colours) != 1:
        raise ValueError("Expected exactly one mutable colour in training data")
    return diff_colours.pop()


def _components(grid: Grid, colour: int) -> List[List[Coord]]:
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]
    comps: List[List[Coord]] = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != colour or seen[r][c]:
                continue
            queue = deque([(r, c)])
            seen[r][c] = True
            comp: List[Coord] = []
            while queue:
                cr, cc = queue.popleft()
                comp.append((cr, cc))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < rows and 0 <= nc < cols and not seen[nr][nc] and grid[nr][nc] == colour:
                        seen[nr][nc] = True
                        queue.append((nr, nc))
            comps.append(comp)
    return comps


def _extract_component_samples(
    comp: Sequence[Coord],
    inp: Grid,
    out: Grid,
    target: int,
) -> List[Tuple[Feature, str]]:
    comp_set = set(comp)
    rows, cols = len(inp), len(inp[0])
    r_vals = [r for r, _ in comp]
    c_vals = [c for _, c in comp]
    r_min, r_max = min(r_vals), max(r_vals)
    c_min, c_max = min(c_vals), max(c_vals)
    width = max(1, c_max - c_min)
    height = max(1, r_max - r_min)

    colour_counts = Counter(out[r][c] for r, c in comp if out[r][c] != target)
    if not colour_counts:
        return []
    sorted_colours = sorted(colour_counts, key=lambda col: _average_column(comp, out, target, col))
    left_colour = sorted_colours[0]
    right_colour = sorted_colours[-1]

    left_seeds = {cell for cell in comp if _touches_colour(inp, cell, left_colour)}
    right_seeds = {cell for cell in comp if _touches_colour(inp, cell, right_colour)}

    dist_left = _distance_map(comp_set, left_seeds)
    dist_right = _distance_map(comp_set, right_seeds)

    samples: List[Tuple[Feature, str]] = []
    for r, c in comp:
        col_norm = (c - c_min) / width
        row_norm = (r - r_min) / height
        d_left = dist_left.get((r, c), float("inf")) / width
        d_right = dist_right.get((r, c), float("inf")) / width
        min_dist = min(d_left, d_right)
        diff = d_left - d_right
        feature = (col_norm, row_norm, d_left, d_right, min_dist, diff)
        label = "mid"
        cell_out = out[r][c]
        if cell_out == left_colour:
            label = "left"
        elif cell_out == right_colour:
            label = "right"
        samples.append((feature, label))
    return samples


def _average_column(comp: Sequence[Coord], out: Grid, target: int, colour: int) -> float:
    cols = [c for r, c in comp if out[r][c] == colour]
    return sum(cols) / len(cols) if cols else float("inf")


def _touches_colour(grid: Grid, cell: Coord, colour: int) -> bool:
    r, c = cell
    rows, cols = len(grid), len(grid[0])
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == colour:
            return True
    return False


def _distance_map(comp: set[Coord], seeds: set[Coord]) -> Dict[Coord, int]:
    if not seeds:
        return {}
    dist: Dict[Coord, int] = {cell: 0 for cell in seeds}
    queue = deque(seeds)
    while queue:
        r, c = queue.popleft()
        base = dist[(r, c)] + 1
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            nxt = (nr, nc)
            if nxt in comp and nxt not in dist:
                dist[nxt] = base
                queue.append(nxt)
    return dist


def _dominant_colour(grid: Grid) -> int:
    return Counter(val for row in grid for val in row).most_common(1)[0][0]


def _guess_target_colour(grid: Grid) -> int:
    counts = Counter(val for row in grid for val in row)
    bg = counts.most_common(1)[0][0]
    for colour, _ in counts.most_common():
        if colour != bg:
            return colour
    return bg


def _knn_predict(feature: Feature, k: int = 3) -> str:
    dataset = _training_samples()
    distances: List[Tuple[float, str]] = []
    for sample_feat, label in dataset:
        dist = sum((feature[i] - sample_feat[i]) ** 2 for i in range(len(feature)))
        distances.append((dist, label))
    distances.sort(key=lambda x: x[0])
    votes: Dict[str, float] = {}
    for dist, label in distances[:k]:
        votes[label] = votes.get(label, 0.0) + 1.0 / (dist + 1e-9)
    return max(votes.items(), key=lambda kv: kv[1])[0]


_GRID_FOR_FEATURES: Grid | None = None


def extractTargetComponents(grid: Grid) -> Tuple[int, int, List[Component]]:
    global _GRID_FOR_FEATURES
    _GRID_FOR_FEATURES = grid
    transition = _guess_target_colour(grid)
    background = _dominant_colour(grid)
    components = _components(grid, transition)
    return transition, background, components


def identifyFringeColours(grid: Grid, components: List[Component]) -> Tuple[int, int]:
    target = _guess_target_colour(grid)
    bg_colour = _dominant_colour(grid)
    rows, cols = len(grid), len(grid[0])
    adjacency: Counter[int] = Counter()
    for comp in components:
        for r, c in comp:
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    val = grid[nr][nc]
                    if val not in (target, bg_colour):
                        adjacency[val] += 1
    if not adjacency:
        return target, target
    fringe = sorted(adjacency, key=lambda col: _average_column_adjacency(grid, components, target, col))
    return fringe[0], fringe[-1]


def _component_bounds(component: Component) -> Tuple[int, int, int, int]:
    r_vals = [r for r, _ in component]
    c_vals = [c for _, c in component]
    return min(r_vals), max(r_vals), min(c_vals), max(c_vals)


def computeFeatures(component: Component, anchors: Tuple[int, int]) -> List[Feature]:
    grid = _GRID_FOR_FEATURES
    assert grid is not None
    left_colour, right_colour = anchors
    r_min, r_max, c_min, c_max = _component_bounds(component)
    width = max(1, c_max - c_min)
    height = max(1, r_max - r_min)
    comp_set = set(component)
    left_seeds = {cell for cell in component if _touches_colour(grid, cell, left_colour)}
    right_seeds = {cell for cell in component if _touches_colour(grid, cell, right_colour)}
    dist_left = _distance_map(comp_set, left_seeds) if left_seeds else {}
    dist_right = _distance_map(comp_set, right_seeds) if right_seeds else {}
    feats: List[Feature] = []
    for r, c in component:
        col_norm = (c - c_min) / width
        row_norm = (r - r_min) / height
        d_left = dist_left.get((r, c), float("inf")) / width
        d_right = dist_right.get((r, c), float("inf")) / width
        min_dist = min(d_left, d_right)
        diff = d_left - d_right
        feats.append((col_norm, row_norm, d_left, d_right, min_dist, diff))
    return feats


def classifyCells(features: List[Feature]) -> List[Label]:
    labels: List[Label] = []
    for col_norm, row_norm, d_left, d_right, min_dist, diff in features:
        if col_norm <= 0.12:
            labels.append("left")
        elif col_norm >= 0.88:
            labels.append("right")
        elif 0.32 <= col_norm <= 0.62 and min_dist >= 3.5:
            labels.append("mid")
        else:
            labels.append(_knn_predict((col_norm, row_norm, d_left, d_right, min_dist, diff), k=3))
    return labels


def repaintByLabels(canvas: Grid, component: Component, labels: List[Label], colours: Tuple[int, int, int]) -> Grid:
    left_colour, right_colour, transition = colours
    out = [row[:] for row in canvas]
    for (r, c), label in zip(component, labels):
        if label == "left":
            out[r][c] = left_colour
        elif label == "right":
            out[r][c] = right_colour
        else:
            out[r][c] = transition
    return out


def fold_repaint(canvas: Grid, items: List[Component], update) -> Grid:
    out = [row[:] for row in canvas]
    for item in items:
        out = update(out, item)
    return out


def solve_800d221b(grid: Grid) -> Grid:
    transition, background, components = extractTargetComponents(grid)
    left_colour, right_colour = identifyFringeColours(grid, components)

    def repaint(canvas: Grid, component: Component) -> Grid:
        features = computeFeatures(component, (left_colour, right_colour))
        labels = classifyCells(features)
        return repaintByLabels(canvas, component, labels, (left_colour, right_colour, transition))

    return fold_repaint(grid, components, repaint)


def _average_column_adjacency(grid: Grid, components: Sequence[Sequence[Coord]], target: int, colour: int) -> float:
    positions: List[int] = []
    for comp in components:
        for r, c in comp:
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == colour:
                    positions.append(c)
                    break
    return sum(positions) / len(positions) if positions else float("inf")


p = solve_800d221b
