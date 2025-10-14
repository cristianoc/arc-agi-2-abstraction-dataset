# Task 20270e3b Abstraction Report

- **identity** – carries input through unchanged; as expected it fails immediately (0/4 train).
- **remove_rows** – drops the contiguous band of rows containing the special colour; captures only the stacked case (1/4 train).
- **vertical_overlay** – folds columns around a background separator and projects 4s from the right slice; fixes the wide-layout tasks but misses horizontal cases (2/4 train, first fail train[2]).
- **horizontal_overlay** – removes the special band and shifts the lower segment by the detected offset; succeeds on stacking tasks but not the column-fold ones (2/4 train, first fail train[0]).
- **final_solver** – selects the vertical overlay when a background column exists, otherwise applies the horizontal overlay, falling back to recolouring 7→4; this hybrid resolves all observed examples (4/4 train) and yields plausible 5×14 and 8×5 outputs on the two unseen test inputs.

The arc-gen split is empty.

## DSL Structure
- **Typed operations**
  - `verticalFold : Grid -> Optional Grid` — fold across a background column, overlaying the right block onto the left.
  - `horizontalFold : Grid -> Optional Grid` — remove the special band and glue the remaining parts with an offset.
  - `recolourFallback : Grid -> Grid` — recolour special cells to the fill colour when no folding applies.
- **Solver summary**: "Try the vertical fold; if it fails, try the horizontal glue; if both fail, recolour the special cells to the fill colour."

## Lambda Representation

```python
def solve_20270e3b(grid: Grid) -> Grid:
    result = verticalFold(grid)
    if result is not None:
        return result
    
    result = horizontalFold(grid)
    if result is not None:
        return result
    
    return recolourFallback(grid)
``` 
