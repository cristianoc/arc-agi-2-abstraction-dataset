# Abstractions for f560132c

- **identity** – direct passthrough of the input; serves as baseline and fails immediately (`0/2` train, fails at train[0]).
- **size_sorted** – map components to palette colours by descending area without regard to offsets; improves coverage of component shapes but still misses spatial arrangement (`0/2` train, fails at train[0]).
- **offset_oriented** – group components by relative offset from the palette anchor, rotate by quadrant-specific rules, and size the canvas via paired min-sums; reproduces both training cases (`2/2` train) and provides confident predictions on the evaluation input.

Final refinement: adopt the **offset_oriented** abstraction, which yields 100% agreement on the training split and generates a coherent 13×10 prediction for the evaluation grid.

## DSL Structure
- **Typed operations**
  - `extractComponents : Grid -> List Component` — gather non-zero components with cell lists, size, and centroid metadata.
  - `classifyQuadrants : List Component -> QuadrantPlan` — identify the palette component, assign roles, and record orientation plus colour per quadrant (accessible via `plan.components`, `plan.orientations`, and `plan.colours`).
  - `rotateComponentMask : QuadrantPlan × Label -> Mask` — trim each component to its minimal mask and rotate it according to the role-specific orientation.
  - `composeCanvas : MaskMap × ColourMap -> Grid` — place rotated masks onto the output canvas corners using the palette colours.
- **Solver summary**: "Extract components, assign them to quadrant roles using centroid offsets, rotate their trimmed masks per role, and compose the canvas with those masks coloured from the palette."

## Lambda Representation

```python
def solve_f560132c(grid: Grid) -> Grid:
    components = extractComponents(grid)
    plan = classifyQuadrants(components)
    rotated_masks = dict(
        (label, rotateComponentMask(plan, label))
        for label in plan.components
    )
    return composeCanvas(rotated_masks, plan.colours)
```
