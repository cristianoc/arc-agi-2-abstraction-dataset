## Abstractions Tested

- `identity`: pass-through of the input grid; serves as a control and fails on train (0/3 solved, first failure at train[0]).
- `template_transfer`: extracts the lone multi-cell template, interprets singleton markers as a coarse lattice, and tiles the template with a color swap at the pivot marker (3/3 train solved; test prediction yields the expected tiled banded cross pattern).

## Final Approach

`template_transfer` is the deployed solver. It reconstructs a grid whose size is determined by the marker lattice (step two in both axes), anchors the lattice one template-height/width above and to the left of the original template, and paints each block with the template color unless the marker matches the template color, in which case it swaps to the alternate marker color. This matches all training examples and produces a coherent extrapolation on the held-out test case.

## DSL Structure
- **Typed operations**
  - `extractTemplate : Grid -> (Template, Color)` — identify the multi-cell pattern and capture its trimmed mask and colour.
  - `collectMarkers : Grid -> Dict Color -> List Cell` — gather singleton markers by colour to infer the lattice spacing.
  - `computeLattice : Dict Color -> List Cell -> (Int, Int, List Cell)` — determine row/column steps and anchor positions from the marker lattice.
  - `tileTemplate : Template × (Int, Int) × List Cell -> Grid` — replicate the template across the lattice, swapping colours when marker colours disagree.
- **Solver summary**: "Extract the template pattern, read the lattice markers, compute the tiling lattice, and tile the template across the lattice with colour swaps driven by the markers."
