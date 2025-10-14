# Abstractions for f560132c

- **identity** – direct passthrough of the input; serves as baseline and fails immediately (`0/2` train, fails at train[0]).
- **size_sorted** – map components to palette colours by descending area without regard to offsets; improves coverage of component shapes but still misses spatial arrangement (`0/2` train, fails at train[0]).
- **offset_oriented** – group components by relative offset from the palette anchor, rotate by quadrant-specific rules, and size the canvas via paired min-sums; reproduces both training cases (`2/2` train) and provides confident predictions on the evaluation input.

Final refinement: adopt the **offset_oriented** abstraction, which yields 100% agreement on the training split and generates a coherent 13×10 prediction for the evaluation grid.

## DSL Structure
- **Typed operations**
  - `extractComponents : Grid -> List Component` — gather non-zero components with cell lists, size, and centroid metadata.
  - `classifyQuadrants : List Component -> Dict Label -> Component` — identify the palette component and assign the remaining components to roles (a/b/c/d) via relative offsets.
  - `rotateComponentMask : Component × Orientation -> Mask` — trim each component to its minimal mask and rotate it according to the role-specific orientation.
  - `composeCanvas : Dict Label -> Mask × Dict Label -> Color -> Grid` — place rotated masks onto the output canvas corners using the palette colours.
- **Solver summary**: "Extract components, assign them to quadrant roles using centroid offsets, rotate their trimmed masks per role, and compose the canvas with those masks coloured from the palette."
