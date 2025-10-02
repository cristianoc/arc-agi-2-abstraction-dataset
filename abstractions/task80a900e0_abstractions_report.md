# Task 80a900e0 – Abstraction Notes

- `identity`: left the grid untouched; 0/2 train matches (first failure at train[0]), so it cannot explain any of the diagonal growth.
- `handle_extension_no_guard`: extended perpendicular stripes from every diagonal handle without conflict checks; 2/2 train matches but risks overwriting non-background structure when handles intersect other colours.
- `handle_extension_guarded`: same extension logic while guarding against overwriting non-background cells; 2/2 train matches and is the only safe variant for novel grids.

Final refinement uses `handle_extension_guarded`, yielding the diagonal-stripe propagation required by both training examples and the held-out evaluation grid.
