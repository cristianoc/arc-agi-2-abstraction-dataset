# Abstractions for ARC task 7c66cb00

- `identity`: naive copy-through baseline; leaves noisy legend rows intact and fails on every train case (0/3).
- `clear_prototypes`: blanks any section that still contains the background color, but without stamping masks; this erases the legend yet leaves the lower bands untouched (0/3).
- `stamp_top`: copies legend masks using the edge color but keeps their original vertical offset; figures float too high, so matches still fail (0/3).
- `stamp_bottom`: reuses the legend masks, re-anchoring them to the bottom of each target band before recoloring; hits all train pairs (3/3) and produces plausible test output.
- `final_solver`: module implementation of the bottom-aligned stamping pipeline; mirrors `stamp_bottom` performance (3/3) and is used for submission.

## DSL Structure
- **Typed operations**
  - `getBackground : Grid -> Color` — choose the background as the top-left cell colour.
  - `splitSections : Grid × Color -> List (RowStart, RowEnd)` — partition the grid into horizontal sections separated by pure-background rows.
  - `extractPrototypes : Grid × List Sections × Color -> Any` — gather legend components, normalise offsets, and split the input sections into legend (`protoSections`) and target (`targetSections`).
  - `clearPrototypeRows : Grid × List Sections × Color -> Grid` — blank out the legend sections once prototypes are captured.
  - `stampBottomAnchored : Grid × Dict[Color, List Prototype] × List Sections -> Grid` — for each target section, realign the prototype mask to the bottom and stamp it using the edge colour.
- **Solver summary**: "Compute background and sections, extract prototype masks and the proto/target partition, clear the legend rows, then bottom-anchor and stamp masks onto each target band."

## Lambda Representation

```python
def solve_7c66cb00(grid: Grid) -> Grid:
    base = getBackground(grid)
    sections = splitSections(grid, base)
    prototypes, protoSections, targetSections = extractPrototypes(grid, sections, base)
    cleared = clearPrototypeRows(grid, protoSections, base)
    return stampBottomAnchored(cleared, prototypes, targetSections)
```
