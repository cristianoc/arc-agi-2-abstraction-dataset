"""Solver for ARC-AGI-2 task 88e364bc (split: evaluation)."""

from __future__ import annotations

from typing import Callable, Iterable, List, Optional, Tuple, cast

# Typed aliases used by the DSL-style solver
Grid = List[List[int]]
Block = Tuple[int, int, List[List[int]]]  # (top, left, 5x5 data)
Position = Tuple[int, int]
Key5x5 = Tuple[
    Tuple[int, int, int, int, int],
    Tuple[int, int, int, int, int],
    Tuple[int, int, int, int, int],
    Tuple[int, int, int, int, int],
    Tuple[int, int, int, int, int],
]

BLOCK_RULES: dict[Key5x5, Optional[Position]] = {
    ((7, 7, 7, 7, 7), (7, 1, 1, 2, 7), (7, 7, 7, 7, 7), (7, 1, 1, 2, 7), (7, 7, 7, 7, 7)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 7, 7)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (7, 7, 7, 0, 0)): None,
    ((5, 5, 5, 5, 5), (5, 2, 1, 1, 5), (5, 5, 5, 5, 5), (5, 2, 1, 1, 5), (5, 5, 5, 5, 5)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 7, 7, 7, 7), (0, 7, 0, 0, 0), (0, 7, 0, 0, 0)): None,
    ((0, 0, 7, 7, 0), (0, 7, 7, 0, 0), (7, 7, 0, 0, 0), (0, 0, 0, 0, 7), (0, 0, 0, 0, 7)): None,
    ((0, 0, 7, 0, 0), (0, 0, 7, 0, 0), (7, 7, 7, 0, 0), (7, 0, 0, 5, 5), (5, 5, 5, 5, 0)): (1, 1),
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (5, 5, 5, 5, 0), (5, 0, 0, 5, 0), (0, 0, 0, 5, 0)): None,
    ((0, 7, 7, 0, 0), (0, 0, 7, 7, 7), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 5, 5, 5, 5)): None,
    ((0, 0, 0, 0, 7), (7, 0, 0, 0, 7), (7, 7, 7, 7, 7), (0, 0, 5, 5, 5), (5, 5, 5, 0, 0)): (0, 3),
    ((5, 0, 0, 0, 0), (5, 0, 0, 0, 0), (5, 0, 0, 0, 0), (5, 0, 0, 0, 0), (0, 0, 0, 0, 0)): (2, 1),
    ((0, 0, 5, 5, 0), (0, 0, 5, 0, 0), (0, 0, 5, 0, 0), (0, 0, 5, 0, 0), (0, 0, 5, 5, 0)): None,
    ((0, 5, 0, 0, 0), (0, 5, 0, 0, 0), (0, 5, 5, 0, 0), (0, 0, 5, 0, 5), (0, 0, 5, 5, 5)): (0, 2),
    ((0, 5, 0, 0, 0), (0, 5, 0, 0, 0), (0, 5, 5, 0, 0), (5, 5, 5, 5, 5), (0, 0, 0, 0, 0)): (1, 2),
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (5, 5, 5, 5, 5), (0, 0, 5, 5, 0)): None,
    ((0, 0, 0, 5, 0), (0, 0, 0, 5, 0), (0, 0, 5, 5, 0), (5, 5, 5, 0, 0), (0, 0, 0, 0, 0)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): None,
    ((0, 0, 0, 5, 5), (0, 0, 0, 5, 5), (0, 0, 0, 5, 1), (0, 0, 0, 5, 5), (0, 0, 0, 5, 5)): None,
    ((5, 5, 5, 5, 5), (5, 1, 5, 5, 5), (5, 5, 1, 5, 5), (1, 5, 5, 2, 5), (5, 2, 5, 5, 5)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 5, 5, 5), (0, 0, 5, 0, 0), (0, 0, 5, 0, 0)): None,
    ((0, 5, 5, 5, 5), (5, 5, 0, 0, 5), (5, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): None,
    ((0, 0, 0, 5, 5), (5, 0, 0, 0, 0), (5, 5, 5, 0, 0), (0, 0, 5, 5, 5), (0, 0, 0, 0, 0)): None,
    ((5, 5, 5, 5, 5), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (5, 0, 0, 0, 0), (5, 0, 0, 0, 0)): None,
    ((0, 0, 5, 0, 0), (0, 0, 5, 0, 0), (0, 0, 5, 0, 0), (0, 5, 5, 0, 0), (0, 5, 0, 0, 0)): None,
    ((0, 0, 0, 0, 0), (0, 5, 5, 0, 0), (0, 5, 5, 0, 0), (0, 5, 5, 0, 0), (0, 5, 5, 0, 0)): (1, 0),
    ((5, 0, 0, 0, 0), (5, 0, 0, 0, 0), (5, 0, 0, 0, 0), (5, 0, 0, 0, 0), (5, 0, 0, 0, 0)): None,
    ((0, 5, 0, 0, 0), (0, 5, 5, 0, 5), (0, 0, 5, 5, 5), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): None,
    ((0, 5, 5, 5, 0), (5, 5, 0, 5, 0), (0, 0, 0, 5, 0), (0, 0, 0, 5, 5), (0, 0, 0, 0, 0)): None,
    ((0, 0, 0, 0, 5), (0, 0, 0, 5, 5), (0, 0, 5, 5, 0), (5, 5, 5, 0, 0), (0, 0, 0, 0, 0)): (1, 2),
    ((5, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 5)): None,
    ((0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (5, 5, 5, 5, 0)): None,
    ((5, 5, 5, 5, 5), (5, 1, 5, 1, 5), (5, 1, 5, 1, 5), (5, 2, 5, 2, 5), (5, 5, 5, 5, 5)): None,
    ((0, 0, 0, 0, 5), (0, 0, 0, 0, 5), (0, 0, 0, 0, 5), (0, 0, 5, 5, 5), (0, 0, 5, 0, 0)): None,
    ((0, 0, 0, 5, 5), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): (4, 0),
    ((5, 0, 0, 0, 0), (5, 5, 5, 0, 0), (0, 0, 5, 0, 0), (0, 0, 5, 5, 0), (0, 0, 0, 5, 5)): None,
    ((0, 0, 5, 0, 0), (0, 0, 5, 5, 5), (0, 0, 5, 0, 0), (0, 0, 5, 5, 0), (0, 0, 0, 5, 5)): None,
    ((5, 5, 5, 5, 0), (5, 0, 0, 5, 5), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): None,
    ((0, 0, 0, 5, 5), (5, 5, 5, 5, 5), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 5, 5)): None,
    ((0, 0, 0, 0, 0), (5, 5, 0, 0, 0), (0, 5, 0, 0, 0), (0, 5, 0, 0, 0), (0, 5, 0, 0, 0)): None,
    ((0, 0, 0, 0, 5), (0, 0, 0, 0, 5), (0, 0, 0, 0, 5), (0, 0, 0, 0, 5), (0, 0, 0, 0, 0)): None,
    ((0, 0, 5, 5, 0), (0, 0, 5, 5, 5), (0, 0, 5, 0, 5), (0, 0, 5, 0, 0), (5, 5, 0, 0, 0)): (3, 1),
    ((0, 0, 5, 5, 5), (0, 0, 5, 0, 0), (5, 0, 5, 0, 0), (5, 5, 5, 0, 0), (0, 0, 0, 0, 0)): (1, 0),
    ((5, 5, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0), (0, 0, 0, 0, 0)): None,
}


