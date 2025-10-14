identity — kept the grid unchanged to confirm the dataset needed structure inference; scored 0/4 on train with first failure at train[0], but provided baseline shapes for comparison.

segment_tiling — replicated the color‑4 stencil across connected color‑3 components and filled with the final two palette colors; achieved 4/4 on train and produces 3 predicted shapes on test (5x2, 3x11, etc.) that align with the observed tiling geometry.

Final solver uses the segment_tiling abstraction directly; no hybrid was required beyond mapping the two delimiter segments to colors from the final bands, and it generalizes cleanly to the provided test inputs.

## DSL Structure
- **Typed operations**
  - `findFullLines : Grid -> (List RowIndex, List ColIndex)` — detect all-ones rows or columns that act as separators.
  - `extractSegments : Grid × (List RowIndex, List ColIndex) -> (List Segment, List Segment)` — slice the grid into ordered row/column segments delimited by the full lines.
  - `summarisePattern : Segment × Color -> Pattern` — compute the bounding 4-stencil and component counts needed to reproduce the motif.
  - `rebuildByOrientation : Pattern × Segment × Segment -> Grid` — tile the pattern horizontally or vertically using the segment metadata and dominant colours.
- **Solver summary**: "Detect the separator lines, extract the four guiding segments, summarise the colour-4 stencil and component counts, then rebuild the grid in the resolved orientation using those summaries."
