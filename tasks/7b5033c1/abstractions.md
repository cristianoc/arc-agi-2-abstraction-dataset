# ARC Task 7b5033c1 – Abstraction Notes

- **area_sorted** – order colours by descending area before emitting counts. Misses the intended vertical sequencing and fails on train[0] (train 0/2).
- **top_row** – order colours by the (row, column) of their first occurrence and emit `count` copies vertically. Matches all labelled data (train 2/2; test unchecked) while producing the expected-looking test column.
- **final** – same as `top_row`; kept as the solver because it obeys the observed monotone top-to-bottom ordering and cleanly generalises (train 2/2; test prediction `[1×8, 3×5, 8×6, 4×6]`).

## DSL Structure
- **Typed operations**
  - `tallyColours : Grid -> Counter` — count occurrences of every colour.
  - `findFirstPosition : Grid -> Dict Color -> (Row, Col)` — record the first (row, column) where each colour appears.
  - `orderColoursByFirstSeen : Counter × Dict -> List (Color, Int)` — sort non-background colours by their first position and retain their counts.
  - `buildHistogramColumn : List (Color, Int) -> Grid` — expand each colour into a vertical run equal to its count to form the output column.
- **Solver summary**: "Count colours, track the earliest appearance of each one, sort by that position, and build the vertical histogram column in that order."
