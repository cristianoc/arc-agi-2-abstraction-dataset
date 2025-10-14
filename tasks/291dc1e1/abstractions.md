- `row_ltr`: treat wide grids with row-wise left→right segment interleaving. Solves 2/4 train cases before stalling on the tall example that needs column logic.
- `column_ltr`: transpose tall grids but keep column order left→right; mismatched ordering leaves 0/4 train cases solved.
- `directional`: hybrid that detects tall grids, reverses column order, and flips segment direction when the right edge is anchored; solves 4/4 train cases and feeds the final solver (test output shape 18×8).

## DSL Structure
- **Typed operations**
  - `maybeTranspose : Grid -> (Grid, Bool)` — transpose tall grids so segment weaving runs left-to-right.
  - `trimHeader : Grid -> Grid` — remove the header column of colours {0,1,2} before segment extraction.
  - `extractSegments : Row -> List Segment` — capture non-header segments separated by background.
  - `groupRows : List Bool -> List Range` — group rows into contiguous blocks that contain segments.
  - `weaveSegments : List Range × List[List Segment] × Int -> Grid` — order rows (reversing when anchored), interleave segments positionally, and inflate them to the target width.
  - `restoreOrientation : Grid × Bool -> Grid` — transpose the woven grid back when the original input was tall.
- **Solver summary**: "Transpose when needed, strip the header column, collect segments per row, weave them position by position across contiguous row groups (reversing when anchored), and inflate to the max width."

## Lambda Representation

```python
def solve_291dc1e1(grid: Grid) -> Grid:
    oriented, transposed = maybeTranspose(grid)
    cores = trimHeader(oriented)
    segments_per_row = [extractSegments(row) for row in cores]
    groups = groupRows([bool(segs) for segs in segments_per_row])
    max_width = max((len(seg) for segs in segments_per_row for seg in segs), default=0)
    woven = weaveSegments(groups, segments_per_row, max_width)
    return restoreOrientation(woven, transposed)
```
