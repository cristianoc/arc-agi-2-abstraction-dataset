"""Solver for ARC-AGI-2 task c7f57c3e (split: evaluation)."""

from functools import lru_cache
from pathlib import Path
import json

WINDOW = 5
RADIUS = WINDOW // 2


def _encode_patch(grid, r, c):
    pattern = []
    height = len(grid)
    width = len(grid[0])
    for dr in range(-RADIUS, RADIUS + 1):
        rr = r + dr
        for dc in range(-RADIUS, RADIUS + 1):
            cc = c + dc
            if 0 <= rr < height and 0 <= cc < width:
                pattern.append(grid[rr][cc])
            else:
                pattern.append(-1)
    return tuple(pattern)


@lru_cache(maxsize=1)
def _training_memory():
    candidates = []
    if "__file__" in globals():
        candidates.append(Path(__file__).with_suffix(".json"))
    candidates.append(Path("arc2_samples/c7f57c3e.json"))
    data = None
    for path in candidates:
        if path.is_file():
            data = json.loads(path.read_text())
            break
    if data is None:
        raise FileNotFoundError("Unable to locate training data for c7f57c3e")
    pattern_to_color = {}
    patterns = []
    colors = []
    for example in data["train"]:
        source = example["input"]
        target = example["output"]
        height = len(source)
        width = len(source[0])
        for r in range(height):
            for c in range(width):
                pattern = _encode_patch(source, r, c)
                color = target[r][c]
                pattern_to_color.setdefault(pattern, color)
                patterns.append(pattern)
                colors.append(color)
    return pattern_to_color, patterns, colors


def _nearest_color(pattern, pattern_to_color, patterns, colors):
    if pattern in pattern_to_color:
        return pattern_to_color[pattern]
    best_color = colors[0]
    best_distance = float("inf")
    for candidate, color in zip(patterns, colors):
        distance = 0
        for a, b in zip(pattern, candidate):
            if a != b:
                distance += 1
                if distance >= best_distance:
                    break
        else:
            # perfect match found
            return color
        if distance < best_distance:
            best_distance = distance
            best_color = color
    return best_color


def solve_c7f57c3e(grid):
    pattern_to_color, patterns, colors = _training_memory()
    height = len(grid)
    width = len(grid[0])
    result = [[0] * width for _ in range(height)]
    for r in range(height):
        for c in range(width):
            pattern = _encode_patch(grid, r, c)
            result[r][c] = _nearest_color(pattern, pattern_to_color, patterns, colors)
    return result


p = solve_c7f57c3e
