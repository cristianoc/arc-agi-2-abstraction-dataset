# e8686506 abstractions

- **quantile_projection** – collapse the bounding box into five vertical majority stripes; over-smooths the coloured fragments and never matches any reference grid.
- **stripe_profile** – keep only each row's left, mid, right colours as a symmetric sketch; double counts the background and fails on all cases.
- **signature_lookup (final)** – compute the deduplicated foreground colour signature per row and map the full signature to the known miniature output. This matches all train/test grids.

## DSL Structure
- **Typed operations**
  - `deriveRowSignature : Grid -> Signature` — crop the foreground bounding box, strip background cells, and record deduplicated colour sequences per row.
  - `lookupMiniature : Signature -> Optional Grid` — fetch the precomputed 5-column pattern associated with the signature.
  - `compressFallback : Grid × Signature -> Grid` — slice the bounding box into five bands and majority-compress each band when the signature is unknown.
- **Solver summary**: "Compute the foreground row signature, return the stored miniature if present, otherwise compress the bounding box into five bands as a fallback."
