# ARC Task 1818057f – Abstraction Notes

- **identity** – Baseline projection that returns the grid unchanged; fails immediately on train case 0 (0/3 matches).
- **plus_painter** – Detects any `4`-colored plus (center with four orthogonal `4` neighbours) and recolors the five-cell motif to `8`; perfect on the training split (3/3) and yields the submitted evaluation output.

Final solver mirrors the `plus_painter` abstraction directly; no additional hybrids were necessary.

## DSL Structure
- **Typed operations**
  - `isPlus : Grid × (Row,Col) -> Bool` — check whether the cell and its four orthogonal neighbours all carry colour 4.
  - `repaintPlus : Grid × (Row,Col) -> Grid` — recolour a detected plus (centre and arms) to colour 8.
- **Solver summary**: "Scan the grid for 4-coloured plus motifs and recolour each detected plus (centre and arms) to 8." 
