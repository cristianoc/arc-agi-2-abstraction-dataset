# ARC 9bbf930d Abstraction Report

- **identity_solver** – baseline copy-through; fails immediately (0/3 train).
- **row_separator_solver** – moves the leading 6 for duplicated row bands; fixes separator edges but still misses column cues (2/3 train, first miss at train[2]).
- **full_solver** – extends with sparse-column heuristics (top/bottom capping + asymmetric boundary marking); passes all training examples and matches the production solver used in `arc2_samples/9bbf930d.py`.

## DSL Structure
- **Typed operations**
  - `analyseRows : Grid -> Tuple[List Int, List Optional Color]` — compute per-row non-(6,7) counts and dominant colours.
  - `adjustSeparatorRows : Grid × List Int × List Optional Color -> Grid` — recolour separator rows when neighbouring dominant colours match.
  - `selectSparseColumns : Grid -> List Int` — find columns with few non-(6,7) cells to inspect for 6 placement.
  - `markColumnJunctions : Grid × List Int × List Int × List Optional Color -> Grid` — place colour 6 markers in sparse columns using learnt heuristics (caps, thin towers).
- **Solver summary**: "Analyse row structures, adjust separator rows via dominant colours, select sparse columns, and mark their junctions with colour 6 according to the heuristic rules."
