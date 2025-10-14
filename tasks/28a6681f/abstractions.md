Identity baseline — kept the grid unchanged; fails immediately because the task requires moving color‑1 cells.

Fill-all gaps — painted every zero span bracketed by non-zero colors with 1; overshoots by extending the 1 block too high (fails train[0]).

Equal-boundary gaps — only filled spans whose flanking colors match; still alters upper 9/3 bands incorrectly (fails train[0]).

Bottom-greedy supply (final) — iterate candidates bottom-right first, consume top-left 1s as supply, relocate them into the gap; passes all training cases and yields plausible test output (diagonal 1 band hugging the lower-right slope).

## DSL Structure
- **Typed operations**
  - `collectSupply : Grid -> List Cell` — enumerate existing colour-1 cells sorted top-to-bottom, left-to-right.
  - `findCandidates : Grid -> List Cell` — list zero cells that sit between non-zero colours on the same row.
  - `orderCandidates : List Cell -> List Cell` — sort candidate gaps by bottom-right priority.
  - `fillCandidates : Grid × List Cell × List Cell -> (Grid, List Cell)` — relocate supply cells into candidates while recording removed sources.
  - `clearRemoved : Grid × List Cell -> Grid` — zero out the original supply positions that were moved.
- **Solver summary**: "Collect colour-1 supply cells, gather bottom-right gap candidates, relocate supply into those gaps in order, and clear the original positions."
