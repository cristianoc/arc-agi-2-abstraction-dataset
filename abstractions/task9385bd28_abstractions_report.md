# Task 9385bd28 – Abstraction Notes

- **identity** – Baseline copy of the input grid; fails all 4 train cases (0/4).
- **naive_fill** – Fills every mapped bounding box without guards; overpaints key structures and still scores 0/4 on train.
- **guarded_fill** – Adds zero-pair handling and protects unmapped colors; reaches 2/4 train matches before stumbling on mixed legends.
- **final_solver** – Incorporates zero-pair clears, legend-aware protection, and recolors pure source boxes; passes all train cases (4/4) and is used for submission.
