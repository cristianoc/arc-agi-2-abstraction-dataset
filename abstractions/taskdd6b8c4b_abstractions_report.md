# task dd6b8c4b – abstraction summary

- **identity** – Baseline copy of the grid used to check expectations; 0/3 train matches.
- **ring_fill** – Applies the quadrant-imbalance heuristic to paint the central ring but keeps all original 9s; 0/3 train matches because surplus 9s stay scattered.
- **balanced_relocation** – Combines ring filling with score-ranked relocation of 9s (final solver); 3/3 train matches and best qualitative fit on the test probe.

Final pipeline: use `balanced_relocation`, which first determines how many ring tiles to promote to colour 9 based on the east–west imbalance, then retires the same number of scattered 9s with the `-3*dr - |dr| + |dc| - boundary` score so the total count is preserved.
