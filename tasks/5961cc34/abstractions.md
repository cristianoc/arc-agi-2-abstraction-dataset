- Ray_connect_all: Filled every motif and propagated all guide rays (no filtering); connected component prune left small glyph active, so train hit 75% with first failure at train[3].
- Filtered_scaffold: Added the orange-guide count gate before ray casting; keeps only motifs with paired guides, yielding 100% on train and matching the test projection we expect.

The filtered scaffold abstraction is the final solver: sentinel-led BFS after guide filtering keeps a single connected blue columned scaffold that passes every available case.

## DSL Structure
- **Typed operations**
  - `extractMotifs : Grid -> List Motif` — collect candidate motifs with their guide-ray metadata.
  - `filterByGuideCount : List Motif -> List Motif` — keep motifs whose orange guides appear in paired counts.
  - `buildGuideGraph : Grid × List Motif -> Graph` — connect filtered motifs via their guide rays and sentinel anchors.
  - `propagateScaffold : Graph -> Grid` — run the sentinel BFS along the guide graph to paint the final scaffold.
- **Solver summary**: "Extract motifs, filter them by guide counts, build the guide/sentinel graph, then propagate the scaffold along that graph."

## Lambda Representation

```python
def solve_5961cc34(grid: Grid) -> Grid:
    motifs = extractMotifs(grid)
    filtered = filterByGuideCount(motifs)
    guide_graph = buildGuideGraph(grid, filtered)
    return propagateScaffold(guide_graph)
```
