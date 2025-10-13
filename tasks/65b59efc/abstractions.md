# ARC Task 65b59efc Abstraction Notes

- **dominant_fill** – Partition rows/cols on heavy-`5` separators and tile each cell with its dominant non-background color; matches: train 0/3 (fails immediately).
- **mapped_tiles** – Uses the handcrafted template lookup per segmented cell with fallback dominant fills; matches: train 3/3, adopted for final solver (test projections yield 25×30 canvases consistent with observed training scaling).

The deployed solver uses the mapped-tiles abstraction, which reproduces the full training set and extrapolates the large test silhouettes produced by the harness.
