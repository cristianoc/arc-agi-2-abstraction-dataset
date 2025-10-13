# Abstraction notes for task 4c7dc4dd

- `identity`: direct passthrough of the 30×30 grid; unsurprisingly fails on both training pairs (0/2) because the target compresses the scene to a symbolic glyph.
- `downsample_zero_presence`: coarse 5×5 zero-mask; still misaligns with targets (0/2) since it over-predicts and cannot express the asymmetric “L/Π” silhouettes.
- `zero_component_glyph`: detect sizeable zero rectangles, derive a coarse row/column scaffold, extend auxiliary strokes when right-heavy, and tag the anchor corner with a rare color. This matches both training pairs (2/2) and is used in the final solver.

The evaluation harness in `analysis/task4c7dc4dd_abstractions.py` compares these abstractions across train/test/arc-gen splits and reports match counts plus first failure indices.
