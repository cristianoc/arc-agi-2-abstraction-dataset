# f931b4a8 Abstractions

- `cycle`: cycles unique tile rows and columns regardless of masks. Reaches 3/5 train matches (first failure train[1]) because it ignores quadrant guidance and repeats the wrong patterns.
- `seqcols_origrow`: keeps the discovered row heuristic but forces sequential columns. Improves to 4/5 train matches (first failure train[4]) yet still misses the alternating row borrowed from the full-zero band.
- `final`: augments the row selector with a fallback borrow when the full-zero signature is present and reuses sequential columns. Achieves 5/5 train matches; test outputs inherit the expected checker/striped motifs.

Key refinement was recognising that the empty zero-signature rows must alternate with the fully-missing rows hinted by the lower-right quadrant; once that borrow hook was added the simple column index cycle sufficed.

## DSL Structure
- **Typed operations**
  - `extractTileQuadrants : Grid -> (Grid, Grid, Grid)` — split the grid into half-height/half-width quadrants and compute the base tile with fallback cells.
  - `deriveRowOrder : Grid -> (List RowId, List Pattern)` — analyse zero signatures, variant orders, and borrow rules to choose the sequence of tile rows.
  - `deriveColumnOrder : Grid × List Pattern -> List ColId` — read the top-right quadrant to compute the repeating column indices.
  - `renderByIds : List Pattern × List RowId × List ColId -> Grid` — materialise the output by indexing into stored row patterns and column ids.
- **Solver summary**: "Compute the base tile from the quadrants, derive the row ids with zero-signature borrowing, derive sequential column ids, and render the grid by indexing tile rows and columns."
