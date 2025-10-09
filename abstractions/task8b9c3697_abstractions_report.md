# ARC task 8b9c3697 – abstraction notes

- `identity`: left the grid unchanged; serves as a sanity baseline (0/3 train matches).
- `greedy_slide`: moved each `2` cluster along the first open corridor; overcorrected by linking to multiple structures and regressed on all train cases (0/3).
- `matched_corridors`: matched `2` clusters to structures with size/shift/distance scoring and capped corridor length; achieves 3/3 train matches and produces a plausible 23×27 test output with paired doors and cleaned corridors.

The final solver uses the `matched_corridors` abstraction.
