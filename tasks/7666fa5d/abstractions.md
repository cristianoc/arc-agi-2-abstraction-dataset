# ARC Task 7666fa5d – Abstraction Notes

- **identity** – Copy of the input; useful only as a baseline (0/2 train).
- **uv_box** – Filled a trimmed rectangle in the `(r+c, c-r)` plane. It captured the overall diamond trend but still flooded the top rows (0/2 train, same first failure as baseline).
- **component_lerp** – Interpolated min/max offsets between adjacent diagonal components. Better coverage yet still leaked above the guide dots (0/2 train).
- **component_corridor** – Final solver. For each background cell we require a guiding component on both the lower-left and upper-right sides of the diagonal. This brackets the corridor perfectly (2/2 train) and generalises cleanly to the test layout.

`component_corridor` is the deployed solution; its prediction on the held-out test grid matches the qualitative expectation (the corridor between the 9-diagonals is filled with 2s only where both sides are present).
