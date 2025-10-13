# Task 195c6913 Abstractions Report

## Abstractions

1. **identity** – baseline returning the input unchanged.
2. **anchor_rows_only** – fills only the legend-defined rows with the detected pattern without spatial propagation.
3. **full_propagation** – implements the final legend-aware row/column propagation with boundary capping (the solver).

## Performance Summary

| Abstraction | Train | Test | arc-gen | Notes |
|-------------|-------|------|---------|-------|
| identity | 0/3 | n/a | n/a | Baseline placeholder. |
| anchor_rows_only | 1/3 | n/a | n/a | Captures anchor rows but misses vertical propagation. |
| full_propagation | 3/3 | n/a | n/a | Matches all observed targets; solver used in `analysis/arc2_samples/195c6913.py`. |

The final abstraction extends the palette pattern across selected rows and columns defined by the anchor rows. The palette columns are propagated upward from the top anchor and upward from the bottom anchor (when present), inserting cap colours at the exposed boundaries to mirror the ground-truth patterns.
