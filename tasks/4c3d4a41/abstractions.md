# Task 4c3d4a41 Abstractions

- `overlay_only`: zeroes the left wedge and mirrors its 5s onto the right via a fixed offset. It misses the upward shift of the right-side digits (train 0/2).
- `copy_second_row_then_overlay`: additionally copies the third row's right block into the second row before mirroring, fixing the first training case but failing when deeper rows introduce new colors (train 1/2).
- `shift_rows_with_left_presence`: copies each right block upward wherever the source row still carries left-wedge 5s, then mirrors the wedge; this matches both training examples (2/2) and is the final solver.

The final strategy layers the selective upward copy with the mirroring step, producing the published solver in `arc2_samples/4c3d4a41.py`.

## DSL Structure
- **Typed operations**
  - `locateLeftWedge : Grid -> Set Row` — identify rows containing the left wedge colour `5`.
  - `extractRightBlocks : Grid × Set Row -> Dict[Row, Block]` — gather the right-hand blocks that correspond to each wedge row.
  - `shiftBlocksUpwards : Grid × Dict[Row, Block] -> Grid` — write the right-hand blocks one row above while the source rows still contain wedge cells.
  - `mirrorWedge : Grid × Set Row -> Grid` — mirror the left wedge onto the right side after the upward shifts.
- **Solver summary**: "Find the wedge rows, extract and shift their right-side blocks upward when wedge cells persist, then mirror the wedge to finish the overlay."

## Lambda Representation

```python
def solve_4c3d4a41(grid: Grid) -> Grid:
    wedge_rows = locateLeftWedge(grid)
    blocks = extractRightBlocks(grid, wedge_rows)
    shifted = shiftBlocksUpwards(grid, blocks)
    return mirrorWedge(shifted, wedge_rows)
```
