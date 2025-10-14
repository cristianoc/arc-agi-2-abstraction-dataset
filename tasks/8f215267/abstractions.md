# ARC task 8f215267 – abstraction notes

- Identity: baseline passthrough used to confirm dataset wiring; 0/3 train matches.
- Striped frames v0: reconstruct frames while counting distinct colours in the noisy patch; 0/3 train matches.
- Striped frames v1: introduce canonical patch templates with fallback to v0 counting; 3/3 train matches, produces clean prediction for the hidden test.
- Final solver: same pipeline as v1 packaged in `solve_8f215267`, adopted as the final refinement.

All evaluations were produced with `analysis/task8f215267_abstractions.py::evaluate_abstractions()`; no arc-gen samples are provided for this task.

## DSL Structure
- **Typed operations**
  - `extractFrames : Grid -> List Frame` — locate rectangular frames and capture their bounding boxes and colours.
  - `sliceInstructionPatch : Grid × Frame -> Patch` — extract and canonicalise the noisy patch to the right of each frame.
  - `lookupStripeCount : Patch -> Int` — map the canonical patch to a stripe count using the learned dictionary (with fallback estimation).
  - `clearAndPaintStripes : Grid × Frame × Int -> Grid` — erase the frame interior, then paint the specified number of vertical stripes in the frame colour.
  - `clearNoise : Grid × List Frame -> Grid` — remove residual pixels outside the frames after reconstruction.
- **Solver summary**: "Extract each frame, read the instruction patch, look up the stripe count, repaint the frame interior accordingly, and clear the surrounding noise."
