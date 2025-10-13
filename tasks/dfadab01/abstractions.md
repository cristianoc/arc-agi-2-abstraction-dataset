# Abstractions for dfadab01

- **identity** – returned the grid unchanged; fails immediately on train[0] (0/4).
- **simple_tiles** – context-free 4×4 motifs per colour; improves coverage but still misses composite interactions (2/4, first failure train[0]).
- **patch_dictionary** – colour-conditioned mapping from 4×4 input patches (with edge padding) to motifs inferred from train data; matches all train cases (4/4) and produces a plausible X-pattern of 7s on the held-out test input.

The final solver uses the patch dictionary abstraction, overlaying motifs only where the learned lookup returns a non-zero pattern; this reproduces every training output exactly while yielding a consistent tessellated output for the unseen test grid.
