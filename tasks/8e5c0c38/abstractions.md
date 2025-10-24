# Task 8e5c0c38 – Abstraction Notes

- `identity`: copied the input grid unchanged; produced 0/2 train matches (first failure at train[0]) so it fails immediately.
- `component_axis_symmetry`: enforced symmetry per connected component; also 0/2 train matches because local axes ignored cross-component structure and left extraneous pixels.
- `global_color_symmetry`: selected a single horizontal mirror axis per color via minimal deletions; 2/2 train matches and generalises cleanly to the test inputs.

Final refinement uses `global_color_symmetry`, which trims the unmatched color pixels relative to the best global axis and yields the official solution.

## DSL Structure
- **Typed operations**
  - `groupCellsByColor : Grid -> ColourGroups` — collect coordinates for each non-background colour.
  - `evaluateAxisCost : List Cell -> Axis` — for each colour, scan candidate horizontal axes and choose the one minimising deletions.
  - `trimAsymmetricCells : Grid × List Cell × Axis -> Grid` — remove cells that lack a mirrored partner with respect to the chosen axis.
- **Solver summary**: "Group cells by colour, pick the best horizontal axis per colour by minimal deletions, and remove asymmetric cells."

## Lambda Representation

```python
def solve_8e5c0c38(grid: Grid) -> Grid:
    colour_groups = groupCellsByColor(grid)

    def trim(canvas: Grid, entry):
        colour, cells = entry
        axis = evaluateAxisCost(cells)
        return trimAsymmetricCells(canvas, cells, axis)

    trimmed = fold_repaint(grid, list(colour_groups.items()), trim)
    return trimmed
```
