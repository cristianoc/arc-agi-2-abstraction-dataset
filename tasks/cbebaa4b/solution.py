"""Solver for ARC-AGI-2 task cbebaa4b."""

from collections import Counter, defaultdict, deque
from typing import Dict, Iterable, List, Sequence, Tuple, cast


Grid = List[List[int]]
Point = Tuple[int, int]
Vector = Tuple[int, int]
Translations = Dict[int, Vector]

# Gadgets bundle used by the typed-DSL style wrappers
# (components, owner, connectors, door_index)
Gadgets = Tuple[
    List[Dict[str, object]],
    List[List[int]],
    Dict[int, List[Tuple[Point, Vector]]],
    int,
]


def in_bounds(h: int, w: int, r: int, c: int) -> bool:
    return 0 <= r < h and 0 <= c < w


def deep_copy(grid: Grid) -> Grid:
    return [row[:] for row in grid]


def get_components(grid: Grid) -> Tuple[List[Dict[str, object]], List[List[int]]]:
    """Return connected components (excluding colours 0 and 2) and owner map."""

    h, w = len(grid), len(grid[0])
    owner = [[-1] * w for _ in range(h)]
    components: List[Dict[str, object]] = []
    visited = [[False] * w for _ in range(h)]

    for r in range(h):
        for c in range(w):
            colour = grid[r][c]
            if colour in (0, 2) or visited[r][c]:
                continue
            idx = len(components)
            queue = [(r, c)]
            visited[r][c] = True
            cells: List[Point] = []
            while queue:
                cr, cc = queue.pop()
                cells.append((cr, cc))
                owner[cr][cc] = idx
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = cr + dr, cc + dc
                    if (
                        in_bounds(h, w, nr, nc)
                        and not visited[nr][nc]
                        and grid[nr][nc] == colour
                    ):
                        visited[nr][nc] = True
                        queue.append((nr, nc))
            ys = [y for y, _ in cells]
            xs = [x for _, x in cells]
            components.append(
                {
                    "colour": colour,
                    "cells": cells,
                    "bbox": (min(ys), max(ys), min(xs), max(xs)),
                }
            )
    return components, owner


def get_connectors(grid: Grid, owner: List[List[int]]) -> Dict[int, List[Tuple[Point, Vector]]]:
    """Return connector cells (colour 2) attached to each component."""

    h, w = len(grid), len(grid[0])
    connectors: Dict[int, List[Tuple[Point, Vector]]] = defaultdict(list)
    for r in range(h):
        for c in range(w):
            if grid[r][c] != 2:
                continue
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if in_bounds(h, w, nr, nc) and owner[nr][nc] != -1:
                    comp_id = owner[nr][nc]
                    # Direction from component cell towards connector.
                    connectors[comp_id].append(((r, c), (r - nr, c - nc)))
                    break
    return connectors


def find_door(components: Sequence[Dict[str, object]]) -> int:
    """Locate the solid rectangular "door" component."""

    best_idx = -1
    best_area = -1
    for idx, comp in enumerate(components):
        cells = cast(List[Point], comp["cells"])
        y0, y1, x0, x1 = cast(Tuple[int, int, int, int], comp["bbox"])  # type: ignore[misc]
        height = y1 - y0 + 1
        width = x1 - x0 + 1
        area = height * width
        if len(cells) == area and min(height, width) >= 3 and area > best_area:
            best_idx = idx
            best_area = area
    if best_idx == -1:
        raise ValueError("Door component not found")
    return best_idx


def build_edges(connectors: Dict[int, List[Tuple[Point, Vector]]]) -> Dict[int, Dict[int, Vector]]:
    """Infer preferred translation deltas between connected components."""

    edges: Dict[int, Dict[int, Vector]] = defaultdict(dict)
    comp_ids = list(connectors)
    for i, a in enumerate(comp_ids):
        con_a = connectors[a]
        for b in comp_ids[i + 1 :]:
            con_b = connectors[b]
            counter: Counter[Vector] = Counter()
            for (pa, dir_a) in con_a:
                for (pb, dir_b) in con_b:
                    if dir_a[0] == -dir_b[0] and dir_a[1] == -dir_b[1]:
                        delta = (pa[0] - pb[0], pa[1] - pb[1])
                        counter[delta] += 1
            if not counter:
                continue
            delta, count = max(counter.items(), key=lambda item: (item[1], -abs(item[0][0]) - abs(item[0][1])))
            if count >= 2:
                edges[a][b] = delta
                edges[b][a] = (-delta[0], -delta[1])
    return edges


