# Abstractions for ARC task 7ed72f31

- **identity** – baseline passthrough; 0/2 train matches, first failure at train[0]; used only as control.
- **nearest_axis_reflection** – mirrors each non-axis component across its closest color-2 axis after checking axis applicability; 2/2 train matches, generalises cleanly to test/arc-gen predictions.
- **final_solver** – reusable wrapper around the finished solver; identical behaviour to `nearest_axis_reflection`, kept for harness completeness and to surface final test predictions.

Final approach: prefer the nearest-axis reflection abstraction because it already attains perfect training accuracy while producing plausible test outputs consistent with the intended symmetry completion.
