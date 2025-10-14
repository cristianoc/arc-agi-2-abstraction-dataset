# Task 64efde09 – Abstraction Notes

- `identity`: simple copy-through baseline; scores 0/2 on train (fails immediately because the task requires adding shadows).
- `vertical_only`: casts accent colors horizontally from each tall motif; captures major structure but still 0/2 on train because horizontal motifs remain untreated.
- `full_shadow`: combines vertical and orientation-aware horizontal shadows, alternating directions across columns and handling near-top motifs; matches 2/2 train cases and runs cleanly on test inputs.

Final solver uses the `full_shadow` abstraction, with the vertical and horizontal passes mirroring the two-stage reasoning above.

## DSL Structure
- **Typed operations**
  - `identifyMotifs : Grid -> List Motif` — collect tall and wide motifs with their anchor cells.
  - `castVerticalShadows : Grid × List Motif -> Grid` — project vertical shadows downward/upward from tall motifs with near-top handling.
  - `castHorizontalShadows : Grid × List Motif -> Grid` — project alternating horizontal shadows for wide motifs based on column parity.
  - `mergeShadowPasses : Grid × Grid × Grid -> Grid` — combine the vertical and horizontal shadow canvases with the original grid.
- **Solver summary**: "Identify motifs, cast vertical shadows, cast orientation-aware horizontal shadows, and merge the passes with the original grid."

## Lambda Representation

```python
def solve_64efde09(grid: Grid) -> Grid:
    motifs = identifyMotifs(grid)
    vertical = castVerticalShadows(grid, motifs)
    horizontal = castHorizontalShadows(grid, motifs)
    return mergeShadowPasses(grid, vertical, horizontal)
```