def fallback_place(
    grid: Grid,
    components: Sequence[Dict[str, object]],
    connectors: Dict[int, List[Tuple[Point, Vector]]],
    translations: Dict[int, Vector],
) -> None:
    """Greedy connector-alignment fallback for components not in the edge graph."""

    h, w = len(grid), len(grid[0])
    remaining = [idx for idx in range(len(components)) if idx not in translations]
    if not remaining:
        return

    placed_cells = set()
    for idx, (dy, dx) in translations.items():
        for r, c in cast(List[Point], components[idx]["cells"]):  # type: ignore[index]
            placed_cells.add((r + dy, c + dx))

    # Known connector coordinates in absolute space.
    known_conns = set()
    for idx, (dy, dx) in translations.items():
        for (r, c), _ in connectors.get(idx, []):
            known_conns.add((r + dy, c + dx))

    # Iteratively place remaining components by aligning connectors to known positions.
    while remaining:
        progress = False
        for idx in remaining[:]:
            con_list = connectors.get(idx, [])
            if not con_list:
                continue
            best = None
            conn_positions = [pos for pos, _ in con_list]
            for (cr, cc) in conn_positions:
                for tr, tc in known_conns:
                    dy, dx = tr - cr, tc - cc
                    # Validate placement bounds and overlap.
                    good = True
                    for r, c in cast(List[Point], components[idx]["cells"]):  # type: ignore[index]
                        nr, nc = r + dy, c + dx
                        if not in_bounds(h, w, nr, nc) or (nr, nc) in placed_cells:
                            good = False
                            break
                    if not good:
                        continue
                    shifted = {(r + dy, c + dx) for (r, c) in conn_positions}
                    matches = len(shifted & known_conns)
                    if matches == 0:
                        continue
                    if best is None or matches > best[0]:
                        best = (matches, dy, dx, shifted)
            if best is None:
                continue
            _, dy, dx, shifted = best
            translations[idx] = (dy, dx)
            for r, c in cast(List[Point], components[idx]["cells"]):  # type: ignore[index]
                placed_cells.add((r + dy, c + dx))
            known_conns |= shifted
            remaining.remove(idx)
            progress = True
        if not progress:
            # If we cannot place the rest, keep them at original location.
            for idx in remaining:
                translations[idx] = (0, 0)
            break


def apply_translations(
    grid: Grid,
    components: Sequence[Dict[str, object]],
    connectors: Dict[int, List[Tuple[Point, Vector]]],
    translations: Dict[int, Vector],
) -> Grid:
    h, w = len(grid), len(grid[0])
    out = [[0] * w for _ in range(h)]

    # Place coloured components.
    for idx, comp in enumerate(components):
        colour = cast(int, comp["colour"])  # type: ignore[index]
        dy, dx = translations.get(idx, (0, 0))
        for r, c in cast(List[Point], comp["cells"]):  # type: ignore[index]
            nr, nc = r + dy, c + dx
            out[nr][nc] = colour

    # Place connectors (colour 2) after all shapes.
    for idx, con_list in connectors.items():
        dy, dx = translations.get(idx, (0, 0))
        for (r, c), _ in con_list:
            nr, nc = r + dy, c + dx
            out[nr][nc] = 2

    return out


def extractGadgetComponents(grid: Grid) -> Gadgets:
    components, owner = get_components(grid)
    if not components:
        # Represent an empty setup with an empty connectors map and dummy door index
        return (components, owner, {}, -1)
    connectors = get_connectors(grid, owner)
    door = find_door(components)
    return (components, owner, connectors, door)


def pairConnectors(gadgets: Gadgets) -> Dict[int, Dict[int, Vector]]:
    components, owner, connectors, door = gadgets
    # Only the connectors map matters to infer deltas
    return build_edges(connectors)


def buildConnectorGraph(gadgets: Gadgets, edges: Dict[int, Dict[int, Vector]]) -> Translations:
    components, owner, connectors, door = gadgets
    if owner:
        h, w = len(owner), len(owner[0])
    else:
        h, w = 0, 0
    if not components:
        return {}
    translations: Translations = {door: (0, 0)}
    queue = deque([door])
    while queue:
        src = queue.popleft()
        base = translations[src]
        for dst, delta in edges.get(src, {}).items():
            candidate = (base[0] + delta[0], base[1] + delta[1])
            if dst in translations:
                if translations[dst] != candidate:
                    # Prefer already assigned value; inconsistent cycles should not occur.
                    continue
            else:
                translations[dst] = candidate
                queue.append(dst)

    # Greedy fallback for components not in the edge graph
    fallback_place(grid=owner and [[0]*len(owner[0]) for _ in range(len(owner))] or [],  # dummy grid shape
                   components=components,
                   connectors=connectors,
                   translations=translations)

    # Ensure all components have translations (default to zero if unreachable).
    for idx in range(len(components)):
        translations.setdefault(idx, (0, 0))
    return translations


def applyTranslations(grid: Grid, graph: Translations) -> Grid:
    components, owner = get_components(grid)
    if not components:
        return deep_copy(grid)
    connectors = get_connectors(grid, owner)
    return apply_translations(grid, components, connectors, graph)


def solve_cbebaa4b(grid: Grid) -> Grid:
    gadgets = extractGadgetComponents(grid)
    pairs = pairConnectors(gadgets)
    graph = buildConnectorGraph(gadgets, pairs)
    return applyTranslations(grid, graph)


p = solve_cbebaa4b
