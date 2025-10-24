# Task 71e489b6 Abstractions

- **identity** – return the grid unchanged; 0/3 train matches (first failure on train[0]).
- **majority_cleanup** – flip 1s with ≥3 zero neighbours to 0; still 0/3 because no highlighting is produced.
- **tip_halo** – detect zero tips and draw guarded 7 halos plus the zero-majority cleanup; 3/3 train matches with no regressions, and the test predictions show the expected tip-centred halos without artefacts.

## DSL Structure
- **Typed operations**
  - `countZeroNeighbours : Grid -> Matrix Int` — precompute, for each cell, the number of adjacent zeros.
  - `pruneLonelyOnes : Grid × Matrix Int -> Grid` — turn colour-1 cells with at least three zero neighbours into zeros.
  - `collectZeroTips : Grid × Matrix Int -> Set Cell` — find zero cells whose zero-degree is ≤1 within each component.
  - `paintTipHalos : Grid × Grid × Set Cell × Matrix Int -> Grid` — given the original grid and the cleaned base canvas, paint guarded 7-halo patterns for each tip (and its paired zero) while respecting adjacency counts.
- **Solver summary**: "Count zero neighbours, prune isolated 1s, gather tip cells in the zero components, and paint guarded 7 halos around each tip."

## Lambda Representation

```python
def solve_71e489b6(grid: Grid) -> Grid:
    zero_counts = countZeroNeighbours(grid)
    cleaned = pruneLonelyOnes(grid, zero_counts)
    tips = collectZeroTips(grid, zero_counts)
    return paintTipHalos(grid, cleaned, tips, zero_counts)
```
