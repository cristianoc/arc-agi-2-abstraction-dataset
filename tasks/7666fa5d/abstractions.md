# ARC Task 7666fa5d – Abstraction Notes

- **identity** – Copy of the input; useful only as a baseline (0/2 train).
- **uv_box** – Filled a trimmed rectangle in the `(r+c, c-r)` plane. It captured the overall diamond trend but still flooded the top rows (0/2 train, same first failure as baseline).
- **component_lerp** – Interpolated min/max offsets between adjacent diagonal components. Better coverage yet still leaked above the guide dots (0/2 train).
- **component_corridor** – Final solver. For each background cell we require a guiding component on both the lower-left and upper-right sides of the diagonal. This brackets the corridor perfectly (2/2 train) and generalises cleanly to the test layout.

`component_corridor` is the deployed solution; its prediction on the held-out test grid matches the qualitative expectation (the corridor between the 9-diagonals is filled with 2s only where both sides are present).

## DSL Structure
- **Typed operations**
  - `extractDiagonalComponents : Grid -> List Component` — flood-fill the target colour and validate that each component lies on a single diagonal.
  - `summariseComponents : List Component -> List (Sum, DiffRange)` — record each component’s `row+col` and admissible `col-row` range.
  - `bracketBackgroundCells : Grid × List Summary -> Set Cell` — for each background cell, require supporting components on both sides of its diagonal and collect eligible locations.
  - `fillCorridor : Grid × Set Cell × Color -> Grid` — paint the collected cells with colour 2 while leaving other cells untouched.
- **Solver summary**: "Extract diagonal components, summarise their diagonal sums/diff ranges, test each background cell for bracketing components, and fill the corridor with colour 2."

## Lambda Representation

```python
def solve_7666fa5d(grid: Grid) -> Grid:
    components = extractDiagonalComponents(grid)
    summaries = summariseComponents(components)
    corridor = bracketBackgroundCells(grid, summaries)
    return fillCorridor(grid, corridor, 2)
```
