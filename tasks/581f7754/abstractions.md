# Task 581f7754 Abstractions

- **identity** – pass-through baseline that keeps the grid unchanged; failed all train cases (0/3, first failure train[0]).
- **column_anchor** – translates connected components so each anchor colour lies on a common column but skips row refinement; solved 2/3 train cases (first failure train[1]).
- **full_alignment** – column anchoring plus row-based compression toward anchor rows, matching all train samples (3/3) and producing the delivered test outputs.

## DSL Structure
- **Typed operations**
  - `groupByAnchorColor : Grid -> Dict Color -> List Component` — collect components keyed by their anchor colour.
  - `alignColumnsToAnchor : Dict Color -> List Component -> Dict Color -> List Component` — translate each group so anchors share a common column.
  - `compressRowsTowardAnchor : Dict Color -> List Component -> Dict Color -> List Component` — collapse rows within each group toward the designated anchor row.
  - `renderAlignedComponents : Grid × Dict Color -> List Component -> Grid` — draw the aligned and compressed components back onto the canvas.
- **Solver summary**: "Group components by anchor colour, align their columns, compress rows toward the anchors, and render the aligned components."
