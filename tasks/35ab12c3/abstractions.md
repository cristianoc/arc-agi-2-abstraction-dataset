# Task 35ab12c3 Abstractions

- **diag_expand**: Connected equal-color points via row/column adjacency and full diagonal chains; it reconstructed rough hulls but introduced spurious interior diagonals, failing all training cases.
- **hull_shift**: Built color hulls with conflict-aware linking, then generated singleton layers by shifting the nearest base component; solved 3/3 training grids and produced a coherent test prediction.

## DSL Structure
- **Typed operations**
  - `extractAnchors : Grid -> Anchors` — gather per-colour anchor points and singleton cells that guide hull placement.
  - `buildPrimaryHulls : Grid -> Hulls` — construct base hull polygons for colours with multiple cells.
  - `matchSingletons : Anchors × Hulls -> Shifts` — pair singleton anchors with neighbouring hulls and compute the required shifts.
  - `applyHullShifts : Grid × Hulls × Shifts -> Grid` — translate hulls according to the computed shifts and paint the resulting layers back into the grid.
- **Solver summary**: "Collect anchors, build base hulls for multi-cell colours, compute shifts that align singleton anchors with those hulls, then render the shifted hulls into the output grid."

## Lambda Representation

```python
def solve_35ab12c3(grid: Grid) -> Grid:
    anchors = extractAnchors(grid)
    primary_hulls = buildPrimaryHulls(grid)
    shifts = matchSingletons(anchors, primary_hulls)
    return applyHullShifts(grid, primary_hulls, shifts)
```
