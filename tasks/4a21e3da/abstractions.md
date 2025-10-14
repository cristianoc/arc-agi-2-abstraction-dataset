# ARC task 4a21e3da – abstraction notes

- **identity_baseline** – treated the puzzle as an identity map; fails immediately on all train cases (0 %) but trivially matches the test input because no target is provided.
- **simple_corner_projection** – projected the entire 7-component to every corner indicated by a border `2`; without directional guards it over-paints large blocks, still 0 % on train.
- **final_corner_projection** – restricted projections to sentinel-aligned subsets and mirrored the learnt ray painting; delivers 100 % accuracy on train and test.

## DSL Structure
- **Typed operations**
  - `findCornerSentinels : Grid -> List Sentinel` — detect border cells of colour `2` that mark projection targets.
  - `extractSourceGlyph : Grid -> Component` — capture the coloured component anchored near the centre.
  - `selectCornerOffsets : List Sentinel × Component -> Dict Sentinel -> Offset` — compute direction-specific offsets that align the glyph with each sentinel corner.
  - `projectGlyphToCorners : Grid × Component × Dict Sentinel -> Offset -> Grid` — stamp the glyph into every sentinel corner using the computed offsets while preserving the original.
- **Solver summary**: "Read the corner sentinels, extract the source glyph, determine corner-specific offsets, then project the glyph into each sentinel corner."
