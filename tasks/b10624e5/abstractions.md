# Task b10624e5 – Abstraction Notes

- **naive** – copies horizontal and vertical ornaments from the reference 2-components but treats vertical inner/outer colours as distinct even when identical; passes 1/2 train grids (fails train[0] where the duplicated colour shortens the outer 8 stripe).
- **refined** – same template inference with a guard that drops the vertical inner colour when it matches the outer stripe; 2/2 train grids, no ground-truth available for test, and arc-gen is absent.

The final solver uses the refined template expansion and therefore matches all available evaluation cases for the task.

## DSL Structure
- **Typed operations**
  - `locateCrossAxes : Grid -> (RowIndex, ColIndex)` — find the dominant row and column of ones that define the central cross.
  - `extractTwoComponents : Grid -> List Component` — capture each colour-2 block with bounding boxes and side metadata.
  - `inferOrnamentPalette : Grid × List Component × (RowIndex, ColIndex) -> OrnamentColors` — measure adjacent columns/rows around each component to choose inner/outer horizontal and vertical colours (dropping redundant inner stripes).
  - `paintOrnaments : Grid × List Component × OrnamentColors -> Grid` — expand the components horizontally and vertically according to the inferred palette to build the final ornamentation.
- **Solver summary**: "Detect the central cross, extract the colour-2 components, infer the horizontal/vertical ornament colours with redundancy guards, and paint those ornaments around each component."
