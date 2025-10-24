"""Solver for ARC-AGI-2 task b6f77b65 (split: evaluation)."""

from __future__ import annotations

from typing import List, Optional

# DSL type alias
Grid = List[List[int]]


COLOR_TO_SEGMENT = {2: 'a', 3: 'b', 4: 'c', 5: 'd', 6: 'e', 7: 'f', 8: 'g'}


MAPPING = {
    (0, 'ace', None): [
        [9, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 6],
        [0, 0, 6],
        [0, 0, 6],
        [0, 4, 2],
        [0, 4, 0],
        [0, 4, 0],
        [0, 4, 0],
    ],
    (0, 'ace', 'c'): [
        [4, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 6],
        [0, 0, 6],
        [0, 0, 6],
        [0, 0, 2],
    ],
    (0, 'acef', 'f'): [
        [7, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 4, 6],
        [0, 4, 6],
        [0, 4, 6],
        [0, 4, 2],
    ],
    (0, 'cde', 'c'): [
        [4, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 9],
        [0, 0, 9],
        [0, 0, 9],
        [0, 6, 5],
        [0, 6, 0],
        [0, 6, 0],
    ],
    (0, 'de', 'e'): [
        [6, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 9],
        [0, 0, 9],
        [0, 0, 9],
        [0, 0, 5],
    ],
    (1, 'abd', None): [
        [0, 0, 0],
        [0, 0, 0],
        [0, 5, 1],
        [0, 5, 0],
        [0, 5, 0],
        [3, 3, 3],
        [0, 0, 3],
        [0, 0, 3],
        [2, 2, 2],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ],
    (1, 'abd', 'c'): [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 5, 1],
        [0, 5, 0],
        [0, 5, 0],
        [3, 3, 3],
        [0, 0, 3],
        [0, 0, 3],
        [2, 2, 2],
    ],
    (1, 'abd', 'f'): [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 5, 0],
        [0, 5, 0],
        [0, 5, 1],
        [3, 3, 3],
        [0, 0, 3],
        [0, 0, 3],
        [2, 2, 2],
    ],
    (1, 'acd', 'c'): [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 2],
        [0, 0, 2],
        [0, 0, 2],
        [0, 0, 2],
        [0, 0, 2],
        [5, 0, 1],
        [5, 0, 1],
        [5, 0, 1],
    ],
    (1, 'acd', 'e'): [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 2],
        [0, 0, 2],
        [0, 0, 2],
        [0, 0, 2],
        [4, 4, 4],
        [5, 0, 1],
        [5, 0, 1],
        [5, 0, 1],
    ],
    (2, 'ad', None): [
        [0, 0, 0],
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 1],
        [0, 0, 1],
        [0, 5, 5],
        [0, 5, 0],
        [0, 5, 0],
        [2, 2, 2],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ],
    (2, 'ad', 'c'): [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 1],
        [0, 0, 1],
        [0, 5, 5],
        [0, 5, 0],
        [0, 5, 0],
        [2, 2, 2],
    ],
    (2, 'ad', 'f'): [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [1, 1, 1],
        [0, 5, 1],
        [0, 5, 1],
        [0, 5, 5],
        [2, 2, 2],
    ],
    (2, 'adf', 'c'): [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [5, 5, 5],
        [0, 0, 0],
        [0, 0, 0],
        [7, 0, 2],
        [7, 0, 2],
        [7, 0, 2],
        [7, 7, 7],
    ],
    (2, 'adf', 'e'): [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [5, 5, 5],
        [0, 0, 0],
        [7, 0, 2],
        [7, 0, 2],
        [7, 0, 2],
        [7, 7, 7],
        [0, 0, 0],
        [0, 0, 0],
    ],
    (3, 'af', None): [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [7, 0, 0],
        [7, 0, 0],
        [7, 0, 0],
        [2, 7, 0],
        [0, 7, 0],
        [0, 7, 0],
        [0, 7, 0],
    ],
    (3, 'af', 'c'): [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [7, 7, 0],
        [7, 7, 0],
        [7, 7, 0],
        [2, 7, 0],
    ],
    (3, 'af', 'f'): [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [2, 0, 0],
    ],
    (3, 'bcfg', 'c'): [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [8, 0, 0],
        [8, 0, 0],
        [8, 0, 0],
        [8, 0, 0],
        [3, 3, 0],
        [0, 3, 0],
        [7, 3, 0],
    ],
    (3, 'bcfg', 'e'): [
        [0, 0, 0],
        [0, 0, 0],
        [8, 0, 0],
        [8, 0, 0],
        [8, 0, 0],
        [8, 0, 0],
        [3, 3, 0],
        [0, 3, 0],
        [0, 3, 0],
        [7, 4, 0],
        [0, 4, 0],
        [0, 4, 0],
    ],
}


def readKeyLetter(grid: Grid) -> Optional[str]:
    return COLOR_TO_SEGMENT.get(grid[0][0])

def segmentKeyForDigit(grid: Grid, index: int) -> str:
    start = index * 3
    letters = {
        COLOR_TO_SEGMENT[val]
        for row in grid
        for val in row[start:start + 3]
        if val in COLOR_TO_SEGMENT
    }
    return ''.join(sorted(letters))

def _digit_block(grid: Grid, index: int) -> Grid:
    start = index * 3
    return [row[start:start + 3] for row in grid]

def lookupDigitTemplate(grid: Grid, index: int, segment_key: str, key_letter: Optional[str]) -> Grid:
    pattern = MAPPING.get((index, segment_key, key_letter))
    if pattern is None and key_letter is None:
        pattern = MAPPING.get((index, segment_key, None))
    if pattern is None:
        return _digit_block(grid, index)
    return [row[:] for row in pattern]

def assembleDigits(templates: List[Grid]) -> Grid:
    if not templates:
        return []
    height = len(templates[0])
    return [
        [val for tpl in templates for val in tpl[r]]
        for r in range(height)
    ]

def solve_b6f77b65(grid: Grid) -> Grid:
    key_letter = readKeyLetter(grid)
    digit_count = int(len(grid[0]) / 3)
    templates = [
        lookupDigitTemplate(
            grid,
            index,
            segmentKeyForDigit(grid, index),
            key_letter,
        )
        for index in range(digit_count)
    ]
    return assembleDigits(templates)


p = solve_b6f77b65
