# cb2d8a2c Abstractions

- **horizontal_only** – constructs anchor-guided zig-zag corridors for grids whose non-background components are horizontal 1/2 strings. Matches every training case of that type; vertical cases fail immediately (first miss: train[1]).
- **vertical_only** – transposes the grid and runs the same corridor builder, fixing the parity/buffer rules to handle tall 1/2 columns. Solves the vertical trains but misses all horizontal ones (first miss: train[0]).
- **hybrid** – classifies component orientation and dispatches to the corresponding corridor routine. This refinement yields 4/4 train accuracy and produces consistent predictions for the evaluation splits.

The final solver implements the hybrid pipeline with the tuned offset rules that keep the 3-path one cell away from converted 2-stripes while routing around future obstacles.

