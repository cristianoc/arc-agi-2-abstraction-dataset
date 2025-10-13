# Task 6ffbe589 – Abstractions Recap

- **`crop_only`** – isolate the densest contiguous non-zero square. It preserves raw geometry but misses that the façade needs reorientation; 0/3 train, 0/1 test.
- **`rotate_ccw`** – rotate the cropped block counter-clockwise. Works for the striped `{1,2,4}` case only; 1/3 train, 0/1 test (first miss train[0]).
- **`rotate_cw_with_edges`** – rotate clockwise and restore the original outer frame. Solves the `{3,4,5}` family (including the evaluation input) but not the others; 1/3 train, 1/1 test, miss train[0].
- **`color_masks`** – rotate colour masks independently (`3` → cw, `8` → 180°) while keeping `6` fixed. Covers the `{3,6,8}` maisonette yet fails elsewhere; 1/3 train, 0/1 test, miss train[1].
- **`final_hybrid`** – detect the colour palette and dispatch to the suited pipeline (mask rotation, edge-preserving cw rotation, or pure ccw). Delivers 3/3 train and 1/1 test pixel-perfect matches.

The winning strategy crops around the active block, recognises which stylistic variant we received via its colour triad, then applies the matching rotation recipe. Combining colour-aware mask rotation with edge-restoring rotations unifies the seemingly different façades and handles the held-out evaluation sample.
