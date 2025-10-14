# Task 62593bfd – Abstraction Notes

- **median_split**: classified each color by comparing its topmost row to the median across colors, then pushed groups to the nearest edge. It cleared the first train puzzle but misclassified the richer second example, so it does not generalise.
- **component_overlap**: compared individual components that share columns and moved the larger one upward. This matches both training outputs but is unstable—when colors have multiple shards in the same columns (e.g., test inputs) it produces conflicting shifts.
- **aggregated_overlap**: aggregates column counts per color before deciding dominance, then resolves leftovers by median min-row placement. This keeps column order, avoids shard conflicts, and matches all training cases; the implemented solver is the code version of this abstraction.

## DSL Structure
- **Typed operations**
  - `aggregateColumnCounts : Grid -> ColumnStats` — sum column occupancies per colour to measure overlap dominance.
  - `rankColorsByDominance : ColumnStats -> List Color` — order colours by their aggregated dominance to decide movement priorities.
  - `computeShiftTargets : Grid × List Color -> ShiftPlan` — derive target rows for each colour using dominance plus median min-row placement.
  - `applyColorShifts : Grid × ShiftPlan -> Grid` — translate each colour’s components toward its target row while preserving column order.
- **Solver summary**: "Aggregate column counts by colour, rank colours by dominance, compute per-colour shift targets, and apply those shifts to realign the components."

## Lambda Representation

```python
def solve_62593bfd(grid: Grid) -> Grid:
    column_counts = aggregateColumnCounts(grid)
    ordered_colors = rankColorsByDominance(column_counts)
    targets = computeShiftTargets(grid, ordered_colors)
    return applyColorShifts(grid, targets)
```
