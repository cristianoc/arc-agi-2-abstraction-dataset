# Task 71e489b6 Abstractions

- **identity** – return the grid unchanged; 0/3 train matches (first failure on train[0]).
- **majority_cleanup** – flip 1s with ≥3 zero neighbours to 0; still 0/3 because no highlighting is produced.
- **tip_halo** – detect zero tips and draw guarded 7 halos plus the zero-majority cleanup; 3/3 train matches with no regressions, and the test predictions show the expected tip-centred halos without artefacts.
