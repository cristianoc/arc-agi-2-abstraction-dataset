# Task 581f7754 Abstractions

- **identity** – pass-through baseline that keeps the grid unchanged; failed all train cases (0/3, first failure train[0]).
- **column_anchor** – translates connected components so each anchor colour lies on a common column but skips row refinement; solved 2/3 train cases (first failure train[1]).
- **full_alignment** – column anchoring plus row-based compression toward anchor rows, matching all train samples (3/3) and producing the delivered test outputs.
