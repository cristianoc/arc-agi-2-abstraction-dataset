# 89565ca0 Abstractions

- **naive_stripe** — mapped each color's bottommost stripe winner directly to prefix length with no fallback. Failed all 3/3 training tasks (first failure train[0]) because top-level colors lost rank when they never dominated a stripe.
- **refined_stripe** — introduced filler-aware dominance, area-ranked fallback for non-dominant colors, and remapped stripe indices (0→2, 1/2→3, 3→4). Achieved 3/3 training matches and produced coherent 4-column summaries on the evaluation input.

Final pipeline uses `refined_stripe`, which matches the production solver and yields plausible outputs on the held-out test grid.

## DSL Structure
- **Typed operations**
  - `tallyColours : Grid -> ColourStats` — compute per-colour areas and component counts to identify the filler colour.
  - `computeStripeDominators : Grid × ColourStats -> StripeDominators` — for each row stripe, select a dominant colour using filler-aware tie-breaking.
  - `derivePrefixLengths : ColourStats × StripeDominators -> PrefixLengths` — map colours to histogram prefix lengths based on stripe dominance and fallback ordering.
  - `renderSummaryRows : PrefixLengths × Color -> Grid` — build the 4-column summary rows using the computed prefix lengths and filler colour.
- **Solver summary**: "Tally colour statistics, determine stripe dominators with filler-aware rules, convert those dominators into prefix lengths, and render the summary rows."

## Lambda Representation

```python
def solve_89565ca0(grid: Grid) -> Grid:
    stats = tallyColours(grid)
    stripe_dominators = computeStripeDominators(grid, stats)
    prefix_lengths = derivePrefixLengths(stats, stripe_dominators)
    return renderSummaryRows(prefix_lengths, stats.filler_colour)
```
