- `middle_segment`: Keeps the literal middle stripe between border columns; misses the outlier stripe on train[0], so it fails immediately (0/2 train).
- `unique_segment`: Chooses the stripe pattern that appears least often per row; matches both training examples (2/2 train) but balloons to width 8 on test[0], revealing that the latent 2-D block structure matters.
- `unique_block_column`: Segments the grid into border-delimited blocks and keeps the unique block per block-row; passes all training examples (2/2 train) and yields plausible 6×6 interiors on test inputs.

Final refinement: Implement the `unique_block_column` abstraction in the solver by detecting non-border block runs and copying only the odd block out per block-row while restoring outer borders.

## DSL Structure
- **Typed operations**
  - `detectBorders : Grid -> BorderSpec` — capture the constant border colours and their thickness.
  - `partitionIntoBlocks : Grid × BorderSpec -> List BlockRow` — split the interior into block rows separated by border columns.
  - `selectUniqueBlockPerRow : List BlockRow -> List Block` — choose the block whose pattern is unique within each block row.
  - `renderUniqueBlocks : Grid × BorderSpec × List Block -> Grid` — reconstruct the grid using the original borders while writing back only the selected unique blocks.
- **Solver summary**: "Detect the border specification, partition the interior into bordered block rows, keep the unique block per row, and render those blocks with the original borders restored."

## Lambda Representation

```python
def solve_38007db0(grid: Grid) -> Grid:
    border_spec = detectBorders(grid)
    block_rows = partitionIntoBlocks(grid, border_spec)
    unique_blocks = selectUniqueBlockPerRow(block_rows)
    return renderUniqueBlocks(grid, border_spec, unique_blocks)
```
