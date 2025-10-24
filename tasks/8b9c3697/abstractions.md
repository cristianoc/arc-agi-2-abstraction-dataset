# ARC task 8b9c3697 – abstraction notes

- `identity`: left the grid unchanged; serves as a sanity baseline (0/3 train matches).
- `greedy_slide`: moved each `2` cluster along the first open corridor; overcorrected by linking to multiple structures and regressed on all train cases (0/3).
- `matched_corridors`: matched `2` clusters to structures with size/shift/distance scoring and capped corridor length; achieves 3/3 train matches and produces a plausible 23×27 test output with paired doors and cleaned corridors.

The final solver uses the `matched_corridors` abstraction.

## DSL Structure
- **Typed operations**
  - `extractObjects : Grid -> List Object` — gather non-background, non-`2` structures with centroids and bounding boxes.
  - `extractTwoComponents : Grid -> List Component` — collect connected components of colour `2` with size and boundary metadata.
- `enumerateCorridorCandidates : Grid × List Component × List Object -> CorridorCandidates` — for each component, test straight corridors toward nearby objects and record feasible shifts.
  - `assignCorridors : CorridorCandidates -> Assignments` — choose at most one corridor per object, preferring larger components, shorter shifts, and closer centroids.
  - `applyCorridorMoves : Grid × Assignments -> Grid` — move assigned components along their corridors and erase the originals; clear unassigned components.
- **Solver summary**: "Extract structures and `2`-components, enumerate valid corridors, assign each object the best corridor, move the matching components along those corridors, and delete leftover `2`s."

## Lambda Representation

```python
def solve_8b9c3697(grid: Grid) -> Grid:
    objects = extractObjects(grid)
    two_components = extractTwoComponents(grid)
    candidates = enumerateCorridorCandidates(grid, two_components, objects)
    assignments = assignCorridors(candidates)
    return applyCorridorMoves(grid, assignments)
```
