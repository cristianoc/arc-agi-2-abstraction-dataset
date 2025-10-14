# Task 58490d8a Abstraction Summary

- `board_copy`: copies the zero-anchored scoreboard rectangle verbatim; 0/3 train matches because it never converts the indicator digits into multiplicities.
- `count4`: repeats each indicator digit using counts of 4-connected components outside the board; 1/3 train matches, under-counting shapes whose structure hinges on diagonal contact.
- `count8`: same counting policy but with 8-connected components, giving 3/3 train matches and the expected test scoreboard (`count8` predicts `0101` / `0202` / `0808` / `0303` bands).

Final pipeline: `count8`.

## DSL Structure
- **Typed operations**
  - `extractScoreboard : Grid -> Grid` — crop the zero-anchored scoreboard rectangle.
  - `enumerateArenaComponents : Grid -> List Component` — find 8-connected components outside the scoreboard region.
  - `countComponentsByColor : List Component -> Dict Color -> Int` — tally components by their indicator colour.
  - `writeCountsToBoard : Grid × Dict Color -> Int -> Grid` — overwrite the scoreboard digits with counts expanded as repeated rows/columns.
- **Solver summary**: "Extract the scoreboard, count 8-connected components per indicator colour, and write those counts back into the board."
