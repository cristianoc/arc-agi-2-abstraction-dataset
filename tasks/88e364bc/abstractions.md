# Task 88e364bc – Abstraction Notes

- **identity** – left the grid untouched. Predictably failed on every training case (0/3).
- **directional_slide** – slid each 4 along the axis with a longer zero corridor. Looked promising in inspection but mis-placed every 4 in practice (0/3, first miss at train[0]).
- **block_template** – recognised the 5×5 digit tiles, zeroed all 4s, then reinserted them at the template-specific offsets. This exactly matches all training outputs (3/3) and is the deployed solver.
