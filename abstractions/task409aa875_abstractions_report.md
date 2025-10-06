# Task 409aa875 Abstraction Notes

- **identity** – Baseline mirror of the input (0/3 train). Useful only to confirm that every case genuinely needs reasoning beyond copy-through.
- **centroid-no-norm** – Lifts 8-connected components by five rows and drops a 9 on their horizontal centroid without re-anchoring columns (2/3 train, first fail train[2] where components live far to the right).
- **centroid-global-shift** – Same lifting scheme, but columns are normalised by each band’s minimum and odd-sized bands highlight the middle marker with colour 1 while recolouring any overlapped component (3/3 train; this is the final hybrid committed as `solve_409aa875`).
