"""Abstraction experiments for ARC task 7b5033c1."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import json


DATA_PATH = Path(__file__).resolve().with_name('arc2_samples') / '7b5033c1.json'


@dataclass
class ObjectStats:
    color: int
    count: int
    top: int
    left: int


def analyse_grid(grid):
    counts = Counter()
    top_left = {}
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            counts[color] += 1
            if color not in top_left or (y, x) < top_left[color]:
                top_left[color] = (y, x)
    if not counts:
        return [], None
    background, _ = max(counts.items(), key=lambda item: (item[1], -item[0]))
    objects = [
        ObjectStats(color=c, count=counts[c], top=top_left[c][0], left=top_left[c][1])
        for c in counts
        if c != background
    ]
    return objects, background


def render_sequence(order):
    output = []
    for obj in order:
        output.extend([[obj.color] for _ in range(obj.count)])
    return output


def abstraction_area_sorted(grid):
    objects, _ = analyse_grid(grid)
    ordered = sorted(objects, key=lambda obj: (-obj.count, obj.top, obj.left, obj.color))
    return render_sequence(ordered)


def abstraction_top_row(grid):
    objects, _ = analyse_grid(grid)
    ordered = sorted(objects, key=lambda obj: (obj.top, obj.left, obj.color))
    return render_sequence(ordered)


def abstraction_final(grid):
    return abstraction_top_row(grid)


ABSTRACTIONS = {
    'area_sorted': abstraction_area_sorted,
    'top_row': abstraction_top_row,
    'final': abstraction_final,
}


def evaluate_abstraction(name, fn, data):
    per_split = {}
    first_fail = None
    unknown_previews = {}
    for split, cases in data.items():
        correct = 0
        unknown = 0
        for idx, ex in enumerate(cases):
            predicted = fn(ex['input'])
            expected = ex.get('output')
            if expected is None:
                unknown += 1
                unknown_previews.setdefault(split, (idx, predicted))
                continue
            if predicted == expected:
                correct += 1
            elif first_fail is None:
                first_fail = (split, idx)
        per_split[split] = (correct, len(cases), unknown)

    overall_pass = all(
        correct == total - unknown for correct, total, unknown in per_split.values()
    )
    sections = []
    for split, (correct, total, unknown) in per_split.items():
        if unknown:
            sections.append(f"{split}:{correct}/{total - unknown}?{unknown}")
        else:
            sections.append(f"{split}:{correct}/{total}")
    status = 'PASS' if overall_pass else 'FAIL'
    joined = ' '.join(sections)
    if first_fail is None:
        print(f"{name:10s} {status} [{joined}]")
    else:
        print(f"{name:10s} {status} [{joined}] first_fail={first_fail}")

    return unknown_previews


def main():
    data = json.loads(DATA_PATH.read_text())
    for name, fn in ABSTRACTIONS.items():
        unknown = evaluate_abstraction(name, fn, data)
        if unknown and name == 'final':
            for split, (idx, predicted) in unknown.items():
                print(f"  {split} sample[{idx}] predicted output:")
                for row in predicted:
                    print('   ', row)


if __name__ == '__main__':
    main()
