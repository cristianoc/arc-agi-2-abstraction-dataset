# Abstraction Notes for Task 8b7bacbf

- **identity** – Leave the grid untouched. Accuracy: `train 0/4`; `test –` (no targets). Fails immediately because all training outputs add new colour-4/7 patches.
- **fill_all_enclosed** – Paint every uniquely bounded zero cavity with the max colour. Accuracy: `train 1/4`; `test –`. Captures the obvious 5- and 3-bounded holes but over-fills the small 2-bounded cavities near the top.
- **distance_filtered_fill** – Only fill cavities whose enclosing colour is close to a frequent, informative colour (≤4 if higher than the border, else ≤3). Accuracy: `train 4/4`; `test –`. This selective distance gate matches all available cases and is used in the submitted solver.

No arc-gen fixtures are provided for this task; the harness therefore reports only train/test splits.

## DSL Structure
- **Typed operations**
  - `extractZeroComponents : Grid -> List Component` — flood-fill zero cavities and capture their cell lists plus boundary colours.
  - `measureBoundaryDistances : Grid × List Component -> DistanceInfo` — for each cavity, compute the minimum Manhattan distance to candidate colours grouped by frequency.
  - `shouldFill : Component × DistanceInfo -> Bool` — apply the distance thresholds (≤4 for higher colours, ≤3 otherwise) to decide whether to fill a cavity.
  - `paintComponent : Grid × Component × Color -> Grid` — recolour all cells of qualifying cavities with the maximal colour.
- **Solver summary**: "Extract zero cavities, measure their closest informative colours, keep those within the learned distance thresholds, and repaint them with the maximal colour."

## Lambda Representation

```python
def solve_8b7bacbf(grid: Grid) -> Grid:
    cavities = extractZeroComponents(grid)
    distance_info = measureBoundaryDistances(grid, cavities)

    def repaint(canvas: Grid, component: Component) -> Grid:
        info = distance_info.get(component)
        if info is None or not shouldFill(component, info):
            return canvas
        return paintComponent(canvas, component, info.colour)

    return fold_repaint(grid, cavities, repaint)
```
