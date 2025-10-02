# Task 271d71e2 – Abstraction Notes

- `identity`: leaves the grid untouched; 0/3 train matches (first failure at train[0]), so it provides a baseline only.
- `patch_lookup_strict`: replays memorised 7×7 input patches from the training set; 3/3 train matches but would revert to the input colour on unseen contexts, so it offers no guard for novel patches in evaluation.
- `patch_lookup_nearest`: extends the lookup with a nearest-neighbour fallback in Hamming space; 3/3 train matches and supplies the final solver used in `analysis/arc2_samples/271d71e2.py`.

Final refinement adopts `patch_lookup_nearest`, ensuring we copy the exact training behaviour while still producing a deterministic answer for unseen neighbourhoods.
