# Abstraction Notes for Task 8b7bacbf

- **identity** – Leave the grid untouched. Accuracy: `train 0/4`; `test –` (no targets). Fails immediately because all training outputs add new colour-4/7 patches.
- **fill_all_enclosed** – Paint every uniquely bounded zero cavity with the max colour. Accuracy: `train 1/4`; `test –`. Captures the obvious 5- and 3-bounded holes but over-fills the small 2-bounded cavities near the top.
- **distance_filtered_fill** – Only fill cavities whose enclosing colour is close to a frequent, informative colour (≤4 if higher than the border, else ≤3). Accuracy: `train 4/4`; `test –`. This selective distance gate matches all available cases and is used in the submitted solver.

No arc-gen fixtures are provided for this task; the harness therefore reports only train/test splits.
