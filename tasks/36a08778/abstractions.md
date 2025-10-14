# Abstraction Summary — Task 36a08778

- **Identity baseline** – leaves the grid unchanged; 0/6 train matches.
- **Seed extension** – extends top-row 6 scaffolds downward without wrapping runs; 0/6 train matches (helps diagnose vertical structure only).
- **Scaffold unfiltered** – wraps every 2-run with the halo irrespective of connectivity; 2/6 train matches but over-paints unrelated regions.
- **Scaffold filtered (final)** – wraps only the 2-runs touched by the propagated scaffolds; 6/6 train matches and is used in the submitted solver.

Final refinement: scaffold filtered abstraction composed with the original grid reproduction (i.e., the solver) passes every available train case and produces plausible outputs for the test split.

## DSL Structure
- **Typed operations**
  - `extractScaffoldColumns : Grid -> Set Column` — detect the seed columns (colour 6) that act as scaffolds.
  - `extendScaffolds : Grid × Set Column -> Grid` — propagate each scaffold downward until a colour-2 barrier is hit, writing the scaffold colour into the canvas.
  - `collectRuns : Grid -> List Run` — enumerate horizontal colour-2 runs together with their row and span.
  - `filterRunsByScaffold : List Run × Grid -> List Run` — keep only runs that touch the propagated scaffolding.
  - `wrapRunsWithHalo : Grid × List Run -> Grid` — surround the selected runs with the halo colour while leaving untouched runs unchanged.
- **Solver summary**: "Find scaffold columns, propagate them through the grid, select only the 2-runs touched by those scaffolds, then wrap the selected segments with the halo."

## Lambda Representation

```python
def solve_36a08778(grid: Grid) -> Grid:
    scaffold_cols = extractScaffoldColumns(grid)
    scaffolded = extendScaffolds(grid, scaffold_cols)
    runs = collectRuns(grid)
    wrap_targets = filterRunsByScaffold(runs, scaffolded)
    return wrapRunsWithHalo(scaffolded, wrap_targets)
```
