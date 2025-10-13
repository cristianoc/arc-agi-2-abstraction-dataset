# ARC Task 221dfab4 Abstraction Notes

- **stripe_projection** – Propagates the observed 4-columns upward with a 6-row period (rows 0 mod 6 → 3, rows 2/4 mod 6 → 4, others → background). Matches: train 0/2 (fails immediately because it ignores non-stripe object cells).
- **stripe_plus_mod0_objects** – Adds a 3-overlay on every 0 mod 6 row wherever the non-background object color appears, preserving the stripe behaviour. Matches: train 2/2; this is the deployed solver.

The combined stripe-plus-overlay abstraction succeeds on the full training set, so we adopt it for test predictions; the generated outputs align with the expected geometric layering.
