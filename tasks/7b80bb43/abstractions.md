# Task 7b80bb43 Abstractions

- **identity**: Baseline copy of the input; leaves gaps and spurious pixels untouched. Performance 0/2 on train.
- **column_snap_v0**: First attempt snapping dominant columns/rows without support checks; overfills columns and still misses long horizontal bridge. Performance 0/2 on train (fails train[0] and train[1]).
- **column_snap_refined**: Final solver with support-aware vertical bridging, pivot-row guarded horizontal fills, and selective singleton retention; solves both training grids (2/2). Test grid inspected manually via solver.

## DSL Structure
- **Typed operations**
  - `computeForegroundMask : Grid -> (Color, Color, Matrix Bool)` — identify the dominant foreground colour, the background colour, and build a mask of its cells.
  - `selectKeyColumns : Matrix Bool -> List Int` — pick columns whose foreground counts exceed dynamic thresholds (with fallbacks when sparse).
  - `buildColumnMasks : Matrix Bool × List Int -> ColumnMasks` — keep or bridge vertical runs in each key column using support tests and gap limits.
  - `extendRows : Matrix Bool × ColumnMasks × List Int × Color × Color -> Grid` — merge vertical masks with horizontal row segments, bridge short gaps on the pivot row when supported by key columns, and paint the regularised structure using the provided colours.
- **Solver summary**: "Compute the foreground mask, choose key columns, refine column masks with gap bridging, then extend rows (including guarded bridges) to produce the cleaned linework."

## Lambda Representation

```python
def solve_7b80bb43(grid: Grid) -> Grid:
    foreground_color, background_color, mask = computeForegroundMask(grid)
    key_columns = selectKeyColumns(mask)
    column_masks = buildColumnMasks(mask, key_columns)
    return extendRows(mask, column_masks, key_columns, foreground_color, background_color)
```
