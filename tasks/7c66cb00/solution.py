"""Solver for ARC-AGI-2 task 7c66cb00.

Refactored to expose DSL-style helpers and a main function that matches the
Lambda Representation in abstractions.md.
"""

from collections import defaultdict, deque
from typing import Dict, List, Tuple, TypedDict

Grid = List[List[int]]


class Component(TypedDict):
    height: int
    width: int
    col: int
    offsets: List[Tuple[int, int]]


def split_sections(grid: Grid, base: int) -> List[Tuple[int, int]]:
    """Return row ranges that contain non-uniform content."""
    sections: List[Tuple[int, int]] = []
    start = None
    for r, row in enumerate(grid):
        if all(cell == base for cell in row):
            if start is not None:
                sections.append((start, r - 1))
                start = None
        else:
            if start is None:
                start = r
    if start is not None:
        sections.append((start, len(grid) - 1))
    return sections


def extract_prototypes(
    grid: Grid, sections: List[Tuple[int, int]], base: int
) -> Tuple[Dict[int, List[Component]], List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Collect prototype components above the first target section."""
    prototypes: Dict[int, List[Component]] = defaultdict(list)
    proto_sections: List[Tuple[int, int]] = []
    target_sections: List[Tuple[int, int]] = []

    found_target = False
    width = len(grid[0])

    for r0, r1 in sections:
        colors = {cell for row in grid[r0 : r1 + 1] for cell in row}
        if not found_target and base in colors:
            proto_sections.append((r0, r1))
            height = r1 - r0 + 1
            visited = [[False] * width for _ in range(height)]
            for rr in range(height):
                for cc in range(width):
                    if visited[rr][cc]:
                        continue
                    color = grid[r0 + rr][cc]
                    if color == base:
                        visited[rr][cc] = True
                        continue
                    visited[rr][cc] = True
                    queue: deque[Tuple[int, int]] = deque([(rr, cc)])
                    cells: List[Tuple[int, int]] = []
                    while queue:
                        ar, ac = queue.popleft()
                        cells.append((ar, ac))
                        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            nr, nc = ar + dr, ac + dc
                            if 0 <= nr < height and 0 <= nc < width and not visited[nr][nc] and grid[r0 + nr][nc] == color:
                                visited[nr][nc] = True
                                queue.append((nr, nc))
                    min_r = min(r for r, _ in cells)
                    min_c = min(c for _, c in cells)
                    norm = [(r - min_r, c - min_c) for r, c in cells]
                    comp_height = max(r for r, _ in norm) + 1
                    comp_width = max(c for _, c in norm) + 1
                    prototypes[color].append(
                        Component(
                            height=comp_height,
                            width=comp_width,
                            col=min_c,
                            offsets=norm,
                        )
                    )
        else:
            found_target = True
            target_sections.append((r0, r1))

    return prototypes, proto_sections, target_sections


def apply_prototypes(
    grid: Grid,
    result: Grid,
    section: Tuple[int, int],
    prototypes: Dict[int, List[Component]],
) -> None:
    r0, r1 = section
    width = len(grid[0])
    colors = {cell for row in grid[r0 : r1 + 1] for cell in row}
    if not colors:
        return

    left_edge = grid[r0][0]
    fill_candidates = colors - {left_edge}
    if len(fill_candidates) != 1:
        right_edge = grid[r0][-1]
        fill_candidates = colors - {right_edge}
        if len(fill_candidates) != 1:
            return
        edge_color = right_edge
    else:
        edge_color = left_edge
    fill_color = next(iter(fill_candidates))

    comps = prototypes.get(fill_color)
    if not comps:
        return

    section_height = r1 - r0 + 1
    for comp in comps:
        comp_height = comp["height"]
        comp_width = comp["width"]
        if comp_height > section_height:
            continue
        top_row = r1 - comp_height + 1
        left_col = comp["col"]
        if left_col < 0 or left_col + comp_width > width:
            continue
        for dr, dc in comp["offsets"]:
            rr = top_row + dr
            cc = left_col + dc
            if r0 <= rr <= r1 and 0 <= cc < width:
                result[rr][cc] = edge_color

# === DSL-style helper wrappers ===

def getBackground(grid: Grid) -> int:
    """Background colour selection used by the pipeline (top-left)."""
    return grid[0][0]


def splitSections(grid: Grid, base: int) -> List[Tuple[int, int]]:
    return split_sections(grid, base)


def extractPrototypes(
    grid: Grid, sections: List[Tuple[int, int]], base: int
) -> Tuple[Dict[int, List[Component]], List[Tuple[int, int]], List[Tuple[int, int]]]:
    return extract_prototypes(grid, sections, base)


def clearPrototypeRows(
    grid: Grid, proto_sections: List[Tuple[int, int]], base: int
) -> Grid:
    width = len(grid[0])
    result = [row[:] for row in grid]
    for r0, r1 in proto_sections:
        for r in range(r0, r1 + 1):
            result[r] = [base] * width
    return result


def stampBottomAnchored(
    cleared: Grid,
    prototypes: Dict[int, List[Component]],
    target_sections: List[Tuple[int, int]],
) -> Grid:
    width = len(cleared[0])
    result = [row[:] for row in cleared]
    for section in target_sections:
        apply_prototypes(cleared, result, section, prototypes)
    return result


# === Lambda-shaped main (must match abstractions.md) ===

def solve_7c66cb00(grid: Grid) -> Grid:
    base = getBackground(grid)
    sections = splitSections(grid, base)
    prototypes, protoSections, targetSections = extractPrototypes(grid, sections, base)
    cleared = clearPrototypeRows(grid, protoSections, base)
    return stampBottomAnchored(cleared, prototypes, targetSections)


p = solve_7c66cb00
