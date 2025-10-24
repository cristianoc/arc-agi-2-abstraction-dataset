# Task d59b0160 – Abstraction Notes

- **identity** – plain copy of the grid; leaves all cavities intact (0/3 train).
- **touch_right** – fills only rooms that touch the right boundary; captures the large rectangular hole but misses the off-boundary pockets (1/3 train, first miss train[0]).
- **internal_height4** – targets interior rooms of height ≤4; fails because key holes straddle edges (0/3 train).
- **full_rule** – combines edge-touch heuristics (right-edge fill, shallow interior rooms, left-edge height guard, height-5 edge bias) and achieves 3/3 train with no failures; used for the final solver, producing the visually coherent fill on the test grid.

## DSL Structure
- **Typed operations**
  - `extractNonSevenComponents : Grid -> List Component` — gather 4-connected components whose colour is not 7, with bbox stats.
  - `shouldFill : Component × Int × Int -> Bool` — decide whether to repaint a component to colour 7 based on width/height and edge contact.
  - `paintComponent : Grid × Component × Color -> Grid` — overwrite all component cells with the given colour.
- **Solver summary**: "Extract non-7 components, decide which to fill via simple guards, and repaint selected components to colour 7 using fold_repaint."

## Lambda Representation

```python
def solve_d59b0160(grid: Grid) -> Grid:
    components = extractNonSevenComponents(grid)
    if not grid:
        return grid
    h, w = len(grid), len(grid[0])

    def repaint(canvas: Grid, comp: Component) -> Grid:
        return paintComponent(canvas, comp, 7) if shouldFill(comp, h, w) else canvas

    return fold_repaint(grid, components, repaint)
```
