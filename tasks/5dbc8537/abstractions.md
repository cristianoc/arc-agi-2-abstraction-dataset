# ARC task 5dbc8537 – abstraction log

- **horizontal-only:** Treat the two-colour region as a 15×7 row canvas; per-row fill runs are recoloured via the palette learnt from the legend. Matches 1/2 train grids (fails on the vertical layout).
- **vertical-only:** Interpret the region as a 9×20 column canvas; per-column fill runs use the legend-derived palette. Matches 1/2 train grids (fails on the horizontal layout).
- **hybrid:** Detect orientation automatically, expand background collars, then dispatch to the appropriate palette (horizontal vs vertical). Matches 2/2 train grids and is used for the final solution/test generation.
