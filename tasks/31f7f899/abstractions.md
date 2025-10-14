# Task 31f7f899 Abstraction Summary

- **identity** – simple copy of the input grid. Performance: 0/3 train matches; first failure at train[0].
- **sorted_stripes** – treat the dense center row as a profile, then sort the vertical spans of all non-dominant stripes from left to right. Performance: 3/3 train matches, no failures; applies cleanly to the evaluation input and produces the expected column cascade on the held-out test grid.

Final refinement: use `sorted_stripes` alone. It preserves the central backbone while redistributing stripe heights monotonically; visual inspection of the evaluation test prediction confirms the intended tapering pattern.

## DSL Structure
- **Typed operations**
  - `pinBackboneRow : Grid -> Row` — locate the anchor row whose pattern stays fixed (the dense middle stripe).
  - `collectStripeSpans : Grid × Row -> List Stripe` — extract each coloured vertical stripe with its height and column index relative to the backbone.
  - `sortStripesByHeight : List Stripe -> List Stripe` — reorder the stripe list by height while preserving colour metadata.
  - `renderSortedStripes : Grid × Row × List Stripe -> Grid` — rebuild the grid by writing stripes back in column order, keeping the backbone unchanged.
- **Solver summary**: "Detect and pin the central backbone row, collect stripe spans with heights, sort them by height, then render the stripes back alongside the untouched backbone."
