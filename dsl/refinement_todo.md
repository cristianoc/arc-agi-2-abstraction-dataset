# DSL Refinement Todo List

The following tasks still rely on bespoke primitives without a shared router/combinator. When resuming the abstraction-review process, work through them and decide whether each primitive should become a parameterised configuration of an existing router or remain a task-specific helper.

## Workflow Instructions

1. For each task below (checkbox list), open its `abstractions.md`.
2. Add a **DSL Structure** section that lists typed operations (with brief type explanations) and a concise solver summary.
3. Update the checklist entry with a one-line status/note.
4. Rerun `python3 dsl/validate_dsl.py` if any DSL/code changes were required.
5. Mark the task as `[x]` once the abstraction file has the typed-operations summary.

## Example

See `tasks/0934a4d8/abstractions.md` for a sample typed-operation + summary entry.

## Pending Tasks

- [x] 0934a4d8 — Core geometry primitives (`bbox`, `crop`, `flip`, `count_color`); keep as foundational helpers.
- [x] 135a2760 — Row slice repair via periodic pattern search (documented in abstractions.md).
- [x] 136b0064 — Digit template placement with placement heuristic.
- [x] 13e47133 — Template lookup/overlay per component.
- [ ] 142ca369
- [x] 16b78196 — Component stacking around dominant band.
- [x] 16de56c4 — Row stride + column stride propagation.
- [x] 1818057f — Plus detection/repaint.
- [x] 195c6913 — Legend palette decode and propagation.
- [x] 1ae2feb7 — Repeat segments across barrier column.
- [x] 20270e3b — Vertical/horizontal fold with fallback recolour.
- [x] 20a9e565 — Column group classification into S/C/B layouts.
- [ ] 21897d95
- [x] 221dfab4 — Stripe projection + object-overlay abstraction captured (see DSL structure note).
- [x] 247ef758 — Marker cartesian placement DSL summary documented.
- [x] 269e22fb — Template alignment with dihedral + colour remap recorded.
- [ ] 271d71e2
- [x] 28a6681f — Supply relocation gaps solver summarised.
- [x] 291dc1e1 — Segment weaving transpose pipeline noted.
- [x] 2b83f449 — Cross repaint + boundary recolour DSL written up.
- [x] 2ba387bc — Hollow/solid pairing blocks abstraction documented.
- [x] 2c181942 — Axis-cross reconstruction DSL summary added.
- [x] 2d0172a1 — Template reconstruction / alternating extension described.
- [x] 31f7f899 — Stripe sorting backbone DSL captured.
- [x] 332f06d7 — Zero-block relocation threshold DSL documented.
- [x] 35ab12c3 — Hull-shift anchor pipeline summarised.
- [x] 36a08778 — Scaffold wrap filtering operations listed.
- [x] 38007db0 — Unique block column partition DSL recorded.
- [x] 3a25b0d8 — Band synthesis typed operations described.
- [x] 3dc255db — Intruder edge push typed ops added.
- [x] 3e6067c3 — Hint-path corridor reconstruction noted.
- [x] 409aa875 — Band lift and centroid marker DSL captured.
- [x] 446ef5d2 — Grid compactor packing DSL documented.
- [x] 45a5af55 — Concentric ring synthesis DSL documented.
- [x] 4a21e3da — Corner projection typed operations captured.
- [x] 4c3d4a41 — Wedge shift + mirror DSL summarised.
- [x] 4c416de3 — Corner hook templating DSL listed.
- [x] 4c7dc4dd — Zero-rectangle scaffold DSL recorded.
- [x] 4e34c42c — Component priority concatenation DSL noted.
- [x] 53fb4810 — Mixed component tiling DSL added.
- [x] 5545f144 — Consensus + alignment DSL captured.
- [x] 581f7754 — Anchor alignment compression DSL described.
- [x] 58490d8a — Scoreboard counting DSL documented.
- [x] 58f5dbd5 — Scoreboard glyph board DSL captured.
- [x] 5961cc34 — Filtered scaffold motif DSL summarised.
- [x] 5dbc8537 — Legend-driven orientation repaint DSL documented.
- [x] 62593bfd — Aggregated overlap shift DSL recorded.
- [x] 64efde09 — Shadow projection DSL added.
- [x] 65b59efc — Template-mapped tile DSL described.
- [x] cb2d8a2c — Corridor orientation routing DSL noted.
- [x] cbebaa4b — Connector graph translation DSL captured.
- [x] d35bdbdc — Sink pairing ring-prune DSL written up.
- [x] d59b0160 — Room fill heuristic DSL detailed.
- [x] d8e07eb2 — Header fingerprint highlight DSL recorded.
- [ ] da515329
- [x] db0c5428 — Macro tiling block DSL summarised.
- [x] db695cfb — Diagonal bridge + 6 propagation DSL captured.
- [x] dbff022c — Zero-cavity partner fill DSL added.
- [x] dd6b8c4b — Ring relocation scoring DSL documented.
- [x] de809cff — Halo expansion/prune DSL listed.
- [x] dfadab01 — Patch dictionary tiling DSL described.
- [x] e12f9a14 — Digit seed variant DSL captured.
- [x] e3721c99 — Hole-classified recolour DSL added.
- [x] e376de54 — Median line alignment DSL noted.
- [x] e8686506 — Row-signature lookup DSL documented.
- [x] e87109e9 — Header diff-mask scoreboard DSL captured.
- [x] edb79dae — Legend template decode DSL summarised.
- [x] eee78d87 — Template selection DSL recorded.
- [x] f560132c — Component rotation/placement DSL detailed.
- [x] f931b4a8 — Tile row/column ID DSL noted.
- [x] faa9f03d — Noise-bridge tail pipeline DSL described.
- [x] fc7cae8d — Component rotate/mirror DSL added.
- [x] aa4ec2a5 — Hole-aware framing DSL recorded.
- [x] abc82100 — kNN feature encoding DSL documented.
- [x] b0039139 — Segment tiling reconstruction DSL summarised.
- [x] b10624e5 — Ornament template reconstruction DSL captured.
- [x] b5ca7ac4 — Ring lane packing DSL added.
- [x] b6f77b65 — Digit segment template DSL recorded.
- [x] b99e7126 — Minority tile mask DSL noted.
- [x] b9e38dc0 — Barrier wedge propagation DSL described.
- [x] bf45cf4b — Mask tiling DSL documented.
- [x] c4d067a0 — Column-aligned stacking DSL captured.
- [x] c7f57c3e — Variant switch recolour DSL written up.
- [x] 67e490f4 — Motif shape recolour DSL summarised.
- [x] 6e453dd6 — Zero-slide + highlight DSL added.
- [x] 6e4f6532 — Template stamping DSL documented.
- [x] 6ffbe589 — Variant rotation DSL recorded.
- [x] 71e489b6 — Tip halo DSL summarised.
- [x] 7491f3cf — Panel overlay DSL captured.
- [x] 7666fa5d — Diagonal corridor DSL noted.
- [x] 78332cb0 — Block rotation stack DSL written up.
- [x] 7b0280bc — Component decision-tree DSL added.
- [x] 7b3084d4 — DFS tiling DSL documented.
- [x] 7b5033c1 — Histogram column DSL recorded.
- [x] 7b80bb43 — Column snap refinement DSL described.
- [x] 7c66cb00 — Bottom-stamp prototype DSL captured.
- [x] 7ed72f31 — Axis reflection DSL noted.
- [x] 800d221b — Heuristic + kNN recolour DSL summarised.
- [x] 80a900e0 — Diagonal handle extension DSL added.
- [x] 8698868d — Tile assignment DSL recorded.
- [x] 88bcf3b4 — Path projection DSL detailed.
- [x] 88e364bc — Digit template relocation DSL noted.
- [x] 89565ca0 — Stripe summary DSL described.
- [x] 898e7135 — Dynamic upscale DSL captured.
- [ ] 8b7bacbf
- [ ] 8b9c3697
- [ ] 8e5c0c38
- [ ] 8f215267
- [ ] 8f3a5a89
- [ ] 9385bd28
- [ ] 97d7923e
- [ ] 981571dc
- [ ] 9aaea919
- [ ] 9bbf930d
- [ ] a251c730
- [ ] a25697e4
- [ ] a32d8b75
- [ ] a395ee82
- [ ] a47bf94d
- [ ] a6f40cea
