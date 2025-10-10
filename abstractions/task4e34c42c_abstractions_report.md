# Abstraction Report – Task 4e34c42c

- **desc_min_col** – Concatenates normalized components in descending order of their left edge. Works on the first training grid but repeats duplicate columns and fails on train[1] (first failure index 1).
- **type_priority** – Prioritises unique short components, then wide-short strips, and finally tall blocks (with redundant snippets deferred). This composite ordering resolves all overlaps; it matches every train/test sample and keeps arc-gen consistent in our harness.

Final solver uses the `type_priority` ordering, as it alone preserves the asymmetry between the mid and bottom structures while avoiding duplicate columns contributed by redundant fragments.
