# Abstractions for Task 8f3a5a89

- `boundary_only`: marks the four-neighbour frontier of the left-accessible `8` region without further filtering; leaves stray `1` components untouched. Fails (0/3 train) because it colours boundaries around internal holes and preserves noisy `1` islands.
- `boundary_with_diag`: extends the previous idea with a diagonal halo to reach corner-adjacent obstacles. Improves to 1/3 train but still paints hole boundaries and keeps isolated `1`s.
- `final_hybrid`: prunes `1` components that neither touch the left edge nor border the accessible background, and filters the frontier so only neighbours that connect to the exterior (or border-touching obstacles) are painted; adds the diagonal halo afterwards. Matches all train cases (3/3) and serves as the submitted solver. Test inference produces a 12×12 grid consistent with the learned pattern (see abstraction harness output).

## DSL Structure
- **Typed operations**
  - `floodAccessibleBackground : Grid -> Set Cell` — flood-fill colour-8 cells reachable from the left edge.
  - `labelInaccessibleRegions : Grid × Set Cell -> Dict Cell -> Bool` — classify other background cells by whether their components touch the border.
  - `pruneOnes : Grid × Set Cell -> Grid` — remove colour-1 components that neither touch the left edge nor border the accessible background.
  - `selectFrontierCells : Grid × Set Cell × Dict Cell -> Set Cell` — choose accessible background cells that neighbour the exterior or diagonal obstacles.
  - `paintFrontier : Grid × Set Cell -> Grid` — colour the selected frontier cells with 7 and leave the rest as 8.
- **Solver summary**: "Flood the left-accessible background, label the remaining background components, prune irrelevant `1`s, select the frontier cells adjacent to obstacles or the exterior, and paint those frontier cells with colour 7."
