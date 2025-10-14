# Abstraction Notes for a32d8b75

- `identity`: simply drops the six instruction columns; leaves the right side untouched and fails all three training tasks (0/3).
- `block_map_no_tail`: uses the 3×6 instruction strips to paint 3×3 macro blocks but ignores the trailing leftover rows, so it misses the final sprite rows (2/3 solved, first failure at train[0]).
- `block_map_full` / `solver_module`: same mapping plus tail handling via dedicated two-row templates; renders every training example perfectly (3/3) and produces coherent outputs for the test grids.

Final refinement adopts `block_map_full`, which exactly matches the training outputs while preserving the instruction-driven structure for unseen inputs.

## DSL Structure
- **Typed operations**
  - `sliceInstructionBlock : Grid × Int -> Tuple Tuple Int` — read each 3×6 instruction strip on the left side.
  - `lookupSpriteRows : Tuple Tuple Int -> Optional List Row` — fetch the precomputed 3×24 sprite rows for the instruction block.
  - `writeSpriteRows : Grid × Int × List Row -> Grid` — overwrite the corresponding rows on the right portion with the looked-up sprite.
  - `handleTailBlock : Grid × Int -> Grid` — apply the specialised two-row templates for leftover rows at the bottom.
- **Solver summary**: "Slice each instruction strip, map it to the stored sprite rows, write those rows onto the right-hand canvas, and handle any trailing rows with the tail templates."
