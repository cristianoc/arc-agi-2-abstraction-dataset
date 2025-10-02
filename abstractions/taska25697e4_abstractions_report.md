# a25697e4 Abstraction Notes

- **fill_anchor_holes** – preserve the dominant component and simply paint the empty slots inside its bounding box with the closest secondary color. This ignores the displaced component, so it solves 0/3 train pairs and fails immediately on train[0].
- **compact_components_v1** – first compaction attempt that projects the third color using a fixed vertical direction. Orientation mistakes break all examples (0/3 train, failure at train[0]).
- **compact_components_final** – refined heuristic that selects the bridge color via row-alignment, then orients the relocated component by scanning both vertical directions against hole statistics. Matches 3/3 train pairs; test has no public labels but this path feeds the production solver.
