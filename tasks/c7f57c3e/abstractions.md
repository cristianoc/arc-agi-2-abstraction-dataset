# c7f57c3e Abstraction Notes

- **variant_a** – promotes the `mid` color to the highlight when it touches the pivot layer and only leaves `pivot` cells that border `c1`; matches 1/2 train cases (fails on train[1]).
- **variant_b** – mirrors `mid` blocks across the pivot layer and swaps them with highlight blocks; matches 1/2 train cases (fails on train[0]).
- **hybrid** – choose variant based on whether `mid` and pivot are adjacent; this refinement solves both train cases and is the solver shipped in `arc2_samples/c7f57c3e.py`.

## DSL Structure
- **Typed operations**
  - `analysePalette : Grid -> (Color, Color, Color, Color)` — determine the background, pivot, mid, and highlight colours from the palette ordering.
  - `checkAdjacency : Grid × Color × Color -> Bool` — test whether the mid and pivot colours touch, selecting between variants.
  - `applyVariantA : Grid × (Color, Color, Color, Color) -> Grid` — promote mid cells, demote pivot cells, and recolour neighbours when mid and pivot are adjacent.
  - `applyVariantB : Grid × (Color, Color, Color, Color) -> Grid` — mirror mid/high components across pivot layers when they are separated.
- **Solver summary**: "Identify the key colours, test adjacency between mid and pivot, then apply either variant A or variant B to swap/promote colours accordingly."

## Lambda Representation

```python
def solve_c7f57c3e(grid: Grid) -> Grid:
    background, pivot, mid, highlight = analysePalette(grid)
    palette = (background, pivot, mid, highlight)
    if checkAdjacency(grid, mid, pivot):
        return applyVariantA(grid, palette)
    return applyVariantB(grid, palette)
```
