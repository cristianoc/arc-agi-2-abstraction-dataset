# faa9f03d Abstractions Report

- **noise_only** – Recolors low-frequency cells with majority neighbours; collapses stray artifacts but leaves underlying digits disconnected. Train accuracy: 0/4.
- **row_col_closure** – Adds short row/column bridges around dominant colors; improves cohesion yet still misses long-range hooks. Train accuracy: 0/4.
- **flanked_extend** – Adds flanked infill and limited row extension; recovers one training case but fails to propagate vertical spines. Train accuracy: 1/4 (first failure at train[1]).
- **final_solver** – Full pipeline from `solve_faa9f03d` combining noise removal, selective closures, flanked infill, row extensions, and tail-specific six propagation. Train accuracy: 4/4 (no failures). Test prediction shown in harness output.