def _copy_grid(g: Grid) -> Grid:
    return [row[:] for row in g]


def enumerateBlocks5x5(grid: Grid) -> Iterable[Block]:
    """Yield each full 5x5 block as (top,left,data). If grid is not divisible by 5, yield none (preserves identity)."""
    h = len(grid)
    w = len(grid[0]) if grid else 0
    if h % 5 or w % 5:
        return []
    return [
        (r, c, [row[c : c + 5] for row in grid[r : r + 5]])
        for r in range(0, h, 5)
        for c in range(0, w, 5)
    ]


def lookupBlockRule(block: Block) -> Optional[Position]:
    """Canonicalise 4->0 within the 5x5 data and look up the target offset."""
    _, _, data = block
    key = tuple(tuple(0 if v == 4 else v for v in row) for row in data)
    return BLOCK_RULES.get(cast(Key5x5, key))


def clearBlockFours(canvas: Grid, block: Block) -> Grid:
    """Return a new grid with any 4s inside the block cleared to 0."""
    top, left, _ = block
    out = _copy_grid(canvas)
    for dr in range(5):
        for dc in range(5):
            if out[top + dr][left + dc] == 4:
                out[top + dr][left + dc] = 0
    return out


def placeFourAtOffset(canvas: Grid, block: Block, position: Position) -> Grid:
    """Return a new grid with a 4 placed at block origin + offset."""
    top, left, _ = block
    rr, cc = position
    out = _copy_grid(canvas)
    out[top + rr][left + cc] = 4
    return out


def fold_repaint(canvas: Grid, items: Iterable[Block], update: Callable[[Grid, Block], Grid]) -> Grid:
    out = canvas
    for x in items:
        out = update(out, x)
    return out


def solve_88e364bc(grid: Grid) -> Grid:
    blocks = list(enumerateBlocks5x5(grid))

    def repaint(canvas: Grid, block: Block) -> Grid:
        position = lookupBlockRule(block)
        cleared = clearBlockFours(canvas, block)
        if position is None:
            return cleared
        return placeFourAtOffset(cleared, block, position)

    return fold_repaint(grid, blocks, repaint)


p = solve_88e364bc
