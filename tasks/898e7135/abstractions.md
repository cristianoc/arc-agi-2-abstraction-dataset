# Task 898e7135 — Abstraction Experiments

- **identity** – simple copy of the input; fails immediately on train (0/2) so it cannot explain the transformation.
- **scale2** – fills holes inside the dominant-color box using area→hole ratio 4 and rescales by ×2; fits all train grids (2/2) but the assumption breaks on the evaluation instance where the ratio is 9, so it cannot generalise.
- **dynamic** – infers the upscale factor by taking the GCD of significant component areas (yielding ×2 on train, ×3 on the eval grid) before stitching colours into zero holes; matches every training example (2/2) and produces the intended structured layout for the unseen test input.

Final approach: use the dynamic abstraction (implemented in `analysis/arc2_samples/898e7135.py`), which adapts the scale factor per grid and reproduces all observed behaviours while giving a plausible test prediction.
