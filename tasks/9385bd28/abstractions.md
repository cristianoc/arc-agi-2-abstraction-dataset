# Task 9385bd28 – Abstraction Notes

- **identity** – Baseline copy of the input grid; fails all 4 train cases (0/4).
- **naive_fill** – Fills every mapped bounding box without guards; overpaints key structures and still scores 0/4 on train.
- **guarded_fill** – Adds zero-pair handling and protects unmapped colors; reaches 2/4 train matches before stumbling on mixed legends.
- **final_solver** – Incorporates zero-pair clears, legend-aware protection, and recolors pure source boxes; passes all train cases (4/4) and is used for submission.

## DSL Structure
- **Typed operations**
  - `extractLegendPairs : Grid -> LegendPairs` — read the legend rows/columns to identify zero-pair and fill-pair mappings.
  - `computeBoundingBoxes : Grid -> BoundingBoxes` — build bounding boxes for each non-legend component colour.
  - `clearZeroPairs : Grid × LegendPairs × BoundingBoxes -> Grid` — clear the interior of boxes whose source colour maps to zero.
  - `fillBoxes : Grid × LegendPairs × BoundingBoxes -> Grid` — recolour each remaining box according to its mapped target while respecting protected boxes.
- **Solver summary**: "Decode legend pairs, compute bounding boxes for source colours, clear boxes mapped to zero, and fill the remaining boxes with their target colours while protecting unmapped content."

## Lambda Representation

```python
def solve_9385bd28(grid: Grid) -> Grid:
    legend_pairs = extractLegendPairs(grid)
    boxes = computeBoundingBoxes(grid)
    cleared = clearZeroPairs(grid, legend_pairs, boxes)
    return fillBoxes(cleared, legend_pairs, boxes)
```
