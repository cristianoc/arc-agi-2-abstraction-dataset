# ARC Task 136b0064 Abstraction Notes

- `identity_right`: copy the seven columns to the right of the separator without reasoning about the digit patterns. Fails immediately (0/3 train) because it ignores the encoded digits on the left.
- `digit_bars`: detect 3×3 digit glyphs on the left, convert each to a compact bar glyph, and place them in order using directional heuristics that keep the bar chain connected. Matches all training cases and produces coherent test output.

## DSL Structure
- **Typed operations**
  - `splitBlocks : Grid -> List RowRange` — find row intervals containing left-side digits.
  - `extractDigitLists : Grid × List RowRange -> (DigitsLeft, DigitsRight)` — read dominant colours to identify the digit sequence on each side of the separator.
  - `planDigitColumns : Grid × DigitsLeft × DigitsRight -> List Column` — run the placement heuristic that decides starting columns for the combined digit stream.
  - `renderDigits : Grid × List Column × List Digit -> Grid` — paint glyph patterns into the target panel in order.
- **Solver summary**: "Decode digits on the left blocks, plan their column positions via the heuristic, then render the glyph templates sequentially on the right panel."

## Lambda Representation

```python
def solve_136b0064(grid: Grid) -> Grid:
    blocks = splitBlocks(grid)
    left_digits, right_digits = extractDigitLists(grid, blocks)
    sequence = planDigitColumns(grid, left_digits, right_digits)
    return renderDigits(grid, sequence, left_digits + right_digits)
```
