# e3721c99 Abstractions

- **identity** – trivial passthrough of the input grid. Serves as a baseline and fails on both training examples because none of the 5-marked regions are recoloured.
- **holes_classifier** – classify each connected component of colour 5 by counting internal holes and a couple of size heuristics; paint the component with the corresponding colour class. This solver matches both training grids (2/2) with pixel-perfect accuracy.

The final solution reuses the `holes_classifier` heuristic directly in `analysis/arc2_samples/e3721c99.py`.
