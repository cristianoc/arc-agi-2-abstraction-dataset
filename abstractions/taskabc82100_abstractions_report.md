# Task abc82100 – Abstraction Notes

- **identity** – simple passthrough used to confirm baseline; fails on every train case because no transformation is applied.
- **knn** – 1-nearest-neighbour classifier over hand-crafted row/column features (parities, distances to non-zero bands, local colours). Matches all train/test examples and is used as the final solver.
