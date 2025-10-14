# e12f9a14 Abstractions

- identity — copies the grid verbatim; matches 0/4 train puzzles (first failure train[0]); used only as sanity baseline.
- union — paints the union of all digit offsets gated only by background; also 0/4 (first failure train[0]) because it overdraws neighbouring glyphs.
- variants — collision-aware selection among per-digit templates (solver in `analysis/arc2_samples/e12f9a14.py`); 4/4 train, test predictions render clean digits for seeds {2,3,4,6,7,9}, no arc-gen samples provided.

Harness: `python analysis/taske12f9a14_abstractions.py`.

## DSL Structure
- **Typed operations**
  - `extractComponents : Grid -> List Component` — enumerate 4-connected components with colour metadata.
  - `filterSeedBlocks : List Component × Color -> List Seed` — keep only 2×2 seed components against the background colour.
  - `selectDigitVariant : Seed -> Optional List Offset` — choose the best collision-free template offsets from the colour’s variant library.
  - `paintDigitTemplate : Grid × Seed × List Offset -> Grid` — fill the seed footprint plus selected offsets while preserving existing structure.
- **Solver summary**: "Extract components, keep the 2×2 seeds, choose the best digit variant for each seed, and paint the variant offsets onto the grid."
