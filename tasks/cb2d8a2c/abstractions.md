# cb2d8a2c Abstractions

- **horizontal_only** – constructs anchor-guided zig-zag corridors for grids whose non-background components are horizontal 1/2 strings. Matches every training case of that type; vertical cases fail immediately (first miss: train[1]).
- **vertical_only** – transposes the grid and runs the same corridor builder, fixing the parity/buffer rules to handle tall 1/2 columns. Solves the vertical trains but misses all horizontal ones (first miss: train[0]).
- **hybrid** – classifies component orientation and dispatches to the corresponding corridor routine. This refinement yields 4/4 train accuracy and produces consistent predictions for the evaluation splits.

The final solver implements the hybrid pipeline with the tuned offset rules that keep the 3-path one cell away from converted 2-stripes while routing around future obstacles.

## DSL Structure
- **Typed operations**
  - `classifyCorridorOrientation : Grid -> Orientation` — decide whether the dominant components are horizontal or vertical.
  - `buildHorizontalCorridor : Grid -> Path` — generate the zig-zag corridor for horizontal layouts using anchor offsets.
  - `buildVerticalCorridor : Grid -> Path` — transpose logic for vertical layouts with adjusted buffer rules.
  - `renderCorridorPath : Grid × Path -> Grid` — paint the corridor onto the grid while respecting the one-cell buffer from colour-2 stripes.
- **Solver summary**: "Classify the corridor orientation, build the matching zig-zag path, and render it onto the grid with the required buffers."
