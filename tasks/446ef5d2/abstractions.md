# ARC Task 446ef5d2 – Abstraction Notes

- `identity`: merely rewrites color `4` to background `8`. Useful sanity check, but it leaves all geometry untouched and fails on both training examples (0/2 matches).
- `horizontal_compactor`: flattens each color's components into a single band ordered by `minx`. It captures the catalogue idea but breaks whenever a color requires wrapping (fails on the second train case; 0/2 matches).
- `grid_compactor`: packs per-color components into a near-square grid, reorders per-row by component height, then centers the assembled rectangle with a border of the dominant color. This abstraction fits both training grids (2/2 matches) and is used in the final solver.

Final approach: apply the `grid_compactor` to all non-background colors after removing noise (color `4`), embed the resulting rectangle over an `8` background, and reuse the dominant color for borders/separators. Test predictions are produced by the same pipeline.

