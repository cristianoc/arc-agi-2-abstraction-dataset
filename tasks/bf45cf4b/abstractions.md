# bf45cf4b Abstraction Notes

**identity** — Copy input directly. Serves as a baseline and fails on train case 0 (0/3) because it cannot synthesize the required tiling.

**mask_tiling** — Detect non-background components, treat the single-colour component as a Boolean mask, and tile the multi-colour component’s bounding box wherever the mask is true. Hits 3/3 on train and yields the expected 25×25 patterned prediction on test.

Final solver: reuse of `mask_tiling` from `analysis/arc2_samples/bf45cf4b.py`.

## DSL Structure
- **Typed operations**
  - `extractComponents : Grid -> (Component, Component)` — separate mask and pattern components via connected component analysis.
  - `computeMaskLayout : Component -> GridBool` — convert the single-colour component into a boolean mask over its bounding box.
  - `extractPatternTile : Grid × Component -> Grid` — slice the multi-colour component to obtain the tile that will be replicated.
  - `tilePatternByMask : GridBool × Grid -> Grid` — replicate the pattern tile wherever the mask is true and background elsewhere.
- **Solver summary**: "Split the grid into mask and pattern components, turn the mask into a boolean layout, extract the pattern tile, and tile the pattern across every mask position."

## Lambda Representation

```python
def solve_bf45cf4b(grid: Grid) -> Grid:
    mask_component, pattern_component = extractComponents(grid)
    mask_layout = computeMaskLayout(mask_component)
    pattern_tile = extractPatternTile(grid, pattern_component)
    return tilePatternByMask(mask_layout, pattern_tile)
```
