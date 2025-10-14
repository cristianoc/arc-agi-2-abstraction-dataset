# 4c416de3 Abstractions

- **identity** – Baseline pass-through; fails on the first training example (0% accuracy). Useful only to confirm that non-trivial repainting is required.
- **corner_hooks** – Uses zero-frame corners plus single-cell markers to paint oriented hook patterns; achieves 100% on train and produces consistent 19×22 predictions for test grids.

Final solution: `corner_hooks` (implemented in `analysis/arc2_samples/4c416de3.py`) which selects pattern families based on corner orientation and marker distances, matching all provided cases.

## DSL Structure
- **Typed operations**
  - `readCornerMarkers : Grid -> List Marker` — detect the coloured corner hooks and their orientation markers.
  - `classifyHookFamily : List Marker -> HookFamily` — classify which hook template to use based on marker orientation and spacing.
  - `generateHookTemplate : HookFamily × Marker -> Grid` — build the hook footprint for each corner, scaling arms by the measured distances.
  - `overlayHooks : Grid × List Grid -> Grid` — overlay the generated hooks onto the canvas without disturbing untouched cells.
- **Solver summary**: "Read the corner markers, choose the hook family, generate the appropriately scaled hook templates, and overlay them onto the grid."

## Lambda Representation

```python
def solve_4c416de3(grid: Grid) -> Grid:
    markers = readCornerMarkers(grid)
    family = classifyHookFamily(markers)
    hook_templates = [generateHookTemplate(family, marker) for marker in markers]
    return overlayHooks(grid, hook_templates)
```
