# Abstractions for b6f77b65

- **identity** – left the grid untouched; matched 1/5 train cases (fails first at train[1]), useful only as a baseline sanity check.
- **segment_lookup_v0** – template lookup with the misaligned `(2,'adf','e')` pattern; matched 4/5 train grids, first failure at train[2] due to the downward-shifted 5/7 bands.
- **segment_lookup_v1** – corrected template alignment; matched 5/5 train grids and produces consistent outputs for both test inputs.
- **solver** – uses the same corrected templates as the shipping solver; serves as the final refinement that passes all observed cases.

The final approach is the corrected segment template lookup (segment_lookup_v1 / solver), which aligns the `(2,'adf','e')` digit template with the observed target and reproduces every training example while yielding plausible completions for the test grids.

## DSL Structure
- **Typed operations**
  - `readKeyLetter : Grid -> Optional SegmentId` — inspect the top-left cell to recover the global key letter for digit lookups.
  - `segmentKeyForDigit : Grid × Int -> SegmentKey` — map the colours present in each 3-column digit slice to their segment-letter signature.
  - `lookupDigitTemplate : Int × SegmentKey × Optional SegmentId -> Grid` — fetch the precomputed 12×3 template for the digit, falling back to the observed slice when missing.
  - `assembleDigits : List Grid -> Grid` — concatenate the four digit templates horizontally to produce the final output.
- **Solver summary**: "Read the key letter, derive segment signatures for each digit slice, look up the corrected templates (with fallback), and stitch the templates into the output grid."
