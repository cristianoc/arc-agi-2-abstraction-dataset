# 89565ca0 Abstractions

- **naive_stripe** — mapped each color's bottommost stripe winner directly to prefix length with no fallback. Failed all 3/3 training tasks (first failure train[0]) because top-level colors lost rank when they never dominated a stripe.
- **refined_stripe** — introduced filler-aware dominance, area-ranked fallback for non-dominant colors, and remapped stripe indices (0→2, 1/2→3, 3→4). Achieved 3/3 training matches and produced coherent 4-column summaries on the evaluation input.

Final pipeline uses `refined_stripe`, which matches the production solver and yields plausible outputs on the held-out test grid.
