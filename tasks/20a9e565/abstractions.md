# Abstraction Notes for 20a9e565

- **column_cycle**: modelled the grid as repeating color cycles across consecutive column groups, emitting color/transition pairs (14×2); fit 1/3 train cases and produced reasonable summaries for evaluation inputs.
- **cross_banner**: treated the unique short-width group as a stem to paint a 3-row banner (3×(2·width)) capturing vertical and horizontal bars; solved the cross-like training example only (1/3).
- **alternating_bar**: encoded the first column color as alternating solid and hollow vertical bars (rows = non-zero columns − 1, width 3); matched the “dual-bar” training case (1/3) and yields compact alternations on evaluation inputs.
- **hybrid**: pattern-classifier combining the above three abstractions by repeating-color detection vs. unique-length cues; matches all training samples and generates structured outputs (22×2 and 3×26) for the evaluation inputs.

## DSL Structure
- **Typed operations**
  - `columnGroups : Grid -> (Groups, Count)` — aggregate consecutive non-zero columns by their top colour.
  - `classifyPattern : Groups -> Tag` — classify the column pattern into S/C/B types.
  - `buildTypeS : Groups -> Grid` — construct the type-S template using doubled segments.
  - `buildTypeC : Grid × Groups -> Grid` — build the type-C template using bounding-box widths.
  - `buildTypeB : Groups -> Grid` — create the fallback type-B template (alternating bars).
- **Solver summary**: "Group non-zero columns, classify the pattern, and emit the corresponding template layout (S, C, or B)."

## Lambda Representation

```python
def solve_20a9e565(grid: Grid) -> Grid:
    groups, total_cols = columnGroups(grid)
    tag = classifyPattern(groups)
    
    if tag == "S":
        return buildTypeS(groups)
    elif tag == "C":
        return buildTypeC(grid, groups)
    else:  # tag == "B"
        return buildTypeB(groups)
```
