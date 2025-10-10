# Task 7b3084d4 Abstraction Notes

- **identity** – Baseline that returns the input grid; unsurprisingly 0/3 train matches because the task requires compressing components into a compact square summary.
- **first_fit** – Greedy row-major packing without backtracking; it jams on train[0] and train[1], leaving shapes misaligned (0/3).
- **perimeter_dfs** – The perimeter-guided DFS from the solver keeps every component shape (3/3 train). Harness preview shows the 14×14 test tiling preserves the 7/8/3/2 regions, so we kept this refinement.
