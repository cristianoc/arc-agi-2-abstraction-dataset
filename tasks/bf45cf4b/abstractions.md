# bf45cf4b Abstraction Notes

**identity** — Copy input directly. Serves as a baseline and fails on train case 0 (0/3) because it cannot synthesize the required tiling.

**mask_tiling** — Detect non-background components, treat the single-colour component as a Boolean mask, and tile the multi-colour component’s bounding box wherever the mask is true. Hits 3/3 on train and yields the expected 25×25 patterned prediction on test.

Final solver: reuse of `mask_tiling` from `analysis/arc2_samples/bf45cf4b.py`.

