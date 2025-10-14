# Task 981571dc Abstraction Notes

- **identity** (matches=0/4): leave the grid unchanged; zeros persist so symmetry never emerges.
- **mirror_nonzero** (matches=0/4): copy colours across the main diagonal when a counterpart exists; cells with zero/zero pairs remain blank and break the pattern.
- **row_match** (matches=4/4): iteratively plug gaps with other rows that agree on visible cells (and, via the transpose pass, matching columns); this already reconstructs the full symmetric mosaic.
- **row_col_match** (matches=4/4): same completion but also considering column candidates during the row phase; settled on this variant for the solver, then enforced diagonal mirroring to tidy any leftovers.

The final row_col_match pipeline generates a symmetric 30×30 grid on the test input, repeating the colour palette seen in training and extending every partial row/column into a consistent counterpart.

## DSL Structure
- **Typed operations**
  - `fillIncompleteLines : Grid -> (Grid, Bool)` — fill each row’s zeros using matching rows or columns that agree on visible entries.
  - `iterateCompletion : Grid -> Grid` — alternate between row and column completion until no further changes occur.
  - `mirrorDiagonalZeros : Grid -> Grid` — copy non-zero values across the main diagonal to eliminate remaining zeros.
- **Solver summary**: "Iteratively complete rows and columns by borrowing matching lines, repeat until stable, and mirror any leftover zeros across the diagonal."
