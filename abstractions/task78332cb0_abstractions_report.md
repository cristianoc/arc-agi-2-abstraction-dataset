Task 78332cb0 Abstraction Report
--------------------------------

- `row_major_stack`: Segment tiles with the separator color and stack them in row-major order without reorientation; hits 1/3 train cases because blocks need rotation before stacking.
- `rotated_cycle`: Rotate the block grid clockwise, cycle the starting tile, and reassemble with separator rows/columns; matches 3/3 train cases and produces structured outputs on both test grids (tall stack for test[0], wide strip for test[1]).

Final pipeline: use `rotated_cycle`, which respects tile orientation and separator placement; manual inspection of its two test predictions shows the digit tiles preserved with clean 6-lines between them.
