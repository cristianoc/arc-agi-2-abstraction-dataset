## 67e490f4 Abstractions

- `colour_bbox`: locate the motif via the largest square colour bounding box and recolour by shape similarity. Matches 2/2 train tasks but relies on lucky alignment, so it is fragile for the evaluation grid (no labelled test targets).
- `two_colour_scan`: scan all two-colour squares and keep the one whose non-background components stay below the size threshold, then reuse the shape-matching palette. Covers 2/2 train tasks and supplies the evaluation prediction used in the solver.

Final pipeline: apply `two_colour_scan`, then recolour each motif component with the dominant matching shape colour gathered from the rest of the grid.

## DSL Structure
- **Typed operations**
  - `locateTwoColourSquare : Grid -> (Box, Color, Color)` — search for the largest square whose palette has exactly two colours and whose components fit the size thresholds.
  - `catalogueExternalShapes : Grid × Box -> Dict Shape -> Counter Color` — enumerate connected components outside the square, canonicalise their shapes, and tally their colours.
  - `classifyMotifComponents : Grid × Box × Color -> List (Shape, Cells, Category)` — segment motif components within the square and assign semantic categories (corner/edge/ring/centre) based on position.
  - `recolourMotif : List (Shape, Cells, Category) × Dict Shape -> Counter Color × Color -> Grid` — map each category to the most frequent matching colour from the external catalogue and paint the motif accordingly.
- **Solver summary**: "Find the defining two-colour square, catalogue external component shapes, classify each motif component inside the square, and recolour it with the dominant matching shape colour."
