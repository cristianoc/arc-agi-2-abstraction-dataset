# Task e87109e9 – Abstraction Notes

- **identity** – Used as sanity baseline; leaves grid unchanged and scores 0/3 on train.
- **union_template** – Applied per-digit column unions derived from train data; insufficient granularity and still 0/3 on train.
- **nearest_neighbor** – Matches each block to the closest training mask in digit space (16×6 binary target mask) and overlays the recorded diff; 3/3 on train and selected as final solver.

Harness: `python analysis/taske87109e9_abstractions.py` prints per-abstraction train/test success and first-failure indices (test is `n/a` because ARC evaluation lacks labels).
