# Task 7b80bb43 Abstractions

- **identity**: Baseline copy of the input; leaves gaps and spurious pixels untouched. Performance 0/2 on train.
- **column_snap_v0**: First attempt snapping dominant columns/rows without support checks; overfills columns and still misses long horizontal bridge. Performance 0/2 on train (fails train[0] and train[1]).
- **column_snap_refined**: Final solver with support-aware vertical bridging, pivot-row guarded horizontal fills, and selective singleton retention; solves both training grids (2/2). Test grid inspected manually via solver.

## DSL Structure
- **Typed operations**
  - `computeForegroundMask : Grid -> (Color, Matrix Bool)` — identify the dominant foreground colour and build a mask of its cells.
  - `selectKeyColumns : Matrix Bool -> List Int` — pick columns whose foreground counts exceed dynamic thresholds (with fallbacks when sparse).
  - `buildColumnMasks : Matrix Bool × List Int -> Dict Int -> List Bool` — keep or bridge vertical runs in each key column using support tests and gap limits.
  - `extendRows : Matrix Bool × Dict Int -> List Bool -> Grid` — merge vertical masks with horizontal row segments, bridge short gaps on the pivot row, and paint the regularised structure.
- **Solver summary**: "Compute the foreground mask, choose key columns, refine column masks with gap bridging, then extend rows (including guarded bridges) to produce the cleaned linework."
