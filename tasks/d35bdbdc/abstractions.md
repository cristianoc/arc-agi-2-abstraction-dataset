d35bdbdc abstraction summary
============================

- identity: left the grid unchanged; fails all train cases (0/3) because the task expects selective pruning of ring gadgets.
- propagate_without_sinks: rewired ring centres via a simple colour map; hits wrong targets on every train case (0/3) due to keeping rings that should be deleted.
- sink_pairing: iteratively keeps rings whose border colour no longer appears as a centre, pairing them with donors and zeroing the rest; matches all train samples (3/3) and is stable on test inputs.
- final solver: same sink-based pairing as above, reused as the production solver; test predictions (three grids) keep the paired ring colours while pruning the others, matching the observed pattern.

## DSL Structure
- **Typed operations**
  - `extractRingGadgets : Grid -> List Ring` — gather ring centres with their border colours.
  - `countBorderOccurrences : List Ring -> Dict Color -> Int` — tally how many times each border colour appears as a centre.
  - `selectSinkPairs : List Ring × Dict Color -> List Pair` — pick rings whose border colours no longer appear as centres and pair them with donors.
  - `pruneRings : Grid × List Ring × List Pair -> Grid` — zero out unpaired rings and preserve the selected sink pairs.
- **Solver summary**: "Extract ring gadgets, count border occurrences, select sink pairs where border colours have no remaining centres, and prune the rest."
