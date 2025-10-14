# task dd6b8c4b – abstraction summary

- **identity** – Baseline copy of the grid used to check expectations; 0/3 train matches.
- **ring_fill** – Applies the quadrant-imbalance heuristic to paint the central ring but keeps all original 9s; 0/3 train matches because surplus 9s stay scattered.
- **balanced_relocation** – Combines ring filling with score-ranked relocation of 9s (final solver); 3/3 train matches and best qualitative fit on the test probe.

Final pipeline: use `balanced_relocation`, which first determines how many ring tiles to promote to colour 9 based on the east–west imbalance, then retires the same number of scattered 9s with the `-3*dr - |dr| + |dc| - boundary` score so the total count is preserved.

## DSL Structure
- **Typed operations**
  - `measureQuadrantImbalance : Grid -> Int` — count how many 9s sit in the east vs. west quadrants around the centre.
  - `selectRingTargets : Grid × Int -> List Cell` — choose ring cells near the centre to receive promoted 9s based on the imbalance.
  - `scoreExistingNines : Grid -> List (Score, Cell)` — rank scattered 9s using the relocation score that prefers far/right/border positions.
  - `rebalanceNines : Grid × List Cell × List (Score, Cell) -> Grid` — paint the selected ring cells with 9 and clear the lowest-scoring originals to background.
- **Solver summary**: "Measure the east–west imbalance of 9s, pick that many ring targets, rank existing 9s by relocation score, then promote ring cells and retire the lowest-ranked originals."

## Lambda Representation

```python
def solve_dd6b8c4b(grid: Grid) -> Grid:
    imbalance = measureQuadrantImbalance(grid)
    ring_targets = selectRingTargets(grid, imbalance)
    ranked = scoreExistingNines(grid)
    return rebalanceNines(grid, ring_targets, ranked)
```
