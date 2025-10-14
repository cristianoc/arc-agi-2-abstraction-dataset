### Identity
Baseline copy; leaves impurities intact. Train mismatch at sample 0; no generalisation potential.

### Naive Component Fill
Flood-fills the dominant non-background component; over-grows into background and fails on first train sample.

### Segmented Wedge
Orientation-aware wedge growth with barrier-aware clamping; matches all train cases and preserves the intended gap structure, producing the final solution.

## DSL Structure
- **Typed operations**
  - `classifyPaletteRoles : Grid -> (Color, Color, Color)` — compute background, barrier, and fill colours by frequency and adjacency.
  - `chooseOrientation : Grid × Color × Color -> (Orientation, Bounds)` — measure distances between fill cells and barrier to decide propagation direction and constraint bounds.
  - `seedSegments : Grid × Orientation × Color -> Seeds` — generate initial row or column intervals around existing fill cells.
  - `propagateSegments : Grid × Orientation × Seeds × (Color, Color) × Bounds -> Dict Index -> List Interval` — extend the seed intervals through background cells while respecting helper scans and barrier limits.
  - `paintSegments : Grid × Dict -> List Interval × Color -> Grid` — convert the propagated intervals into filled cell locations and repaint them with the fill colour.
- **Solver summary**: "Identify the background/barrier/fill colours, choose propagation orientation, seed the fill intervals, extend them with barrier-aware clamping, and paint the resulting segments."
