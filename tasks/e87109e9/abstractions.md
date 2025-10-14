# Task e87109e9 – Abstraction Notes

- **identity** – Used as sanity baseline; leaves grid unchanged and scores 0/3 on train.
- **union_template** – Applied per-digit column unions derived from train data; insufficient granularity and still 0/3 on train.
- **nearest_neighbor** – Matches each block to the closest training mask in digit space (16×6 binary target mask) and overlays the recorded diff; 3/3 on train and selected as final solver.

Harness: `python analysis/taske87109e9_abstractions.py` prints per-abstraction train/test success and first-failure indices (test is `n/a` because ARC evaluation lacks labels).

## DSL Structure
- **Typed operations**
  - `splitHeaderBody : Grid -> (Grid, Grid)` — locate the row where the header digits end and split the grid into header and body blocks.
  - `detectTargetColor : Grid × Set Color -> Color` — choose the body colour that should be punched out by checking frequencies against header colours.
  - `readHeaderDigit : Grid × Int -> Optional Digit` — scan each header block to recover the controlling digit.
  - `buildTargetMask : Grid × Int × Color -> Mask` — mark body cells inside the block that currently hold the target colour.
  - `selectDiffMask : Digit × Mask -> Optional Mask` — pick the pre-recorded diff mask whose template best matches the target mask.
  - `applyDiffMask : Grid × Int × Color × Mask -> Grid` — zero out target-colour cells wherever the diff mask is active.
- **Solver summary**: "Split the scoreboard into header and body, detect the target colour, read each digit, compute its body mask, choose the closest diff template, and apply that mask to carve the digit."
