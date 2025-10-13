# Task 332f06d7 – Abstraction Summary

- **identity** – left the grid untouched; 0/4 train matches (first failure train[0]).
- **swap_to_color2** – always replaced the zero block with the colour-2 component; 2/4 train matches (first failure train[1]).
- **threshold_5** – relocate the zero block to the most central 1-block candidate whose adjacency covers the colour-2 gap when it improves distance-to-centre by ≥5; 4/4 train matches, no failures observed. Test labels unavailable, but the produced outputs align with the expected structural shift.

The final solver uses the `threshold_5` abstraction.
