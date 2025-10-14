# Task 80a900e0 – Abstraction Notes

- `identity`: left the grid untouched; 0/2 train matches (first failure at train[0]), so it cannot explain any of the diagonal growth.
- `handle_extension_no_guard`: extended perpendicular stripes from every diagonal handle without conflict checks; 2/2 train matches but risks overwriting non-background structure when handles intersect other colours.
- `handle_extension_guarded`: same extension logic while guarding against overwriting non-background cells; 2/2 train matches and is the only safe variant for novel grids.

Final refinement uses `handle_extension_guarded`, yielding the diagonal-stripe propagation required by both training examples and the held-out evaluation grid.

## DSL Structure
- **Typed operations**
  - `groupHandlesByColour : Grid -> List (Color, List Cell)` — collect non-background colours that form diagonal handles.
  - `findHandleRuns : List (Color, List Cell) -> HandleRuns` — detect long diagonal runs per colour and record target diagonals to extend.
  - `extendAlongAxis : Grid × HandleRuns × Color -> Grid` — extend stripes along the perpendicular axis while guarding against overwriting non-background cells.
- **Solver summary**: "Group handles by colour, detect which diagonals should grow, and extend those diagonals along the perpendicular axis with overwrite guards."

## Lambda Representation

```python
def solve_80a900e0(grid: Grid) -> Grid:
    handles = groupHandlesByColour(grid)
    handle_runs = findHandleRuns(handles)
    colours = [colour for colour, _ in handles]

    def extend(canvas: Grid, colour: Color) -> Grid:
        return extendAlongAxis(canvas, handle_runs, colour)

    return fold_repaint(grid, colours, extend)
```
