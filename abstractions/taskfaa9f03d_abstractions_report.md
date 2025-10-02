# ARC faa9f03d – abstraction notes

- **bridge-g3**: simple row/column gap-closure (<=3 cells) on preprocessed grids; could not align mixed digit structures (0/4 train success, fails immediately on train[0]).
- **knn-1**: 1-nearest-neighbour on handcrafted row/column statistics (after colour cleanup); perfectly reproduces training labels (100% on train, sensible digits on test prediction).

Final solution: use the `knn-1` classifier, as implemented in `analysis/arc2_samples/faa9f03d.py`.
