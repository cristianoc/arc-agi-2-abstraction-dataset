"""Abstraction experiments for ARC task 89565ca0."""

from collections import Counter, defaultdict, deque
import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "arc2_samples" / "89565ca0.json"


Grid = List[List[int]]
Abstraction = Callable[[Grid], Grid]


def _load_cases() -> Dict[str, Sequence[dict]]:
    with DATA_PATH.open() as fh:
        raw = json.load(fh)
    return {
        "train": raw.get("train", []),
        "test": raw.get("test", []),
        "arc_gen": raw.get("generated", raw.get("arc_gen", [])),
    }


def _color_cells(grid: Grid) -> Dict[int, List[Tuple[int, int]]]:
    color_cells: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val != 0:
                color_cells[val].append((r, c))
    return color_cells


def _component_count(grid: Grid, color: int) -> int:
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    comps = 0
    for r in range(h):
        for c in range(w):
            if grid[r][c] == color and not seen[r][c]:
                comps += 1
                dq = deque([(r, c)])
                seen[r][c] = True
                while dq:
                    cr, cc = dq.pop()
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = cr + dr, cc + dc
                        if (
                            0 <= nr < h
                            and 0 <= nc < w
                            and grid[nr][nc] == color
                            and not seen[nr][nc]
                        ):
                            seen[nr][nc] = True
                            dq.append((nr, nc))
    return comps


def _stripe_ranges(length: int, parts: int) -> Iterable[Tuple[int, int]]:
    base = length // parts
    extra = length % parts
    start = 0
    for idx in range(parts):
        end = start + base + (1 if idx < extra else 0)
        yield start, end
        start = end


def _shared_profile_data(grid: Grid):
    h, w = len(grid), len(grid[0])
    color_cells = _color_cells(grid)
    if not color_cells:
        return None

    components = {color: _component_count(grid, color) for color in color_cells}
    filler = max(components, key=lambda col: components[col])

    stripe_dominators: List[Optional[int]] = []
    for start, end in _stripe_ranges(h, 4):
        if start == end:
            stripe_dominators.append(None)
            continue
        counts = Counter()
        for r in range(start, end):
            for c in range(w):
                val = grid[r][c]
                if val != 0:
                    counts[val] += 1
        if not counts:
            stripe_dominators.append(None)
            continue
        winner = None
        winner_count = -1
        for color, count in counts.items():
            if (
                winner is None
                or count > winner_count
                or (count == winner_count and color == filler and winner != filler)
            ):
                winner = color
                winner_count = count
        stripe_dominators.append(winner)

    bottommost = {color: None for color in color_cells}
    for idx, dom_color in enumerate(stripe_dominators):
        if dom_color is None:
            continue
        prev = bottommost.get(dom_color)
        if prev is None or idx > prev:
            bottommost[dom_color] = idx

    areas = {color: len(cells) for color, cells in color_cells.items()}
    non_filler = [color for color in color_cells if color != filler]
    return {
        "filler": filler,
        "areas": areas,
        "non_filler": non_filler,
        "bottom": bottommost,
    }


def _profile_to_rows(
    grid: Grid,
    mapper,
    *,
    refined: bool,
) -> Grid:
    data = _shared_profile_data(grid)
    if data is None:
        return []

    filler = data["filler"]
    areas = data["areas"]
    non_filler = data["non_filler"]
    bottom = data["bottom"]

    prefix_lengths: Dict[int, int] = {}
    if refined:
        no_dom = sorted(
            (color for color in non_filler if bottom[color] is None),
            key=lambda col: (areas[col], col),
        )
        for rank, color in enumerate(no_dom):
            prefix_lengths[color] = 1 if rank == 0 else 2
    else:
        for color in non_filler:
            if bottom[color] is None:
                prefix_lengths[color] = 1

    for color in non_filler:
        length = mapper(bottom[color])
        if length is not None:
            prefix_lengths[color] = length

    rows: Grid = []
    for color in sorted(non_filler, key=lambda col: (prefix_lengths.get(col, 1), col)):
        length = max(1, min(4, prefix_lengths.get(color, 1)))
        rows.append([color] * length + [filler] * (4 - length))
    return rows


def abstraction_naive_stripe(grid: Grid) -> Grid:
    """First attempt: map stripe index directly to prefix length."""

    def mapper(dom_idx: Optional[int]) -> Optional[int]:
        if dom_idx is None:
            return None
        return min(4, dom_idx + 1)

    return _profile_to_rows(grid, mapper, refined=False)


def abstraction_refined_stripe(grid: Grid) -> Grid:
    """Final refinement mirroring the production solver."""

    def mapper(dom_idx: Optional[int]) -> Optional[int]:
        if dom_idx is None:
            return None
        if dom_idx == 0:
            return 2
        if dom_idx in (1, 2):
            return 3
        return 4

    return _profile_to_rows(grid, mapper, refined=True)


ABSTRACTIONS: List[Tuple[str, Abstraction]] = [
    ("naive_stripe", abstraction_naive_stripe),
    ("refined_stripe", abstraction_refined_stripe),
]


def _evaluate_split(name: str, cases: Sequence[dict]) -> None:
    print(f"\n[{name.upper()}]")
    for abs_name, fn in ABSTRACTIONS:
        matches = 0
        first_fail: Optional[int] = None
        total = len(cases)
        predictions: List[Grid] = []
        for idx, sample in enumerate(cases):
            grid = sample["input"]
            pred = fn(grid)
            predictions.append(pred)
            expected = sample.get("output")
            if expected is not None:
                if pred == expected:
                    matches += 1
                elif first_fail is None:
                    first_fail = idx
        if cases and cases[0].get("output") is not None:
            print(
                f"  {abs_name:15s} matches={matches}/{total}"
                f" first_fail={'-' if first_fail is None else first_fail}"
            )
        else:
            print(f"  {abs_name:15s} matches=N/A ({total} cases)")
        if predictions:
            print(f"    preview[0]={predictions[0]}")


def main() -> None:
    cases = _load_cases()
    for split in ("train", "test", "arc_gen"):
        _evaluate_split(split, cases.get(split, []))


if __name__ == "__main__":
    main()
