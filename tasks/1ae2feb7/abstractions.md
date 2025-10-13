# ARC task 1ae2feb7 – Abstraction Experiments

- `identity`: Baseline copy of the input grid; leaves the right region empty so it fails on every training case (0/3).
- `repeat_last_nonzero_block`: Projects only the block adjacent to the barrier and spaces repeats by its length; works for simple rows but misses additional colors (2/3, first fail train[1]).
- `repeat_all_blocks`: Sweeps non-zero blocks from right to left, repeating each across the barrier while preserving nearer-block precedence; matches all training examples (3/3) and underpins the final solver.

## DSL Structure
- **Typed operations**
  - `collectSegments : Row -> List Segment` — find colour segments to the left of the barrier column.
  - `extendSegment : Row × Segment -> Row` — repeat each segment to the right of the barrier at its own length spacing.
- **Solver summary**: "For each row, record the colour segments before the barrier and repeat each segment to the right across the barrier at matching spacing."
