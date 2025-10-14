# Task 7b3084d4 Abstraction Notes

- **identity** – Baseline that returns the input grid; unsurprisingly 0/3 train matches because the task requires compressing components into a compact square summary.
- **first_fit** – Greedy row-major packing without backtracking; it jams on train[0] and train[1], leaving shapes misaligned (0/3).
- **perimeter_dfs** – The perimeter-guided DFS from the solver keeps every component shape (3/3 train). Harness preview shows the 14×14 test tiling preserves the 7/8/3/2 regions, so we kept this refinement.

## DSL Structure
- **Typed operations**
  - `extractComponents : Grid -> List Component` — gather non-zero components with cell lists for later placement.
  - `enumerateVariants : Component -> List Shape` — normalise each component and produce all rotated/mirrored variants.
  - `searchTilings : List Shape -> (Grid, Score)` — depth-first search the space of placements on the target square, maximising perimeter and a weighted feature score.
  - `renderBestTiling : Grid -> Grid` — convert the best placement board into the final coloured grid.
- **Solver summary**: "Extract all components, generate their dihedral variants, search for the perimeter-maximising tiling of the square canvas, and render the highest scoring placement."

## Lambda Representation

```python
def solve_7b3084d4(grid: Grid) -> Grid:
    components = extractComponents(grid)
    shapes = [shape for component in components for shape in enumerateVariants(component)]
    board, _ = searchTilings(shapes)
    return renderBestTiling(board)
```
