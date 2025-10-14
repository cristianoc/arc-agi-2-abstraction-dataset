# de809cff Abstraction Report

- **identity** – untouched grids show the gap to close; 0/2 on train.
- **seed_halo** – mark zero pockets with ≥3 uniform neighbours and repaint their halos with the opposite colour; introduces the 8 markers but still misses the structural clean-up (0/2).
- **halo_plus_pruning** – adds a pruning pass that deletes stranded pixels (≥3 zero neighbours) and already solves train[0] while failing on train[1] (1/2, first failure at 1).
- **final_abstraction** – halo expansion plus a secondary-to-primary realignment (for secondary pixels with ≥3 primary neighbours) and the pruning pass; 2/2 on train and matches the production solver.
- **final_solver** – wrapper around `solve_de809cff`, which reuses the final abstraction pipeline for submission (2/2 train, handles the test case without ground truth).

`analysis/taskde809cff_abstractions.py` exposes these pipelines and the small evaluation harness.

## DSL Structure
- **Typed operations**
  - `detectZeroSeeds : Grid -> List (Cell, Color)` — find zero cells with ≥3 matching non-zero neighbours and record their host colour.
  - `paintHalos : Grid × List (Cell, Color) -> Grid` — promote seeds to colour 8 and paint the surrounding halo with the opposite colour.
  - `realignSecondaryPixels : Grid × Grid -> Grid` — flip secondary-colour pixels that are supported by ≥3 primary neighbours.
  - `pruneStragglers : Grid × Grid -> Grid` — remove pixels that retain ≥3 zero neighbours, restoring the cleaned background.
- **Solver summary**: "Detect strong zero pockets, paint haloes around them, realign secondary pixels near primary clusters, and prune residual stragglers."
