# Abstractions for ARC task 7ed72f31

- **identity** – baseline passthrough; 0/2 train matches, first failure at train[0]; used only as control.
- **nearest_axis_reflection** – mirrors each non-axis component across its closest color-2 axis after checking axis applicability; 2/2 train matches, generalises cleanly to test/arc-gen predictions.
- **final_solver** – reusable wrapper around the finished solver; identical behaviour to `nearest_axis_reflection`, kept for harness completeness and to surface final test predictions.

Final approach: prefer the nearest-axis reflection abstraction because it already attains perfect training accuracy while producing plausible test outputs consistent with the intended symmetry completion.

## DSL Structure
- **Typed operations**
  - `extractAxes : Grid -> List Axis` — collect colour-2 components and classify them as vertical, horizontal, block, or point axes.
  - `axisApplicable : Axis × Cell -> Bool` — check whether a non-axis cell falls within the span guarded by the axis type.
  - `reflectAcrossAxis : Axis × Cell -> Cell` — mirror a cell’s coordinates around the chosen axis centre.
  - `paintReflections : Grid × List Axis -> Grid` — for each non-background cell, choose the nearest applicable axis and reflect it onto background cells.
- **Solver summary**: "Identify axis components, determine which axis applies to each coloured cell, reflect the cell across the chosen axis, and paint the reflection if the target cell is background."
