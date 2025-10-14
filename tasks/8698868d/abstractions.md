# Task 8698868d – Abstraction Notes

- `identity`: Pass-through baseline; leaves the composite palette untouched and fails immediately on the first train case (0/2 matches).
- `column_priority_v1`: Rebuilds background tiles but uses a mild column bias when pairing shape exemplars, which mismatches the top-right overlay (1/2 matches; fails on train[1]).
- `column_priority_v2`: Strengthens the column weighting, yielding the intended background→shape assignment and reproducing both training outputs; test inference produces a coherent 2×2 tiling with centered motifs.

Final choice: `column_priority_v2` abstraction.

## DSL Structure
- **Typed operations**
  - `extractComponents : Grid -> List Component` — gather non-background components with bounding boxes, areas, and centroids.
  - `separateBackgroundAndShapes : List Component -> (List Component, List Component)` — identify large background tiles vs. smaller motif shapes.
  - `assignShapesToTiles : List Component × List Component -> Dict Int -> Component` — pair shapes to background tiles by minimising row/column distance with column-heavy weighting.
  - `renderTiledLayout : Grid × Dict -> Component -> Grid` — tile the background colours into a grid layout and stamp each assigned shape into the centered position.
- **Solver summary**: "Extract components, split background tiles from motifs, match motifs to tiles using a column-weighted cost, and render the tiled layout with centred shapes."
