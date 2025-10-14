# ARC task 2b83f449 – abstraction notes

- `identity_abstraction`: leaves the grid untouched; 0/2 train matches because the task requires recolouring the 7-structures and boundary cues.
- `cross_paint_abstraction`: repaints each length-3 run of 7s as vertical + horizontal crosses (colour 6) but keeps the rest intact; 0/2 train because boundary colour (3) logic is missing.
- `refined`: adds zero-distance bookkeeping to colour the necessary boundary cells in 3 while preserving the new 6-crosses; 2/2 train and matches the provided test expectation.

## DSL Structure
- **Typed operations**
  - `precomputeZeroDistances : Grid -> (MatrixAbove, MatrixBelow)` — count zeros above/below each column for boundary heuristics.
  - `paintCrossRuns : Grid -> Grid` — recolour length-3 runs of 7s into 6-crosses with 8 arms.
  - `collectBoundaryCells : Grid × Distances -> Set Cell` — evaluate neighbourhood rules to pick boundary cells to recolour to 3.
  - `applyBoundaryRecolor : Grid × Grid × Set Cell -> Grid` — copy the cross-painted grid and apply the 3-boundary recolouring.
- **Solver summary**: "Precompute zero distances, repaint length-3 runs as 6-crosses, identify boundary cells via neighbourhood rules, and recolour those cells to 3."
