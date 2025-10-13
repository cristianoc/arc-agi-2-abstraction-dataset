# Task 5545f144 – Abstraction Notes

- `intersection`: keeps columns where every segment agrees on the highlight color; handles shared motifs but misses rows where only one segment carries signal (train 0/3).
- `first_segment_shift`: aligns the leftmost segment by stripping separator gaps; fixes single-segment rows yet ignores cross-segment consensus (train 0/3).
- `combined`: merges intersection cues, first-segment shifting, and special handling for two-segment grids to propagate the central column and back-fill supporting rows; matches 3/3 train cases and evaluates smoothly on held-out inputs.

The final solver mirrors the `combined` abstraction, using the consensus check for high-support columns and the alignment/extension rules to recover sparse motifs while respecting the double-segment idiosyncrasy.
