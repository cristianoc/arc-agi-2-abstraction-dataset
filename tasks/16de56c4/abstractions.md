# Abstractions for ARC task 16de56c4

- **identity** – simple copier used to verify dataset format. `train: 0/3` (first failure at train[0]); produced 2 test predictions.
- **row_rule** – propagates the rightmost color backwards using row-local arithmetic spacing. `train: 1/3` (first failure at train[1]); produced 2 test predictions.
- **column_rule** – vertical extrapolation driven by repeated column seeds. `train: 2/3` (first failure at train[0]); produced 2 test predictions.
- **row_then_column** – apply the row scaffold followed by the column extrapolator; this hybrid matches every training case (`train: 3/3`) and yields consistent test predictions.

The final solver adopts the `row_then_column` pipeline: first extend structured progressions within each row (only when the support is reliable), then lift columnar sequences to finish tiling the grid.

## DSL Structure
- **Typed operations**
  - `applyRowRule : Grid -> Grid` — extend colours along each row using gcd-based spacing from the original grid.
  - `applyColumnRule : Grid × Grid -> Grid` — extend colours along each column, referencing the original grid to guard conflicts.
- **Solver summary**: "Extend rows with the stride rule, then extend columns with the column rule while consulting the original grid for guards."

## Lambda Representation

```python
def solve_16de56c4(grid: Grid) -> Grid:
    after_rows = applyRowRule(grid)
    return applyColumnRule(after_rows, grid)
``` 
