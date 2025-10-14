# Abstractions for dfadab01

- **identity** – returned the grid unchanged; fails immediately on train[0] (0/4).
- **simple_tiles** – context-free 4×4 motifs per colour; improves coverage but still misses composite interactions (2/4, first failure train[0]).
- **patch_dictionary** – colour-conditioned mapping from 4×4 input patches (with edge padding) to motifs inferred from train data; matches all train cases (4/4) and produces a plausible X-pattern of 7s on the held-out test input.

The final solver uses the patch dictionary abstraction, overlaying motifs only where the learned lookup returns a non-zero pattern; this reproduces every training output exactly while yielding a consistent tessellated output for the unseen test grid.

## DSL Structure
- **Typed operations**
  - `extractPatch4x4 : Grid × Cell -> Patch` — capture the 4×4 neighbourhood around a seed cell with padding.
  - `lookupPatchTemplate : Color × Patch -> Optional Patch` — query the colour-specific dictionary for a replacement motif.
  - `stampTemplate : Grid × Patch × Cell -> Grid` — overlay the template onto the output grid, ignoring zero entries.
- **Solver summary**: "Extract 4×4 patches per coloured cell, look up the matching template in the colour-conditioned dictionary, and stamp the template into the output."

## Lambda Representation

```python
def solve_dfadab01(grid: Grid) -> Grid:
    seeds = [
        (r, c)
        for r, row in enumerate(grid)
        for c, colour in enumerate(row)
        if colour != 0
    ]

    def repaint(canvas: Grid, cell: Cell) -> Grid:
        colour = grid[cell[0]][cell[1]]
        patch = extractPatch4x4(grid, cell)
        template = lookupPatchTemplate(colour, patch)
        if template is None:
            return canvas
        return stampTemplate(canvas, template, cell)

    return fold_repaint(grid, seeds, repaint)
```
