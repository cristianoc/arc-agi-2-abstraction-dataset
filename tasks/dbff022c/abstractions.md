# Abstraction Notes for dbff022c

- `identity`: Leaves inputs untouched; fails immediately on train because the puzzle requires filling structured cavities.
- `fill_same_color`: Flood-fills zero pockets with their boundary color; still misses coloured partner fills and breaks samples with multi-colour legends (0/3 train).
- `partner_rule`: Detects zero cavities, filters by boundary colour/size, and paints partner colours (3/3 train). Test output aligns qualitatively (no ground truth to score).

Final solver uses the `partner_rule` abstraction.

## DSL Structure
- **Typed operations**
  - `enumerateZeroCavities : Grid -> List Component` — gather 0-components with metadata (boundary colour, size, adjacency set, border contact).
  - `choosePartnerColour : Component -> Optional Color` — apply the partner heuristics to decide the fill colour for a cavity.
  - `fillComponent : Grid × Component × Color -> Grid` — repaint the cavity cells with the chosen partner colour.
- **Solver summary**: "Enumerate zero cavities with their metadata, pick the partner colour per cavity, then fill the cavity cells accordingly."

## Lambda Representation

```python
def solve_dbff022c(grid: Grid) -> Grid:
    cavities = enumerateZeroCavities(grid)

    def fill(canvas: Grid, component: Component) -> Grid:
        colour = choosePartnerColour(component)
        if colour is None:
            return canvas
        return fillComponent(canvas, component, colour)

    return fold_repaint(grid, cavities, fill)
```
