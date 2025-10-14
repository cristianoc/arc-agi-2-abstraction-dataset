# Abstraction Summary – Task 58f5dbd5

- **identity:** copies the input grid without analysis; matches 0/3 training cases (first failure train[0]).
- **scoreboard:** clusters high-area colors, picks a row×column layout, and paints the learnt 5×5 glyph per slot; matches 3/3 training cases and is used for the final solver.

The final refinement is the **scoreboard** abstraction, which reliably reproduces the provided outputs and yields a coherent 3×2 glyph board on the withheld test input.

## DSL Structure
- **Typed operations**
  - `findSignificantColors : Grid -> (Color, List Color)` — identify the background and the non-background colours with enough support.
  - `computeCentroids : Grid × List Color -> Dict Color -> Point` — measure each colour’s centroid to guide board placement.
  - `inferBoardLayout : Dict Color -> Layout` — choose the row×column arrangement by comparing centroid spreads and factor pairs.
  - `assignSlotsAndRender : Grid × Color × Dict Color -> Layout -> Grid` — assign colours to board slots using centroid order and render the scoreboard with the stored digit templates.
- **Solver summary**: "Find significant colours, compute their centroids, infer a board layout from the spreads, then assign slots and render the scoreboard templates."
