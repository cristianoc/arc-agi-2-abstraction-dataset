# Task 7491f3cf – Abstraction Report

- **copy_left** – Mirrors the left panel into the blank area. Fails on all cases because it never adds the cross/diagonal features required in the target digits.
- **cross_overlay** – Applies the cross-armed overlay using directional heuristics. Solves the diamond/cross layouts (4/5) but breaks on the block-style case where the template differs.
- **block_template** – Stamps a hard-coded block pattern; handles the block example but misses others (2/5).
- **final_solver** – Chooses between cross-overlay and block template based on panel shapes; passes all provided examples (5/5) and is used for submission.

## DSL Structure
- **Typed operations**
  - `extractPanels : Grid -> (Grid, Grid, Grid)` — identify border columns and slice the left, centre, and right panels.
  - `classifyPanelShape : Grid -> ShapeId` — reduce each panel to its interior mask and recognise cross/diamond/block variants.
  - `chooseTemplate : ShapeId × ShapeId -> TemplateId` — select the overlay routine (cross subset vs. block template) based on panel pairings.
  - `renderTemplatePanel : TemplateId × Grid × Grid -> Grid` — apply the chosen overlay, preserving borders and copying accents to form the final panel.
- **Solver summary**: "Slice the panels, classify their interior shapes, pick the appropriate overlay template, and render that template into the output panel before copying it to the right section."

## Lambda Representation

```python
def solve_7491f3cf(grid: Grid) -> Grid:
    left, centre, right = extractPanels(grid)
    left_shape = classifyPanelShape(left)
    centre_shape = classifyPanelShape(centre)
    template = chooseTemplate(left_shape, centre_shape)
    rendered = renderTemplatePanel(template, left, centre)
    return renderTemplatePanel(template, rendered, right)
```
