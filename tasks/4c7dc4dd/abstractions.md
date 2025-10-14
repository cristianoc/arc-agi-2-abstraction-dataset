# Abstraction notes for task 4c7dc4dd

- `identity`: direct passthrough of the 30×30 grid; unsurprisingly fails on both training pairs (0/2) because the target compresses the scene to a symbolic glyph.
- `downsample_zero_presence`: coarse 5×5 zero-mask; still misaligns with targets (0/2) since it over-predicts and cannot express the asymmetric “L/Π” silhouettes.
- `zero_component_glyph`: detect sizeable zero rectangles, derive a coarse row/column scaffold, extend auxiliary strokes when right-heavy, and tag the anchor corner with a rare color. This matches both training pairs (2/2) and is used in the final solver.

The evaluation harness in `analysis/task4c7dc4dd_abstractions.py` compares these abstractions across train/test/arc-gen splits and reports match counts plus first failure indices.

## DSL Structure
- **Typed operations**
  - `detectZeroRectangles : Grid -> List Rectangle` — find maximal zero-filled rectangles that describe the coarse scaffold.
  - `buildScaffold : List Rectangle -> Scaffold` — convert rectangles into a coarse row/column scaffold with anchor metadata.
  - `augmentScaffold : Scaffold -> Scaffold` — extend auxiliary strokes and add anchor tags when the scaffold is right-heavy.
  - `renderGlyph : Scaffold -> Grid` — paint the symbolic glyph defined by the scaffold onto the output canvas.
- **Solver summary**: "Detect zero rectangles, turn them into a scaffold, augment it with auxiliary strokes and anchor tags, then render the resulting glyph."

## Lambda Representation

```python
def solve_4c7dc4dd(grid: Grid) -> Grid:
    rectangles = detectZeroRectangles(grid)
    scaffold = buildScaffold(rectangles)
    augmented = augmentScaffold(scaffold)
    return renderGlyph(augmented)
```
