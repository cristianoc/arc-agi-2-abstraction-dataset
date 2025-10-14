# ARC Task 446ef5d2 – Abstraction Notes

- `identity`: merely rewrites color `4` to background `8`. Useful sanity check, but it leaves all geometry untouched and fails on both training examples (0/2 matches).
- `horizontal_compactor`: flattens each color's components into a single band ordered by `minx`. It captures the catalogue idea but breaks whenever a color requires wrapping (fails on the second train case; 0/2 matches).
- `grid_compactor`: packs per-color components into a near-square grid, reorders per-row by component height, then centers the assembled rectangle with a border of the dominant color. This abstraction fits both training grids (2/2 matches) and is used in the final solver.

Final approach: apply the `grid_compactor` to all non-background colors after removing noise (color `4`), embed the resulting rectangle over an `8` background, and reuse the dominant color for borders/separators. Test predictions are produced by the same pipeline.

## DSL Structure
- **Typed operations**
  - `filterNoise : Grid × Color -> Grid` — drop the spurious colour-4 cells before packing.
  - `extractPerColorComponents : Grid -> Dict[Color, List Component]` — gather components per colour with width/height metadata.
  - `packComponentsIntoGrid : Dict[Color, List Component] -> PackedGrid` — arrange each colour’s components into a near-square grid ordered by component height.
  - `embedPackedGrid : PackedGrid × Color -> Grid` — centre the packed rectangle on an `8` background and draw the dominant-colour border.
- **Solver summary**: "Filter out noise, collect components per colour, pack them into a balanced grid, then embed the packed rectangle on the background with the dominant border."

## Lambda Representation

```python
def solve_446ef5d2(grid: Grid) -> Grid:
    cleaned = filterNoise(grid, 4)
    per_color = extractPerColorComponents(cleaned)
    packed = packComponentsIntoGrid(per_color)
    return embedPackedGrid(packed, 8)
```
