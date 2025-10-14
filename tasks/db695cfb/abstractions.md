# Abstractions for ARC task db695cfb

- **identity** – served as the sanity baseline; leaves grids unchanged and scores 0/5 on train, immediately failing the first example.
- **connect_ones** – draws diagonal segments that bridge matching `1` endpoints; reaches 2/5 train cases but misses situations where embedded `6`s must propagate.
- **connect_and_extend** – connects the `1` pairs *and* projects perpendicular diagonals from any `6` that lies on those paths; this hybrid matches 5/5 train cases and produces the submitted test prediction shown in the harness log.

Final approach: `connect_and_extend`, which combines the diagonal-bridging abstraction with perpendicular `6` propagation to satisfy every training example and yields a coherent extrapolation on the test grid.

## DSL Structure
- **Typed operations**
  - `groupAnchorsByDiagonal : Grid -> (Dict Int -> List Cell, Dict Int -> List Cell)` — group colour-1 anchors by both diagonal orientations (NW–SE and NE–SW).
  - `paintOnePaths : Grid × Dict Int -> List Cell × Dict Int -> List Cell -> (Grid, Dict Orientation -> Set Cell)` — fill the diagonals that have at least two anchors and record colour-6 seeds encountered along the paths.
  - `extendSixDiagonals : Grid × Dict Orientation -> Set Cell -> Grid` — grow diagonals of colour 6 through each recorded seed, keeping existing 1-paths intact.
  - `finaliseGrid : Grid × Grid -> Grid` — overlay the repainted diagonals onto the original grid.
- **Solver summary**: "Group the colour-1 anchors by both diagonal orientations, paint the connecting 1-paths while collecting 6-seeds, then extend the 6 diagonals through those seeds and merge the result with the original grid."
