# 89565ca0 Abstractions

- **naive_stripe** — mapped each color's bottommost stripe winner directly to prefix length with no fallback. Failed all 3/3 training tasks (first failure train[0]) because top-level colors lost rank when they never dominated a stripe.
- **refined_stripe** — introduced filler-aware dominance, area-ranked fallback for non-dominant colors, and remapped stripe indices (0→2, 1/2→3, 3→4). Achieved 3/3 training matches and produced coherent 4-column summaries on the evaluation input.

Final pipeline uses `refined_stripe`, which matches the production solver and yields plausible outputs on the held-out test grid.

## DSL Structure
- **Typed operations**
  - `tallyColours : Grid -> Dict Color -> Stats` — compute per-colour areas and component counts to identify the filler colour.
  - `computeStripeDominators : Grid × Dict Stats -> List Optional Color` — for each row stripe, select a dominant colour using filler-aware tie-breaking.
  - `derivePrefixLengths : Dict Stats × List Optional Color -> Dict Color -> Int` — map colours to histogram prefix lengths based on stripe dominance and fallback ordering.
  - `renderSummaryRows : Dict Color -> Int × Color -> Grid` — build the 4-column summary rows using the computed prefix lengths and filler colour.
- **Solver summary**: "Tally colour statistics, determine stripe dominators with filler-aware rules, convert those dominators into prefix lengths, and render the summary rows."
