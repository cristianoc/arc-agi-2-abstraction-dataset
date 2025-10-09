### Identity
Baseline copy; leaves impurities intact. Train mismatch at sample 0; no generalisation potential.

### Naive Component Fill
Flood-fills the dominant non-background component; over-grows into background and fails on first train sample.

### Segmented Wedge
Orientation-aware wedge growth with barrier-aware clamping; matches all train cases and preserves the intended gap structure, producing the final solution.
