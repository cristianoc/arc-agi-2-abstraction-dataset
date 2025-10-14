# Abstractions for ARC task aa4ec2a5

- **identity** – sanity check baseline that copies the input; unsurprisingly scores 0/3 on train (fails case 0).
- **rectangular_frame** – first attempt that draws a full bounding-box frame around each `1` component; captures 2/3 train cases but over-fills rows that contain gaps, tripping case 1.
- **segment_frame** – segment-aware refinement that respects per-row spans and preserves enclosed holes; matches 3/3 train cases and aligns with the final solver output on the held-out test grid.

Final approach: `segment_frame` (packaged in the production solver), which combines hole detection with segment-wise framing so that only the intended neighborhood cells switch to colours `2` and `6`; this resolves every training example and produces a structured extrapolation on the evaluation input.

## DSL Structure
- **Typed operations**
  - `extractOneComponents : Grid -> List Component` — gather each colour-1 component with row/column ranges and cell lists.
  - `findInteriorHoles : Grid × Component × Color -> (Bool, Set Cell)` — flood-fill background cells inside the component bbox to detect enclosed holes.
  - `frameComponentRows : Grid × Component × Set Cell -> Grid` — extend per-row segments to recolour adjacent background cells (colour 2) while skipping hole cells.
  - `markComponentBody : Grid × Component × Bool -> Grid` — recolour the component itself to colour 8 when a hole exists and annotate hole cells with colour 6.
- **Solver summary**: "Extract each colour-1 component, detect whether it encloses holes, frame neighbouring background cells per row, and recolour the component/hole cells accordingly."

## Lambda Representation

```python
def solve_aa4ec2a5(grid: Grid) -> Grid:
    components = extractOneComponents(grid)

    def repaint(canvas: Grid, component: Component) -> Grid:
        has_hole, hole_cells = findInteriorHoles(canvas, component, 0)
        framed = frameComponentRows(canvas, component, hole_cells)
        return markComponentBody(framed, component, has_hole)

    return fold_repaint(grid, components, repaint)
```
