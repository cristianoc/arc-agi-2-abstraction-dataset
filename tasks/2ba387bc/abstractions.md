# 2ba387bc Abstraction Notes

- `identity`: returned the input unchanged; 0/4 train matches, failed first on train[0].
- `scan_pairing`: paired components strictly by scan order; 0/4 train matches, failed first on train[0].
- `hollow_vs_solid`: sorted hollows and solids separately, then zipped them into canonical 4×4 pair blocks; 4/4 train matches with no failures and produces the test prediction `[[4,4,4,4,6,6,6,6], …]` shown in the evaluation harness.

Final solver: `hollow_vs_solid` abstraction — converts each hollow component to the left sub-block, each solid to the right sub-block, pairing by ascending top-left position and padding leftovers with zeros. This reproduces every training output and yields the plausible test arrangement of the four component pairs.

## DSL Structure
- **Typed operations**
  - `extractComponents : Grid -> List Component` — gather components with metadata (colour, bounding box, hollowness).
  - `partitionByHollowness : List Component -> (List Component, List Component)` — split components into hollow vs. solid lists.
  - `resampleToFour : Pattern -> Grid4x4` — resize each component pattern to a 4×4 block via nearest-neighbour sampling.
  - `packPairs : List Grid4x4 × List Grid4x4 -> Grid` — zip hollow/solid blocks (padding with zeros) and stitch them side by side.
- **Solver summary**: "Extract components, split into hollow vs. solid, resample each to 4×4, and stitch the paired blocks horizontally."
