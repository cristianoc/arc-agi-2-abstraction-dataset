# Abstractions for ARC task 7c66cb00

- `identity`: naive copy-through baseline; leaves noisy legend rows intact and fails on every train case (0/3).
- `clear_prototypes`: blanks any section that still contains the background color, but without stamping masks; this erases the legend yet leaves the lower bands untouched (0/3).
- `stamp_top`: copies legend masks using the edge color but keeps their original vertical offset; figures float too high, so matches still fail (0/3).
- `stamp_bottom`: reuses the legend masks, re-anchoring them to the bottom of each target band before recoloring; hits all train pairs (3/3) and produces plausible test output.
- `final_solver`: module implementation of the bottom-aligned stamping pipeline; mirrors `stamp_bottom` performance (3/3) and is used for submission.
