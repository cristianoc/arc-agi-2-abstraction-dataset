# ARC Task a6f40cea Abstractions

- **baseline_projection** – projects colors orthogonally from the frame using axis-aligned run lengths only. It reaches 2/3 training success but misses the evaluation example that requires alternating bands (first failure at train[2]).
- **augmented_projection** – extends the projection with sequence heuristics (alternating stripes from left/right/bottom) and targeted gap closing. It solves all 3/3 training cases and yields the final submission (see script output for the generated test grid).

## DSL Structure
- **Typed operations**
  - `detectFrame : Grid -> Frame` — locate the rectangular frame (bounds and frame colour).
  - `projectBorderColours : Grid × Frame -> Grid` — scan each border direction and project colours inward based on contiguous border runs.
  - `applySequenceHeuristics : Grid × Frame -> Grid` — inject alternating stripe sequences derived from side patches and adjust offsets.
  - `closeGaps : Grid × Frame -> Grid` — fill single-cell gaps horizontally and vertically to smooth the projection.
- **Solver summary**: "Detect the frame, project border colours into the interior, apply the learned sequence heuristics for alternating bands, and close any remaining gaps."
