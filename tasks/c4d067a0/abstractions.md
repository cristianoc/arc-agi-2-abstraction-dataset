Abstractions explored for task c4d067a0:

- **identity** – leaves the grid untouched; scored 0/3 on train (fails immediately on train[0]) and only serves as a baseline sanity check.
- **global_stack** – extends template blocks using one shared top offset; hits 2/3 on train but misplaces the rightmost column in train[1], showing that columns require independent vertical anchoring.
- **column_aligned** – aligns all columns at the bottom and stacks with the learned spacing; matches 3/3 train cases and provides the final prediction for the evaluation input (test has no released labels for verification).

Final pipeline: adopt the column-aligned abstraction (matching spacing horizontally and vertically, bottom-aligning columns, then colouring according to instruction sequences) to satisfy all observed constraints.
