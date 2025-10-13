# Abstractions for 3dc255db

- `identity`: baseline copy of the input; keeps every training failure (0/3) so it establishes the reference diff set.
- `normalized_axis`: moves intruder components using normalized offsets; fixes two grids but fails on train[0] because horizontal placement chooses the wrong side (2/3, first fail train[0]).
- `intruder_edge_push`: compares raw offsets and pushes intruders opposite their dominant drift, using per-axis uniqueness to size the segment; passes all training grids (3/3) and yields the deployed solution.

Final solver: `intruder_edge_push` applied directly in `analysis/arc2_samples/3dc255db.py`, producing the expected behaviour on train and the computed test prediction.

