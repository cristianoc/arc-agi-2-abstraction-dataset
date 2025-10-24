"""Solver for ARC-AGI-2 task 2ba387bc (split: evaluation)."""

from typing import Dict, List, Optional, Tuple

Grid = List[List[int]]


def _extract_components(grid: Grid) -> List[Dict[str, object]]:
    """Detect non-zero components together with their metadata."""
    height = len(grid)
    width = len(grid[0])
    seen = [[False] * width for _ in range(height)]
    components: List[Dict[str, object]] = []

    for r in range(height):
        for c in range(width):
            color = grid[r][c]
            if color == 0 or seen[r][c]:
                continue

            stack = [(r, c)]
            seen[r][c] = True
            min_r = max_r = r
            min_c = max_c = c

            while stack:
                y, x = stack.pop()
                min_r = min(min_r, y)
                max_r = max(max_r, y)
                min_c = min(min_c, x)
                max_c = max(max_c, x)

                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width and not seen[ny][nx] and grid[ny][nx] == color:
                        seen[ny][nx] = True
                        stack.append((ny, nx))

            pattern = [grid[row][min_c : max_c + 1] for row in range(min_r, max_r + 1)]
            has_zero = any(cell == 0 for row in pattern for cell in row)
            components.append(
                {
                    "color": color,
                    "top": min_r,
                    "left": min_c,
                    "pattern": [row[:] for row in pattern],
                    "hollow": has_zero,
                }
            )

    components.sort(key=lambda item: (item["top"], item["left"]))
    return components


def _resample_to_four(pattern: Grid) -> Grid:
    """Resize a small grid to 4×4 via nearest-neighbour sampling."""
    target = 4
    src_h = len(pattern)
    src_w = len(pattern[0])

    if src_h == target and src_w == target:
        return [row[:] for row in pattern]

    def sample(idx: int, size: int) -> int:
        return 0 if size == 1 else int(round(idx * (size - 1) / (target - 1)))

    resized: Grid = []
    for i in range(target):
        src_i = sample(i, src_h)
        row: List[int] = []
        for j in range(target):
            src_j = sample(j, src_w)
            row.append(pattern[src_i][src_j])
        resized.append(row)
    return resized


def _canonical_pattern(component: Optional[Dict[str, object]]) -> Grid:
    if component is None:
        return [[0] * 4 for _ in range(4)]
    pattern = component["pattern"]
    return _resample_to_four(pattern)  # type: ignore[arg-type]

def extractComponents(grid: Grid) -> List[Dict[str, object]]:
    return _extract_components(grid)


def partitionByHollowness(
    components: List[Dict[str, object]]
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    hollows = [comp for comp in components if comp["hollow"]]
    solids = [comp for comp in components if not comp["hollow"]]
    return hollows, solids


def resampleToFour(component: Dict[str, object]) -> Grid:
    pattern = component["pattern"]  # type: ignore[index]
    return _resample_to_four(pattern)  # type: ignore[arg-type]


def packPairs(hollow_blocks: List[Grid], solid_blocks: List[Grid]) -> Grid:
    pair_count = max(len(hollow_blocks), len(solid_blocks))
    output: Grid = []
    for idx in range(pair_count):
        left_block = (
            hollow_blocks[idx]
            if idx < len(hollow_blocks)
            else [[0] * 4 for _ in range(4)]
        )
        right_block = (
            solid_blocks[idx]
            if idx < len(solid_blocks)
            else [[0] * 4 for _ in range(4)]
        )
        for lr, rr in zip(left_block, right_block):
            output.append(lr + rr)
    return output


def solve_2ba387bc(grid: Grid) -> Grid:
    components = extractComponents(grid)
    hollows, solids = partitionByHollowness(components)

    hollow_blocks = [resampleToFour(comp) for comp in hollows]
    solid_blocks = [resampleToFour(comp) for comp in solids]

    return packPairs(hollow_blocks, solid_blocks)


p = solve_2ba387bc
