# ARC task 5dbc8537 – abstraction log

- **horizontal-only:** Treat the two-colour region as a 15×7 row canvas; per-row fill runs are recoloured via the palette learnt from the legend. Matches 1/2 train grids (fails on the vertical layout).
- **vertical-only:** Interpret the region as a 9×20 column canvas; per-column fill runs use the legend-derived palette. Matches 1/2 train grids (fails on the horizontal layout).
- **hybrid:** Detect orientation automatically, expand background collars, then dispatch to the appropriate palette (horizontal vs vertical). Matches 2/2 train grids and is used for the final solution/test generation.

## DSL Structure
- **Typed operations**
  - `findTwoColourRegion : Grid -> (Color, Box)` — locate the instruction block and return the fill colour with its bounding box.
  - `inferOrientation : Grid × Box -> Orientation` — decide whether the block spans the full height (horizontal mode) or width (vertical mode).
  - `expandCollar : Grid × Box -> Box` — grow the bounding box outward while preserving background collars.
  - `repaintWithPalette : Grid × Box × Orientation -> Grid` — recolour the block using the orientation-specific hard-coded palette maps.
- **Solver summary**: "Find the two-colour instruction block, infer its orientation, expand the bounding box to include collars, then repaint the block with the corresponding palette."

## Lambda Representation

```python
def solve_5dbc8537(grid: Grid) -> Grid:
    fill_color, box = findTwoColourRegion(grid)
    orientation = inferOrientation(grid, box)
    expanded = expandCollar(grid, box)
    return repaintWithPalette(grid, expanded, orientation)
```
