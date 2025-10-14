# Task b10624e5 – Abstraction Notes

- **naive** – copies horizontal and vertical ornaments from the reference colour-2 blocks without distinguishing inner/outer colours; succeeds on only 1/2 train grids (fails train[0]).
- **refined** – infers ornament colours by sampling rows/columns around each component, guards against duplicated inner stripes, and paints horizontal/vertical bands separately; matches 2/2 train grids and is used as the final solver.

Final solver adopts the refined template expansion; it extracts the cross axes from the colour-1 scaffold and reproduces the horizontal and vertical ornaments with the correct inner/outer colours.

## DSL Structure
- **Typed operations**
  - `findCenterCross : Grid -> (RowIndex, ColIndex)` — locate the dominant row and column of colour 1 that form the central cross.
  - `extractTwoComponents : Grid -> List Component` — gather colour-2 components with bounding boxes and side metadata.
  - `inferOrnamentColours : Grid × Component × (RowIndex, ColIndex) -> OrnamentPalette` — sample neighbouring cells to choose inner/outer horizontal and vertical colours, dropping redundant inner bands.
  - `paintOrnaments : Grid × Component × OrnamentPalette -> Grid` — expand each component horizontally and vertically according to the inferred palette while preserving the frame.
- **Solver summary**: "Find the centre cross, extract each colour-2 component, infer the horizontal/vertical ornament colours from surrounding cells, and paint those ornaments around the components."

## Lambda Representation

```python
def solve_b10624e5(grid: Grid) -> Grid:
    cross = findCenterCross(grid)
    components = extractTwoComponents(grid)

    def repaint(canvas: Grid, component: Component) -> Grid:
        palette = inferOrnamentColours(canvas, component, cross)
        return paintOrnaments(canvas, component, palette)

    return fold_repaint(grid, components, repaint)
```
