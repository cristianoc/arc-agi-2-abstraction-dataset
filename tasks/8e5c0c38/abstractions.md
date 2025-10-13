# Task 8e5c0c38 – Abstraction Notes

- `identity`: copied the input grid unchanged; produced 0/2 train matches (first failure at train[0]) so it fails immediately.
- `component_axis_symmetry`: enforced symmetry per connected component; also 0/2 train matches because local axes ignored cross-component structure and left extraneous pixels.
- `global_color_symmetry`: selected a single horizontal mirror axis per color via minimal deletions; 2/2 train matches and generalises cleanly to the test inputs.

Final refinement uses `global_color_symmetry`, which trims the unmatched color pixels relative to the best global axis and yields the official solution.
