# ARC d8e07eb2 Abstractions

- **Identity baseline** – simply copies the grid; unsurprisingly keeps all errors (0/5 train).
- **Row-match highlight** – lights up the third digit row when the top digits reuse `{0,1,6,7}`; captures the dedicated training pair but misses the other regimes (1/5 train).
- **Row-or-column highlight** – adds a column fingerprint test so `{0,1,2,6}` triggers a vertical stripe; improves coverage to 2/5 but still fails for mixed colour sets (train first failure at index 2).
- **Priority fallback (final)** – keeps the row/column rules, then assigns the remaining colours via a priority order of 5×5 digit blocks and paints the outer background depending on whether both 0 and 1 appear in the header; 5/5 train. On test grids it highlights column 3 for `{0,1,2,9}` and the `(2,0),(2,0),(3,1),(3,2)` blocks for `{2,5,7}`, matching the observed structure.

The final solver is `analysis.arc2_samples.d8e07eb2.solve_d8e07eb2` and corresponds to the **priority fallback** abstraction.

## DSL Structure
- **Typed operations**
  - `collectHeaderDigits : Grid -> Dict Color -> Int` — tally the colours detected across the top digit blocks.
  - `matchColumnFingerprint : Dict Color -> Optional List (RowIdx, ColIdx)` — compare the colour multiset against stored column fingerprints to pick highlight blocks.
  - `fallbackBlockSelection : Dict Color -> List (RowIdx, ColIdx)` — use the priority ordering when no fingerprint matches the observed counts.
  - `renderHighlights : Grid × List (RowIdx, ColIdx) × Bool -> Grid` — paint the chosen 5×5 blocks, optionally highlight the top band, and set the bottom background depending on the header colours.
- **Solver summary**: "Count header digits, match fingerprints to select highlight blocks (falling back to the priority list), then render those blocks while adjusting the top and bottom bands."
