"""Solver for ARC-AGI-2 task 7b5033c1."""

from collections import Counter


def solve_7b5033c1(grid):
    """Collapse non-background colours into a vertical histogram column."""

    if not grid:
        return []

    counts = Counter()
    first_pos = {}
    for y, row in enumerate(grid):
        for x, colour in enumerate(row):
            counts[colour] += 1
            if colour not in first_pos or (y, x) < first_pos[colour]:
                first_pos[colour] = (y, x)

    if not counts:
        return []

    # Background is the most common colour; ties fall back to the smallest code.
    background = max(counts.items(), key=lambda item: (item[1], -item[0]))[0]

    histogram = []
    for top, left, colour, amount in sorted(
        (first_pos[c][0], first_pos[c][1], c, counts[c])
        for c in counts
        if c != background
    ):
        histogram.extend([[colour]] * amount)

    return histogram


p = solve_7b5033c1
