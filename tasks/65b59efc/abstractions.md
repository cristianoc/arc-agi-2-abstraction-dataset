# ARC Task 65b59efc Abstraction Notes

- **dominant_fill** – Partition rows/cols on heavy-`5` separators and tile each cell with its dominant non-background color; matches: train 0/3 (fails immediately).
- **mapped_tiles** – Uses the handcrafted template lookup per segmented cell with fallback dominant fills; matches: train 3/3, adopted for final solver (test projections yield 25×30 canvases consistent with observed training scaling).

The deployed solver uses the mapped-tiles abstraction, which reproduces the full training set and extrapolates the large test silhouettes produced by the harness.

## DSL Structure
- **Typed operations**
  - `segmentBoardCells : Grid -> List CellRegion` — partition the grid into cell-sized regions delimited by the heavy `5` separators.
  - `lookupCellTemplate : CellRegion -> TemplateId` — determine which template to use for each region based on its legend mapping.
  - `renderTemplate : TemplateId -> Grid` — fetch or synthesise the template corresponding to the mapped tile.
  - `placeTemplate : Grid × CellRegion × Grid -> Grid` — write the template into the region, falling back to the dominant colour when no mapping exists.
- **Solver summary**: "Segment the board into cell regions, look up each region’s template, render the template, and place it into the output with fallback dominant fills."
