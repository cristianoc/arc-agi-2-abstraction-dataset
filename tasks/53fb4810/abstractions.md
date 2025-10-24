# Task 53fb4810 Abstractions

- `identity`: copied the grid unchanged as a sanity baseline. 0/2 train matches; offered no insight beyond confirming the gap we need to bridge.
- `top4_fill`: filled cells above the first visible `4` in each column with `4`. 0/2 train matches; it over-paints but misses the alternating 2/4 structure evident in train[0].
- `mixed_components`: detect every 4-connected component containing both colors {2,4} and, for each, tile its internal 2/4 pattern upward within its column span until reaching the top. 2/2 train matches.

Final refinement: `mixed_components` forms the submitted solver. It preserves each component’s geometry and handles multiple mixed components by overlaying their upward tiles independently.

## DSL Structure
- **Typed operations**
  - `findMixedComponents : Grid -> List Component` — enumerate components containing both colours {2,4}.
  - `tilePatternUpward : Grid × Component -> Grid` — paste the component’s pattern upward within its bounding columns.
- **Solver summary**: "Find all mixed 2/4 components and fold an upward-tiling repaint over them."

## Lambda Representation

```python
def solve_53fb4810(grid: Grid) -> Grid:
    components = findMixedComponents(grid)

    def repaint(canvas: Grid, comp: Component) -> Grid:
        return tilePatternUpward(canvas, comp)

    return fold_repaint(grid, components, repaint)
```
