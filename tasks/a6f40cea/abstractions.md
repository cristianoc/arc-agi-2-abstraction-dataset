# ARC Task a6f40cea Abstractions

- **baseline_projection** – projects colors orthogonally from the frame using axis-aligned run lengths only. It reaches 2/3 training success but misses the evaluation example that requires alternating bands (first failure at train[2]).
- **augmented_projection** – extends the projection with sequence heuristics (alternating stripes from left/right/bottom) and targeted gap closing. It solves all 3/3 training cases and yields the final submission (see script output for the generated test grid).
