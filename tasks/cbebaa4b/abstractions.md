# Task cbebaa4b – Abstraction Notes

- **identity** – simple copy baseline to confirm harness wiring; 0/2 on train (stops at train[0]).
- **naive_stack** – detected the solid “door” block and stacked all other shapes above it purely by size; ignores the colour-2 connectors and fails immediately (0/2 train).
- **connector_matching** – treat each non-zero component + its colour-2 spokes as a gadget, pair spokes with opposite directions to recover translation deltas via majority voting, root the resulting graph at the door, and translate every component together with its connectors (with a greedy fallback for stray nodes). Achieves 2/2 on train and is the solver now shipped in `analysis/arc2_samples/cbebaa4b.py`.

The connector graph abstraction also produces plausible layouts on the two test inputs (scoreboard-style assemblies with all connectors engaged).

## DSL Structure
- **Typed operations**
  - `extractGadgetComponents : Grid -> List Gadget` — collect each coloured component with its colour-2 connector spokes.
  - `pairConnectors : List Gadget -> List ConnectorPair` — match spokes with opposite directions to infer translation deltas.
  - `buildConnectorGraph : List Gadget × List ConnectorPair -> Graph` — assemble the gadget connectivity graph rooted at the door block.
  - `applyTranslations : Grid × Graph -> Grid` — translate each gadget according to the graph while moving its connectors.
- **Solver summary**: "Extract gadget components with connectors, pair the connectors to find translation deltas, build the connector graph, and translate each gadget accordingly."

## Lambda Representation

```python
def solve_cbebaa4b(grid: Grid) -> Grid:
    gadgets = extractGadgetComponents(grid)
    pairs = pairConnectors(gadgets)
    graph = buildConnectorGraph(gadgets, pairs)
    return applyTranslations(grid, graph)
```
