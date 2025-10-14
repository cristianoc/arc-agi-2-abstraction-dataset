# Abstractions for 3dc255db

- `identity`: baseline copy of the input; keeps every training failure (0/3) so it establishes the reference diff set.
- `normalized_axis`: moves intruder components using normalized offsets; fixes two grids but fails on train[0] because horizontal placement chooses the wrong side (2/3, first fail train[0]).
- `intruder_edge_push`: compares raw offsets and pushes intruders opposite their dominant drift, using per-axis uniqueness to size the segment; passes all training grids (3/3) and yields the deployed solution.

Final solver: `intruder_edge_push` applied directly in `analysis/arc2_samples/3dc255db.py`, producing the expected behaviour on train and the computed test prediction.

## DSL Structure
- **Typed operations**
  - `extractIntruders : Grid -> List Component` — gather non-background components with centroid and bounding-box metadata.
  - `computeDrift : Component -> Offset` — calculate the signed offset between each component’s centroid and the host region centre.
  - `chooseTargetEdge : Offset -> Edge` — select the destination edge opposite the dominant drift axis (resolving ties via uniqueness checks).
  - `pushComponent : Grid × Component × Edge -> Grid` — translate the component along the chosen axis until it contacts the edge, repainting vacated cells with background.
- **Solver summary**: "Extract intruding components, compute their centroid drift, pick the edge opposite that drift, and push each component flush to the chosen edge."

## Lambda Representation

```python
def solve_3dc255db(grid: Grid) -> Grid:
    intruders = extractIntruders(grid)
    result = grid
    
    for component in intruders:
        drift = computeDrift(component)
        edge = chooseTargetEdge(drift)
        result = pushComponent(result, component, edge)
    
    return result
```
