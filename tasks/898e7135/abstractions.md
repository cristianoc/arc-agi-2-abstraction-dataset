# Task 898e7135 — Abstraction Experiments

- **identity** – simple copy of the input; fails immediately on train (0/2) so it cannot explain the transformation.
- **scale2** – fills holes inside the dominant-color box using area→hole ratio 4 and rescales by ×2; fits all train grids (2/2) but the assumption breaks on the evaluation instance where the ratio is 9, so it cannot generalise.
- **dynamic** – infers the upscale factor by taking the GCD of significant component areas (yielding ×2 on train, ×3 on the eval grid) before stitching colours into zero holes; matches every training example (2/2) and produces the intended structured layout for the unseen test input.

Final approach: use the dynamic abstraction (implemented in `analysis/arc2_samples/898e7135.py`), which adapts the scale factor per grid and reproduces all observed behaviours while giving a plausible test prediction.

## DSL Structure
- **Typed operations**
  - `extractComponents : Grid -> List Component` — compute non-background components with areas used to infer the scale factor.
  - `inferScaleFactor : List Component -> Int` — take the GCD of significant component areas to determine the upscale ratio.
  - `expandComponent : Component × Int -> Grid` — blow up each component by the inferred scale while filling enclosed zeros.
  - `composeUpscaledGrid : List Grid -> Grid` — stitch the upscaled components back into the output grid respecting their relative positions.
- **Solver summary**: "Extract components, infer the upscale factor from their areas, expand each component accordingly, and compose the scaled components into the final grid."

## Lambda Representation

```python
def solve_898e7135(grid: Grid) -> Grid:
    components = extractComponents(grid)
    scale = inferScaleFactor(components)
    upscaled = [expandComponent(component, scale) for component in components]
    return composeUpscaledGrid(upscaled)
```
