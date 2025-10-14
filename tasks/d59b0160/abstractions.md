# Task d59b0160 – Abstraction Notes

- **identity** – plain copy of the grid; leaves all cavities intact (0/3 train).
- **touch_right** – fills only rooms that touch the right boundary; captures the large rectangular hole but misses the off-boundary pockets (1/3 train, first miss train[0]).
- **internal_height4** – targets interior rooms of height ≤4; fails because key holes straddle edges (0/3 train).
- **full_rule** – combines edge-touch heuristics (right-edge fill, shallow interior rooms, left-edge height guard, height-5 edge bias) and achieves 3/3 train with no failures; used for the final solver, producing the visually coherent fill on the test grid.

## DSL Structure
- **Typed operations**
  - `identifyRooms : Grid -> List Room` — detect enclosed background regions with boundary metadata.
  - `classifyRoomFill : List Room -> Dict Room -> FillRule` — decide which heuristic applies (right-edge touch, shallow interior, left-edge guard, height-5 bias).
  - `applyFillRules : Grid × Dict Room -> FillRule -> Grid` — fill rooms according to their assigned rule while preserving protected regions.
  - `mergeFilledRooms : Grid × Grid -> Grid` — combine the filled rooms with the original grid to produce the final output.
- **Solver summary**: "Identify the rooms, classify each room’s fill rule, apply the fills per rule, and merge the result back into the grid."
