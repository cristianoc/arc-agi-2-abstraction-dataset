# ARC Task 3a25b0d8 – Abstraction Attempts

- **expanded_only** – crop to the columns/rows that contain non-background colours and pad with background. Train accuracy: 0/2 (fails immediately at train[0] by missing the required downscaled logo).
- **band_adjust** – adds the band heuristics (widening 7s, removing singleton 4s, isolating 6 rows) but stops before the final row synthesis. Train accuracy: 0/2 (train[0] still fails; train[1] mis-shapes the mid block).
- **final_solver** – full pipeline from `analysis/arc2_samples/3a25b0d8.py`, combining band adjustments with row-wise synthesis and duplication. Train accuracy: 2/2 (no failures).

Test outputs are unavailable for this evaluation split, so only training matches are reported.

## DSL Structure
- **Typed operations**
  - `identifyBands : Grid -> List Band` — crop the salient horizontal bands and capture their colour profiles.
  - `normalizeBandPatterns : List Band -> List Band` — widen/shrink band motifs (e.g., stretching 7s, removing singleton 4s) to the canonical widths.
  - `synthesiseBandRows : List Band -> List Row` — build the output bands by combining adjusted motifs with the preserved separators.
  - `duplicateBands : List Row -> Grid` — replicate selected bands to satisfy the expected row counts and assemble the final grid.
- **Solver summary**: "Extract the horizontal bands, normalise each band's motif, synthesise the rows for the adjusted bands, then duplicate the required bands to rebuild the output."

## Lambda Representation

```python
def solve_3a25b0d8(grid: Grid) -> Grid:
    bands = identifyBands(grid)
    normalized = normalizeBandPatterns(bands)
    band_rows = synthesiseBandRows(normalized)
    return duplicateBands(band_rows)
```
