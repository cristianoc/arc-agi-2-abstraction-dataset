# Task 2c181942 – Abstraction Notes

- **identity** – Baseline copy-through; leaves all artefacts in place so it fails immediately on every train example (0/3).
- **axis-cross-no-shift** – Packs dominant colours around the detected vertical axis but skips the top-row widening tweak; succeeds on 2/3 trains and dies on the sample whose top arm needs to flare outward.
- **axis-cross-final** – Adds the selective top-row shift plus refined left/right arm placement; matches all train cases (3/3) and yields the submitted test prediction above.

## DSL Structure
- **Typed operations**
  - `gatherColorStats : Grid -> Stats` — collect per-colour counts, row lists, column lists, and cell sets.
  - `detectAxis : Grid -> (AxisColumn, AxisCounts, AxisCells)` — locate the best 2-column axis and tally colours appearing there.
  - `selectVerticalColors : Stats × AxisCounts -> (TopColor, BottomColor)` — choose the colours that occupy the axis vertically, ordered by mean row.
  - `fillVerticalArms : Grid × (TopColor, BottomColor) × Axis -> Grid` — build the vertical arms around the axis and apply the top flare adjustment.
  - `placeHorizontalArms : Grid × Stats × Axis -> Grid` — pick horizontal colours by centroid offsets and paint their row counts left/right of the axis.
- **Solver summary**: "Analyse the colour stats, detect the axis, fill vertical arms (with top flare adjustment), then choose horizontal colours by centroid and paint their arms around the axis."
