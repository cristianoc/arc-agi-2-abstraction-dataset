## Abstractions Tested

- `identity`: pass-through of the input grid; serves as a control and fails on train (0/3 solved, first failure at train[0]).
- `template_transfer`: extracts the lone multi-cell template, interprets singleton markers as a coarse lattice, and tiles the template with a color swap at the pivot marker (3/3 train solved; test prediction yields the expected tiled banded cross pattern).

## Final Approach

`template_transfer` is the deployed solver. It reconstructs a grid whose size is determined by the marker lattice (step two in both axes), anchors the lattice one template-height/width above and to the left of the original template, and paints each block with the template color unless the marker matches the template color, in which case it swaps to the alternate marker color. This matches all training examples and produces a coherent extrapolation on the held-out test case.
