- `middle_segment`: Keeps the literal middle stripe between border columns; misses the outlier stripe on train[0], so it fails immediately (0/2 train).
- `unique_segment`: Chooses the stripe pattern that appears least often per row; matches both training examples (2/2 train) but balloons to width 8 on test[0], revealing that the latent 2-D block structure matters.
- `unique_block_column`: Segments the grid into border-delimited blocks and keeps the unique block per block-row; passes all training examples (2/2 train) and yields plausible 6×6 interiors on test inputs.

Final refinement: Implement the `unique_block_column` abstraction in the solver by detecting non-border block runs and copying only the odd block out per block-row while restoring outer borders.
