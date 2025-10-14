# Task 7b0280bc Abstraction Notes

- **union_component_tree** – Classified BFS regions built from the union of the two dominant colors. Worked on two train grids but missed bottom subcomponents in case 0 (2/3 matches).
- **color_component_tree** – Switched to monochrome components with a refined tree; perfect on all train grids and used for the final solver. Test prediction inspected via harness and retains the expected 3/5 recoloring pattern.

## DSL Structure
- **Typed operations**
  - `identifyForegroundColours : Grid -> (Color, Color)` — choose the two most frequent non-background colours (major/minor).
  - `extractMonoComponents : Grid × Set Color -> List Component` — flood-fill monochrome components for the selected colours and gather size/bounds features.
  - `evaluateDecisionTree : Component -> Bool` — apply the handcrafted thresholds on colour, size, and position to decide whether to recolour the component.
  - `repaintComponents : Grid × List Component -> Grid` — map qualifying major components to colour 5 and minor components to colour 3.
- **Solver summary**: "Select the two dominant colours, extract their monochrome components, run each through the learned decision tree, and recolour qualifying components."
