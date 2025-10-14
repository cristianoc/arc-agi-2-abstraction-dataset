# e3721c99 Abstractions

- **identity** – trivial passthrough of the input grid. Serves as a baseline and fails on both training examples because none of the 5-marked regions are recoloured.
- **holes_classifier** – classify each connected component of colour 5 by counting internal holes and a couple of size heuristics; paint the component with the corresponding colour class. This solver matches both training grids (2/2) with pixel-perfect accuracy.

The final solution reuses the `holes_classifier` heuristic directly in `analysis/arc2_samples/e3721c99.py`.

## DSL Structure
- **Typed operations**
  - `extractComponents : Grid × Color -> List Component` — gather 5-components as coordinate lists.
  - `buildComponentMask : Grid × Component -> Mask` — convert a component into a tight binary mask.
  - `countInternalHoles : Mask -> Int` — count hole regions that do not touch the mask boundary.
  - `classifyComponent : Mask × Int -> Color` — choose the recolour based on hole count and mask dimensions.
  - `paintComponent : Grid × Component × Color -> Grid` — overwrite the component cells with the classified colour.
- **Solver summary**: "Extract colour-5 components, build masks for each, count their internal holes, classify the component from those features, and recolour it."

## Lambda Representation

```python
def solve_e3721c99(grid: Grid) -> Grid:
    components = extractComponents(grid, 5)

    def repaint(canvas: Grid, component: Component) -> Grid:
        mask = buildComponentMask(grid, component)
        holes = countInternalHoles(mask)
        colour = classifyComponent(mask, holes)
        return paintComponent(canvas, component, colour)

    return fold_repaint(grid, components, repaint)
```
