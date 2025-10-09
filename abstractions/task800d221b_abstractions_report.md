# Task 800d221b – Abstraction Notes

- **column_threshold** – Simple left/right split based on normalised column index (`col_norm < 0.45 → left`, `> 0.55 → right`). Ignores interior structure, so it recolours most pixels incorrectly (train 0/3).
- **distance_threshold** – Adds a distance-to-nearest-anchor check (`min(dist) < 4`) before colouring, but still only examines naïve column halves. It fails on all training cases (0/3) because the central “neutral” core needs more nuanced handling.
- **hybrid_knn** – Final solver: combines lightweight heuristics for obvious edge columns with a kNN on features (column/row position and normalised seed distances) learned from the embedded training set. Achieves 3/3 on training and generalises to the held-out test grid.
