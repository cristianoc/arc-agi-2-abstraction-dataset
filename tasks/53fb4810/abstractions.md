# Task 53fb4810 Abstractions

- `identity`: copied the grid unchanged as a sanity baseline. 0/2 train matches; offered no insight beyond confirming the gap we need to bridge.
- `top4_fill`: filled cells above the first visible `4` in each column with `4`. 0/2 train matches; it over-paints but misses the alternating 2/4 structure evident in train[0].
- `mixed_component`: detects the unique 4-connected component containing both colors {2,4} and tiles its pattern upward to the top of the grid. 2/2 train matches.

Final refinement: `mixed_component` alone forms the submitted solver and yields the chosen test prediction (see harness output). The tiling step preserves the component geometry (horizontal vs vertical) so it generalises cleanly across the observed examples.

## DSL Structure
- **Typed operations**
  - `findMixedComponent : Grid -> Component` — locate the unique component containing both colours {2,4}.
  - `extractComponentPattern : Component -> Grid` — capture the component’s internal layout.
  - `tilePatternUpward : Grid × Component -> Grid` — repeatedly copy the pattern upward until it touches the grid top.
  - `mergeWithOriginal : Grid × Grid -> Grid` — overlay the tiled pattern onto the original background, preserving existing solids.
- **Solver summary**: "Locate the mixed 2/4 component, extract its pattern, tile it upward to the top, and merge the tiles back into the grid."
