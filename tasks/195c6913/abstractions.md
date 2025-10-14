# Task 195c6913 Abstractions Report

## Abstractions

1. **identity** – baseline returning the input unchanged.
2. **anchor_rows_only** – fills only the legend-defined rows with the detected pattern without spatial propagation.
3. **full_propagation** – implements the final legend-aware row/column propagation with boundary capping (the solver).

## Performance Summary

| Abstraction | Train | Test | arc-gen | Notes |
|-------------|-------|------|---------|-------|
| identity | 0/3 | n/a | n/a | Baseline placeholder. |
| anchor_rows_only | 1/3 | n/a | n/a | Captures anchor rows but misses vertical propagation. |
| full_propagation | 3/3 | n/a | n/a | Matches all observed targets; solver used in `analysis/arc2_samples/195c6913.py`. |

The final abstraction extends the palette pattern across selected rows and columns defined by the anchor rows. The palette columns are propagated upward from the top anchor and upward from the bottom anchor (when present), inserting cap colours at the exposed boundaries to mirror the ground-truth patterns.

## DSL Structure
- **Typed operations**
  - `iterComponents : Grid -> List Component` — enumerate connected components and their cells per colour.
  - `extractPalette : List Component -> Pattern` — derive the palette order and legend cells from size/position cues.
  - `stripPalette : Grid × Pattern -> Grid` — remove palette and cap components from the working grid.
  - `locateAnchors : Grid × Pattern -> List Anchor` — find anchor rows with pattern start indices and boundaries.
  - `propagatePattern : Grid × Pattern × Anchor -> Grid` — propagate the repeating palette across anchor rows and neighbouring regions, inserting cap colours.
- **Solver summary**: "Decode the palette from legend components, clear them out, locate anchor rows, propagate the repeating pattern across anchors, and add caps where needed."

## Lambda Representation

```python
def solve_195c6913(grid: Grid) -> Grid:
    components = iterComponents(grid)
    pattern = extractPalette(components)
    result = stripPalette(grid, pattern)
    anchors = locateAnchors(result, pattern)
    
    for anchor in anchors:
        result = propagatePattern(result, pattern, anchor)
    
    return result
``` 
