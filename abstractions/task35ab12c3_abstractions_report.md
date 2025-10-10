# Task 35ab12c3 Abstractions

- **diag_expand**: Connected equal-color points via row/column adjacency and full diagonal chains; it reconstructed rough hulls but introduced spurious interior diagonals, failing all training cases.
- **hull_shift**: Built color hulls with conflict-aware linking, then generated singleton layers by shifting the nearest base component; solved 3/3 training grids and produced a coherent test prediction.
