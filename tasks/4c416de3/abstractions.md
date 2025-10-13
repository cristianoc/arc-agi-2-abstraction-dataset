# 4c416de3 Abstractions

- **identity** – Baseline pass-through; fails on the first training example (0% accuracy). Useful only to confirm that non-trivial repainting is required.
- **corner_hooks** – Uses zero-frame corners plus single-cell markers to paint oriented hook patterns; achieves 100% on train and produces consistent 19×22 predictions for test grids.

Final solution: `corner_hooks` (implemented in `analysis/arc2_samples/4c416de3.py`) which selects pattern families based on corner orientation and marker distances, matching all provided cases.
