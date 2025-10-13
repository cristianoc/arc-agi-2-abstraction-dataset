# Task 7b0280bc Abstraction Notes

- **union_component_tree** – Classified BFS regions built from the union of the two dominant colors. Worked on two train grids but missed bottom subcomponents in case 0 (2/3 matches).
- **color_component_tree** – Switched to monochrome components with a refined tree; perfect on all train grids and used for the final solver. Test prediction inspected via harness and retains the expected 3/5 recoloring pattern.
