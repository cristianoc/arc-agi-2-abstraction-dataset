# Task 9aaea919 – Abstraction Notes

- `identity`: Pass-through baseline that retains the input grid unchanged. It fails immediately on train case 0 (0/3 matches).
- `instruction_driven`: Interprets the bottom-row markers, recolors flagged columns to color 5, and stacks plus-shaped digits according to the counts encoded by the color-2 columns. Achieves 3/3 matches on the train split; generated test output forms a consistent extended scoreboard.

Final choice: `instruction_driven` abstraction.

## DSL Structure
- **Typed operations**
  - `extractCrossColumns : Grid -> ColumnInfoMap` — detect plus-shaped columns (colour 9) and record their positions and row stacks.
  - `readInstructionSegments : Grid -> InstructionSegments` — parse the bottom-row segments to determine colour-coded instructions.
  - `mapInstructionsToColumns : InstructionSegments × ColumnInfoMap -> ColumnInstructionMap` — assign counts and recolour directives to each cross column.
  - `repaintColumn : Grid × ColumnInfo × Instruction -> Grid` — recolour columns flagged for colour 5 and extend columns based on the instruction counts.
  - `clearInstructionSegments : Grid × InstructionSegments × Color -> Grid` — clear the bottom-row instruction markers back to background.
  - `getBackground : Grid -> Color` — infer the background colour as the modal value.
- **Solver summary**: "Detect existing plus columns, read the bottom instructions, map those instructions to the columns, and repaint/extend each column according to its assigned directive."

## Lambda Representation

```python
def solve_9aaea919(grid: Grid) -> Grid:
    columns = extractCrossColumns(grid)
    segments = readInstructionSegments(grid)
    assignments = mapInstructionsToColumns(segments, columns)

    def repaint(canvas: Grid, column_index: ColumnIndex) -> Grid:
        instruction = assignments[column_index]
        column_info = columns[column_index]
        return repaintColumn(canvas, column_info, instruction)

    repainted = fold_repaint(grid, list(assignments.keys()), repaint)
    background = getBackground(grid)
    return clearInstructionSegments(repainted, segments, background)
```
