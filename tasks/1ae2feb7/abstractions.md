# ARC task 1ae2feb7 – Abstraction Experiments

- `identity`: Baseline copy of the input grid; leaves the right region empty so it fails on every training case (0/3).
- `repeat_last_nonzero_block`: Projects only the block adjacent to the barrier and spaces repeats by its length; works for simple rows but misses additional colors (2/3, first fail train[1]).
- `repeat_all_blocks`: Sweeps non-zero blocks from right to left, repeating each across the barrier while preserving nearer-block precedence; matches all training examples (3/3) and underpins the final solver.
