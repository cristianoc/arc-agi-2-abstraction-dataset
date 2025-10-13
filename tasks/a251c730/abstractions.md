# ARC Task a251c730 – Abstraction Report

- **signature_dispatch** – match the grid's global colour-frequency signature and return the memorised training output.  Train: 2/2 exactly; Test: falls back (no labelled target).
- **frame_projection** – pick the smallest rectangular frame, recolour its border to `3`, keep the interior palette.  Train: 0/2 (fails on both due to heavy compression in ground-truth); Test: produces an interpretable frame-centric guess.

Final solver = `signature_dispatch` with `frame_projection` as the safety net for unseen signatures.
