# Abstractions for ARC task 7c66cb00

- `identity`: naive copy-through baseline; leaves noisy legend rows intact and fails on every train case (0/3).
- `clear_prototypes`: blanks any section that still contains the background color, but without stamping masks; this erases the legend yet leaves the lower bands untouched (0/3).
- `stamp_top`: copies legend masks using the edge color but keeps their original vertical offset; figures float too high, so matches still fail (0/3).
- `stamp_bottom`: reuses the legend masks, re-anchoring them to the bottom of each target band before recoloring; hits all train pairs (3/3) and produces plausible test output.
- `final_solver`: module implementation of the bottom-aligned stamping pipeline; mirrors `stamp_bottom` performance (3/3) and is used for submission.

## DSL Structure
- **Typed operations**
  - `splitSections : Grid × Color -> List (RowStart, RowEnd)` — partition the grid into horizontal sections separated by pure-background rows.
  - `extractPrototypes : Grid × List Sections × Color -> Dict[Color, List[Prototype]]` — gather top legend components, normalise their offsets, and group them by fill colour.
  - `clearPrototypeRows : Grid × List Sections -> Grid` — blank out the legend sections once prototypes are captured.
  - `stampBottomAnchored : Grid × Dict[Color, List[Prototype]] × List Sections -> Grid` — for each target section, realign the prototype mask to the bottom and stamp it using the edge colour.
- **Solver summary**: "Split the grid into legend/target sections, extract prototype masks from the legend, clear the legend rows, and stamp each prototype onto the bottom of its corresponding target band."

## Lambda Representation

```python
def solve_7c66cb00(grid: Grid) -> Grid:
    sections = splitSections(grid, 0)
    prototypes = extractPrototypes(grid, sections, 0)
    cleared = clearPrototypeRows(grid, sections)
    return stampBottomAnchored(cleared, prototypes, sections)
```
