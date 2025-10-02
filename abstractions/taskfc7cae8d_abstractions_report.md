# fc7cae8d Abstraction Report

- `identity`: Baseline copy of the input grid; leaves the oversized canvas untouched and therefore misses all targets (0/3 train solved).
- `rotate_ccw`: Crop the largest interior component and rotate it 90° counter-clockwise; resolves two training grids but misorients the asymmetric instance (2/3 solved, first miss train[0]).
- `rotate_ccw_flip`: Same crop with a forced horizontal mirror after rotation; fixes the asymmetric case but breaks the symmetric ones (1/3 solved, first miss train[1]).
- `rotate_ccw_column_heuristic`: Apply the rotation and flip only when the dominant color is heavier on the right edge; keeps the asymmetric example aligned while preserving the symmetric grids (3/3 solved, no failures). This heuristic matches the final solver shipped in `analysis/arc2_samples/fc7cae8d.py` and is used for the test inference.
