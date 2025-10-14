# ARC Task 247ef758 – Abstraction Notes

- **identity** – baseline copy-through; leaves the puzzle unchanged and therefore misses every training output (0/3).
- **gravity_drop** – align left glyphs with top-row markers then drop them vertically; collisions land in the wrong rooms so the idea scores 0/3.
- **border_marker_cartesian** – treat top-row columns and last-column rows as placement beacons, translate each left glyph to every row/column combination, painting lower glyphs first; this hybrid nails all training cases (3/3) and is the final solver.

## DSL Structure
- **Typed operations**
  - `findAxisColumn : Grid -> Optional Column` — locate the separator column whose values are constant and non-zero.
  - `extractGlyphs : Grid × Column -> GlyphMap` — collect each left-side glyph keyed by colour.
  - `extractColumnMarkers : Grid × Column -> ColumnMarkerMap` — read top-row markers to determine target columns per colour.
  - `extractRowMarkers : Grid -> RowMarkerMap` — read last-column markers to determine target rows per colour.
  - `placeGlyphs : Grid × Glyph × List Row × List Column -> Grid` — clear the source glyph and stamp it at every row/column combination via its offsets.
- **Solver summary**: "Find the axis column, extract each coloured glyph, read its row/column markers from the borders, then place the glyph at every marker combination."

## Lambda Representation

```python
def solve_247ef758(grid: Grid) -> Grid:
    axis_col = findAxisColumn(grid)
    if axis_col is None:
        return grid
    
    glyphs = extractGlyphs(grid, axis_col)
    col_markers = extractColumnMarkers(grid, axis_col)
    row_markers = extractRowMarkers(grid)
    glyph_entries = list(glyphs.items())
    
    def place(canvas: Grid, entry: Tuple[Color, Glyph]) -> Grid:
        color, glyph = entry
        return placeGlyphs(canvas, glyph, row_markers[color], col_markers[color])
    
    return fold_repaint(grid, glyph_entries, place)
```
