# Task 62593bfd – Abstraction Notes

- **median_split**: classified each color by comparing its topmost row to the median across colors, then pushed groups to the nearest edge. It cleared the first train puzzle but misclassified the richer second example, so it does not generalise.
- **component_overlap**: compared individual components that share columns and moved the larger one upward. This matches both training outputs but is unstable—when colors have multiple shards in the same columns (e.g., test inputs) it produces conflicting shifts.
- **aggregated_overlap**: aggregates column counts per color before deciding dominance, then resolves leftovers by median min-row placement. This keeps column order, avoids shard conflicts, and matches all training cases; the implemented solver is the code version of this abstraction.
