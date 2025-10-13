# ARC Task 136b0064 Abstraction Notes

- `identity_right`: copy the seven columns to the right of the separator without reasoning about the digit patterns. Fails immediately (0/3 train) because it ignores the encoded digits on the left.
- `digit_bars`: detect 3×3 digit glyphs on the left, convert each to a compact bar glyph, and place them in order using directional heuristics that keep the bar chain connected. Matches all training cases and produces coherent test output.

## DSL Structure
- **Typed operations**
  - `splitBlocks : Grid -> List RowRange` — find row intervals containing left-side digits.
  - `extractDigits : Grid × RowRange -> Digits` — read dominant colours to identify digits on both sides of the separator.
  - `glyphSize : Digit -> (Height, Width)` — fetch glyph dimensions from predefined templates.
  - `planPositions : Digits × AnchorInfo -> List Column` — run the placement heuristic to sequence starting columns.
  - `renderDigits : Grid × List Column × Digits -> Grid` — paint glyph patterns into the target panel in order.
- **Solver summary**: "Decode digits on the left blocks, plan their column positions via the heuristic, then render the glyph templates sequentially on the right panel."
