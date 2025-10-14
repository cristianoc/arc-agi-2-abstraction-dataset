# Abstraction Report – Task 4e34c42c

- **desc_min_col** – Concatenates normalized components in descending order of their left edge. Works on the first training grid but repeats duplicate columns and fails on train[1] (first failure index 1).
- **type_priority** – Prioritises unique short components, then wide-short strips, and finally tall blocks (with redundant snippets deferred). This composite ordering resolves all overlaps; it matches every train/test sample and keeps arc-gen consistent in our harness.

Final solver uses the `type_priority` ordering, as it alone preserves the asymmetry between the mid and bottom structures while avoiding duplicate columns contributed by redundant fragments.

## DSL Structure
- **Typed operations**
  - `extractComponents : Grid -> List Component` — gather all non-background components with size metadata.
  - `classifyComponentType : Component -> ComponentType` — label components as unique short, wide-short strip, tall block, etc.
  - `prioritiseComponents : List (Component, ComponentType) -> List Component` — sort components using the type priority and tie-breakers on position.
  - `concatenateComponents : List Component -> Grid` — place components left-to-right according to the prioritised order, avoiding duplicates.
- **Solver summary**: "Extract components, classify them, prioritise by type and position, then concatenate in that order to rebuild the column layout."

## Lambda Representation

```python
def solve_4e34c42c(grid: Grid) -> Grid:
    components = extractComponents(grid)
    typed = [(component, classifyComponentType(component)) for component in components]
    ordered = prioritiseComponents(typed)
    return concatenateComponents(ordered)
```
