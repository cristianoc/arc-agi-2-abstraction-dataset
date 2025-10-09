# Task 7b80bb43 Abstractions

- **identity**: Baseline copy of the input; leaves gaps and spurious pixels untouched. Performance 0/2 on train.
- **column_snap_v0**: First attempt snapping dominant columns/rows without support checks; overfills columns and still misses long horizontal bridge. Performance 0/2 on train (fails train[0] and train[1]).
- **column_snap_refined**: Final solver with support-aware vertical bridging, pivot-row guarded horizontal fills, and selective singleton retention; solves both training grids (2/2). Test grid inspected manually via solver.
