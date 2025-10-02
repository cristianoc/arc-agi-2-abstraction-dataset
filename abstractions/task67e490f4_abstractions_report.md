## 67e490f4 Abstractions

- `colour_bbox`: locate the motif via the largest square colour bounding box and recolour by shape similarity. Matches 2/2 train tasks but relies on lucky alignment, so it is fragile for the evaluation grid (no labelled test targets).
- `two_colour_scan`: scan all two-colour squares and keep the one whose non-background components stay below the size threshold, then reuse the shape-matching palette. Covers 2/2 train tasks and supplies the evaluation prediction used in the solver.

Final pipeline: apply `two_colour_scan`, then recolour each motif component with the dominant matching shape colour gathered from the rest of the grid.

