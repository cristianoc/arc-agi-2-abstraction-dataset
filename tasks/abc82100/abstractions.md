# Task abc82100 – Abstraction Notes

- **identity** – simple passthrough used to confirm baseline; fails on every train case because no transformation is applied.
- **knn** – 1-nearest-neighbour classifier over hand-crafted row/column features (parities, distances to non-zero bands, local colours). Matches all train/test examples and is used as the final solver.

## DSL Structure
- **Typed operations**
  - `loadTrainingFeatures : Unit -> List (FeatureVector, Color)` — retrieve the cached feature vectors derived from the training pairs.
  - `precomputeAxisStats : Grid -> (List RowInfo, List ColInfo, Bounds)` — gather per-row/per-column metadata (edge colours, categories, non-zero counts, bounding box).
  - `encodeCellFeatures : Grid × RowInfo × ColInfo × Bounds -> FeatureVector` — turn a cell into the mixed numeric/categorical feature tuple (normalised position, categories, parity, neighbouring colours).
  - `nearestColour : FeatureVector × List (FeatureVector, Color) -> Color` — evaluate the mixed-distance 1-NN classifier to pick the output colour.
- **Solver summary**: "Load training feature vectors, precompute row/column stats, encode each output cell into feature space, and classify it with the 1-NN distance."

## Lambda Representation

```python
def solve_abc82100(grid: Grid) -> Grid:
    samples = loadTrainingFeatures(None)
    row_stats, col_stats, bounds = precomputeAxisStats(grid)

    def classify_cell(y: int, x: int) -> Color:
        features = encodeCellFeatures(grid, row_stats[y], col_stats[x], bounds)
        return nearestColour(features, samples)

    height = len(grid)
    width = len(grid[0])
    return [
        [classify_cell(y, x) for x in range(width)]
        for y in range(height)
    ]
```
