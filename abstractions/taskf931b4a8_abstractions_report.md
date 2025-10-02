# f931b4a8 Abstractions

- `cycle`: cycles unique tile rows and columns regardless of masks. Reaches 3/5 train matches (first failure train[1]) because it ignores quadrant guidance and repeats the wrong patterns.
- `seqcols_origrow`: keeps the discovered row heuristic but forces sequential columns. Improves to 4/5 train matches (first failure train[4]) yet still misses the alternating row borrowed from the full-zero band.
- `final`: augments the row selector with a fallback borrow when the full-zero signature is present and reuses sequential columns. Achieves 5/5 train matches; test outputs inherit the expected checker/striped motifs.

Key refinement was recognising that the empty zero-signature rows must alternate with the fully-missing rows hinted by the lower-right quadrant; once that borrow hook was added the simple column index cycle sufficed.
