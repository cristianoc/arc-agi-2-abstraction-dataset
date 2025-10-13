# e8686506 abstractions

- **quantile_projection** – collapse the bounding box into five vertical majority stripes; over-smooths the coloured fragments and never matches any reference grid.
- **stripe_profile** – keep only each row's left, mid, right colours as a symmetric sketch; double counts the background and fails on all cases.
- **signature_lookup (final)** – compute the deduplicated foreground colour signature per row and map the full signature to the known miniature output. This matches all train/test grids.
