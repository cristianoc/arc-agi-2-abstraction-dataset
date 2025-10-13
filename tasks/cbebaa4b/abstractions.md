# Task cbebaa4b – Abstraction Notes

- **identity** – simple copy baseline to confirm harness wiring; 0/2 on train (stops at train[0]).
- **naive_stack** – detected the solid “door” block and stacked all other shapes above it purely by size; ignores the colour-2 connectors and fails immediately (0/2 train).
- **connector_matching** – treat each non-zero component + its colour-2 spokes as a gadget, pair spokes with opposite directions to recover translation deltas via majority voting, root the resulting graph at the door, and translate every component together with its connectors (with a greedy fallback for stray nodes). Achieves 2/2 on train and is the solver now shipped in `analysis/arc2_samples/cbebaa4b.py`.

The connector graph abstraction also produces plausible layouts on the two test inputs (scoreboard-style assemblies with all connectors engaged).
