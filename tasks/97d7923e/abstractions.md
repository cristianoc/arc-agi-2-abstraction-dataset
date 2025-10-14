# ARC task 97d7923e abstractions

- **identity** – left grids untouched; matches 0/3 train examples (first fail at train[0]) so unusable as a solver.
- **naive_column_fill** – fills every sandwiched column; fixes the missing column at train[0] but over-fills others (first fail train[0]) showing the need for contextual checks.
- **selective_cap_fill** – keeps the naive fill machinery but adds guards for upstream caps, tall mid runs at row 3, and right-edge thin towers; matches 3/3 train examples and is used for the final solver and test prediction.

## DSL Structure
- **Typed operations**
  - `parseColumnRuns : Grid -> ColumnRuns` — for each column, compute colour runs with lengths and start rows.
  - `detectCapPattern : List Run -> Optional CapPattern` — identify top/mid/bottom runs where top and bottom colours match and the middle is zero.
  - `applyFillGuards : ColumnIndex × CapPattern -> Bool` — evaluate heuristics (upstream caps, row-3 tall runs, right-edge towers) to decide whether to fill the middle run.
  - `paintColumnRun : Grid × ColumnIndex × Run × Color -> Grid` — recolour qualifying middle runs with the cap colour.
- **Solver summary**: "Parse column runs, find zero runs sandwiched by matching caps, keep only those that pass the learned guards, and paint the middle runs with the cap colour."

## Lambda Representation

```python
def solve_97d7923e(grid: Grid) -> Grid:
    column_runs = parseColumnRuns(grid)
    entries = list(column_runs.items())

    def repaint(canvas: Grid, entry):
        column_index, runs = entry
        pattern = detectCapPattern(runs)
        if pattern is None:
            return canvas
        top, middle, bottom = pattern
        if not applyFillGuards(column_index, pattern):
            return canvas
        return paintColumnRun(canvas, column_index, middle, top.color)

    return fold_repaint(grid, entries, repaint)
```
