# Abstraction Summary — Task 36a08778

- **Identity baseline** – leaves the grid unchanged; 0/6 train matches.
- **Seed extension** – extends top-row 6 scaffolds downward without wrapping runs; 0/6 train matches (helps diagnose vertical structure only).
- **Scaffold unfiltered** – wraps every 2-run with the halo irrespective of connectivity; 2/6 train matches but over-paints unrelated regions.
- **Scaffold filtered (final)** – wraps only the 2-runs touched by the propagated scaffolds; 6/6 train matches and is used in the submitted solver.

Final refinement: scaffold filtered abstraction composed with the original grid reproduction (i.e., the solver) passes every available train case and produces plausible outputs for the test split.

## DSL Structure
- **Typed operations**
  - `extractScaffoldColumns : Grid -> List Column` — detect the seed columns (colour 6) that act as scaffolds.
  - `propagateScaffolds : Grid × List Column -> Dict Column -> Segment` — extend each scaffold downward while recording the segments the scaffold touches.
  - `selectWrapTargets : Dict Column -> Segment -> List Segment` — filter candidate colour-2 runs to those contacted by an active scaffold.
  - `wrapSegmentsWithHalo : Grid × List Segment -> Grid` — surround the selected runs with the halo colour while leaving untouched runs unchanged.
- **Solver summary**: "Find scaffold columns, propagate them through the grid, select only the 2-runs touched by those scaffolds, then wrap the selected segments with the halo."
