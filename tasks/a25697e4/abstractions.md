# a25697e4 Abstraction Notes

- **fill_anchor_holes** – preserve the dominant component and simply paint the empty slots inside its bounding box with the closest secondary color. This ignores the displaced component, so it solves 0/3 train pairs and fails immediately on train[0].
- **compact_components_v1** – first compaction attempt that projects the third color using a fixed vertical direction. Orientation mistakes break all examples (0/3 train, failure at train[0]).
- **compact_components_final** – refined heuristic that selects the bridge color via row-alignment, then orients the relocated component by scanning both vertical directions against hole statistics. Matches 3/3 train pairs; test has no public labels but this path feeds the production solver.

## DSL Structure
- **Typed operations**
  - `collectColorStats : Grid -> ColourStats` — identify the anchor colour and gather cell lists for each palette colour.
  - `analyseHoles : List Cell -> HoleStats` — compute the hole set inside the anchor bounding box and measure its row offset from the anchor centre.
  - `chooseBridgeColour : ColourStats × HoleStats -> Color` — select the bridge colour whose centroid best matches the hole offset, with fallbacks.
  - `placeThirdComponent : Grid × ColourStats × HoleStats -> Grid` — position the remaining colour’s component by testing directional templates while avoiding conflicts with anchors and holes.
- **Solver summary**: "Collect colour statistics, measure the anchor holes, choose the bridge colour by row alignment, and place the third component using the directional placement routine."

## Lambda Representation

```python
def solve_a25697e4(grid: Grid) -> Grid:
    colour_stats = collectColorStats(grid)
    hole_stats = analyseHoles(colour_stats.anchor_cells)
    return placeThirdComponent(grid, colour_stats, hole_stats)
```
