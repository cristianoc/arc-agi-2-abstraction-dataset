# ARC Task 247ef758 – Abstraction Notes

- **identity** – baseline copy-through; leaves the puzzle unchanged and therefore misses every training output (0/3).
- **gravity_drop** – align left glyphs with top-row markers then drop them vertically; collisions land in the wrong rooms so the idea scores 0/3.
- **border_marker_cartesian** – treat top-row columns and last-column rows as placement beacons, translate each left glyph to every row/column combination, painting lower glyphs first; this hybrid nails all training cases (3/3) and is the final solver.
