# ARC Task 6e4f6532 – Abstractions Summary

- **identity** – Baseline that returns the input unchanged; serves as a control and unsurprisingly scores 0/2 on train cases.
- **heuristic_orientation** – Attempted to rotate shapes by matching their 9-cells to marker positions; partial alignment but still mismatched colors, yielding 0/2 matches.
- **canonical_template** – Uses the templates learned from train outputs (now implemented in the solver); reproduces the motifs around each marker and achieves 2/2 train accuracy.
