# Task 409aa875 Abstraction Notes

- **identity** – Baseline mirror of the input (0/3 train). Useful only to confirm that every case genuinely needs reasoning beyond copy-through.
- **centroid-no-norm** – Lifts 8-connected components by five rows and drops a 9 on their horizontal centroid without re-anchoring columns (2/3 train, first fail train[2] where components live far to the right).
- **centroid-global-shift** – Same lifting scheme, but columns are normalised by each band’s minimum and odd-sized bands highlight the middle marker with colour 1 while recolouring any overlapped component (3/3 train; this is the final hybrid committed as `solve_409aa875`).

## DSL Structure
- **Typed operations**
  - `groupByBand : Grid -> List Band` — cluster components that share the same source row band.
  - `liftBands : List Band -> List Band` — raise each band by the prescribed offset while tracking component centroids.
  - `normaliseBandColumns : List Band -> List Band` — reanchor lifted components so their columns start at the band’s minimum x-coordinate.
  - `markBandCentroids : Grid × List Band -> Grid` — paint the lifted bands back into the canvas and drop the centroid marker (colour 1) for odd-sized bands.
- **Solver summary**: "Group components into bands, lift the bands upward, normalise their columns, then render the lifted bands and mark odd-band centroids."

## Lambda Representation

```python
def solve_409aa875(grid: Grid) -> Grid:
    bands = groupByBand(grid)
    lifted = liftBands(bands)
    normalised = normaliseBandColumns(lifted)
    return markBandCentroids(grid, normalised)
```
