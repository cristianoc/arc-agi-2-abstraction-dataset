# Abstractions for b6f77b65

- **identity** – left the grid untouched; matched 1/5 train cases (fails first at train[1]), useful only as a baseline sanity check.
- **segment_lookup_v0** – template lookup with the misaligned `(2,'adf','e')` pattern; matched 4/5 train grids, first failure at train[2] due to the downward-shifted 5/7 bands.
- **segment_lookup_v1** – corrected template alignment; matched 5/5 train grids and produces consistent outputs for both test inputs.
- **solver** – uses the same corrected templates as the shipping solver; serves as the final refinement that passes all observed cases.

The final approach is the corrected segment template lookup (segment_lookup_v1 / solver), which aligns the `(2,'adf','e')` digit template with the observed target and reproduces every training example while yielding plausible completions for the test grids.
