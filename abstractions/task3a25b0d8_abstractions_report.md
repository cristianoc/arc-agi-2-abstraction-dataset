# ARC Task 3a25b0d8 – Abstraction Attempts

- **expanded_only** – crop to the columns/rows that contain non-background colours and pad with background. Train accuracy: 0/2 (fails immediately at train[0] by missing the required downscaled logo).
- **band_adjust** – adds the band heuristics (widening 7s, removing singleton 4s, isolating 6 rows) but stops before the final row synthesis. Train accuracy: 0/2 (train[0] still fails; train[1] mis-shapes the mid block).
- **final_solver** – full pipeline from `analysis/arc2_samples/3a25b0d8.py`, combining band adjustments with row-wise synthesis and duplication. Train accuracy: 2/2 (no failures).

Test outputs are unavailable for this evaluation split, so only training matches are reported.
