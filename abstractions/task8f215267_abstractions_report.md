# ARC task 8f215267 – abstraction notes

- Identity: baseline passthrough used to confirm dataset wiring; 0/3 train matches.
- Striped frames v0: reconstruct frames while counting distinct colours in the noisy patch; 0/3 train matches.
- Striped frames v1: introduce canonical patch templates with fallback to v0 counting; 3/3 train matches, produces clean prediction for the hidden test.
- Final solver: same pipeline as v1 packaged in `solve_8f215267`, adopted as the final refinement.

All evaluations were produced with `analysis/task8f215267_abstractions.py::evaluate_abstractions()`; no arc-gen samples are provided for this task.
