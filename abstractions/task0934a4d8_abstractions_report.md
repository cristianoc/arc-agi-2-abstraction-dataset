horizontal_mirror_offset2 — mirror the block opposite the 8 rectangle across the vertical axis with a fixed offset of 2 columns. Worked on 3/4 train cases (first miss at train[2]); fails when the copied block actually lies across the horizontal axis.

vertical_mirror_offset2 — same idea but across the horizontal axis. Also achieved 3/4 train accuracy (first miss at train[0]); fails on instances where the missing block is positioned horizontally.

hybrid_offset2 — select between horizontal and vertical mirrors by comparing the offset distance and preferring the farther candidate (ties broken by the 8-count heuristic). This variation matched all train examples and produces a 9x3 output for the test case, aligning with the copied block observed in the grid.
