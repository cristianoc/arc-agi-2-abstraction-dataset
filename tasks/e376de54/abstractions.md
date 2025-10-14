# e376de54 Abstraction Notes

**identity** — Baseline copy of the input grid. Fails immediately on the first training puzzle (0/3) because it leaves the misaligned stripes untouched.

**median_line_alignment** — Scores each orientation (rows, columns, diagonals) by how strongly coloured cells cluster, aligns the family along the best-scoring direction, and rebuilds every line to match the median line’s footprint. Achieves 3/3 on train with no failures and produces the expected structured prediction on test.

Final solver: reuse of `median_line_alignment` as implemented in `analysis/arc2_samples/e376de54.py`.

## DSL Structure
- **Typed operations**
  - `collectColoredCells : Grid -> (Color, List Cell)` — determine the background colour and list all coloured cells.
  - `scoreOrientations : List Cell -> (Orientation, LineGroups)` — evaluate row/column/diagonal groupings, returning the best orientation and all line families.
  - `extractMedianPattern : Orientation × LineGroups -> Pattern` — choose the median line within the winning orientation and capture its footprint.
  - `realignLines : Grid × Orientation × Pattern -> Grid` — rebuild each line so it matches the median footprint, clearing stray cells.
- **Solver summary**: "Collect coloured cells, score candidate orientations, take the median line’s footprint, then realign every line to that pattern."

## Lambda Representation

```python
def solve_e376de54(grid: Grid) -> Grid:
    _, coloured_cells = collectColoredCells(grid)
    orientation, line_groups = scoreOrientations(coloured_cells)
    pattern = extractMedianPattern(orientation, line_groups)
    return realignLines(grid, orientation, pattern)
```
