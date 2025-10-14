# faa9f03d Abstractions Report

- **noise_only** – Recolors low-frequency cells with majority neighbours; collapses stray artifacts but leaves underlying digits disconnected. Train accuracy: 0/4.
- **row_col_closure** – Adds short row/column bridges around dominant colors; improves cohesion yet still misses long-range hooks. Train accuracy: 0/4.
- **flanked_extend** – Adds flanked infill and limited row extension; recovers one training case but fails to propagate vertical spines. Train accuracy: 1/4 (first failure at train[1]).
- **final_solver** – Full pipeline from `solve_faa9f03d` combining noise removal, selective closures, flanked infill, row extensions, and tail-specific six propagation. Train accuracy: 4/4 (no failures). Test prediction shown in harness output.

## DSL Structure
- **Typed operations**
  - `denoiseAndProfile : Grid -> (Grid, Color, Dict Color -> Stats)` — remove sparse noise, return the dominant colour, and compute max row/column support per colour.
  - `bridgeSelectiveGaps : Grid × Color × Dict Color -> Stats -> Grid` — close short gaps along rows/columns and apply flanked fills while respecting dominant-colour guards.
  - `extendBackbones : Grid × Color -> Grid` — prune sparse tops, extend qualifying rows, and propagate colour-1 columns through empty spans.
  - `tailPropagation : Grid -> Grid` — fill tail sections with colour 6, extend vertical tails, and suppress stray sixes at the top.
- **Solver summary**: "Denoise and profile the colours, bridge selective gaps with flanked fills, extend the main spines and propagate ones, then finish by growing the six-tail structures."
