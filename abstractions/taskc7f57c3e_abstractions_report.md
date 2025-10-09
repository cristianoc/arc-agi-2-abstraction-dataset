# ARC task c7f57c3e — abstraction notes

- **identity** – straight copy of the input grid. Matches no training cases (0/2) so it serves only as a baseline sanity check.
- **knn5** – reuse every 5×5 input patch observed in the training set and colour each cell by the nearest recorded patch (Hamming distance). Achieves 2/2 train matches; the predicted evaluation grid collapses to the background colour 4 everywhere, so generalisation is uncertain.

Final submission relies on the `knn5` patch-lookup abstraction because it is the only variant that fits the known examples exactly, though its test output (uniform 4) should be treated cautiously.
