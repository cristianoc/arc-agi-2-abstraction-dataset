# Task 800d221b – Abstraction Notes

- **column_threshold** – Simple left/right split based on normalised column index (`col_norm < 0.45 → left`, `> 0.55 → right`). Ignores interior structure, so it recolours most pixels incorrectly (train 0/3).
- **distance_threshold** – Adds a distance-to-nearest-anchor check (`min(dist) < 4`) before colouring, but still only examines naïve column halves. It fails on all training cases (0/3) because the central “neutral” core needs more nuanced handling.
- **hybrid_knn** – Final solver: combines lightweight heuristics for obvious edge columns with a kNN on features (column/row position and normalised seed distances) learned from the embedded training set. Achieves 3/3 on training and generalises to the held-out test grid.

## DSL Structure
- **Typed operations**
  - `extractTargetComponents : Grid -> (Color, Color, List Component)` — detect the transition colour, dominant background, and connected components to recolour.
  - `identifyFringeColours : Grid × List Component -> (Color, Color)` — analyse adjacency to pick the left/right anchor colours around each component.
  - `computeFeatures : Component × (Color, Color) -> List Feature` — build per-cell feature vectors (normalised positions, seed distances, heuristics).
  - `classifyCells : List Feature -> List Label` — apply rule-based shortcuts and the embedded kNN to label cells as `left`, `right`, or `mid`.
  - `repaintByLabels : Grid × Component × List Label × (Color, Color, Color) -> Grid` — recolour component cells according to their labels while preserving mid-cells.
- **Solver summary**: "Extract transition components, choose flank colours, compute feature vectors for each component cell, classify them via heuristics + kNN, and repaint according to the predicted labels."
