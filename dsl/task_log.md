# DSL Task Log

This file tracks observations while surveying ARC tasks to evolve the abstraction-composition DSL.

## Log Format
- `task`: ARC task identifier.
- `summary`: short description of the solver's structure.
- `dsl`: tentative DSL sketch using current primitives/combinators.
- `gaps`: missing primitives/combinators or refinements needed.
- `actions`: updates to DSL state (if any).

Each entry appends to the end of this file in chronological order.

## Entries
- task: 0934a4d8
  summary: "Mirror the 8-block across horizontal/vertical axes with offset=2, choose orientation by distance and 8-count heuristics."
  dsl: |
    let region = bbox(color=8)
    let block = crop(region)
    let candidate_h = reflect_offset(region, axis="vertical", offset=2)
    let candidate_v = reflect_offset(region, axis="horizontal", offset=2)
    branch(dist(candidate_h) > dist(candidate_v),
           flip(candidate_h.block, axis="vertical"),
           branch(dist(candidate_v) > dist(candidate_h),
                  flip(candidate_v.block, axis="horizontal"),
                  branch(count_color(candidate_v.block, 8) < count_color(candidate_h.block, 8),
                         flip(candidate_v.block, axis="horizontal"),
                         flip(candidate_h.block, axis="vertical"))))
  gaps: "Needed primitives for bbox/crop/reflect_offset/flip and branch combinator; added them to DSL."
  actions: "Introduced bbox, crop, reflect_offset, flip, count_color primitives and branch combinator."
- task: 135a2760
  summary: "Repair each inner row segment by inferring the dominant repeating pattern bounded by period ≤6, respecting frame colors."
  dsl: |
    let border = grid[0][0]
    let walkway = grid[1][1]
    foreach row in grid:
      let inner = strip(row, exclude={border, walkway})
      let pattern = periodic_majority(inner, max_period=6)
      write(inner, pattern)
    return grid
  gaps: "Required a combinator to iterate rows and a primitive to infer periodic-majority patterns."
  actions: "Added foreach combinator and periodic_majority primitive."
- task: 136b0064
  summary: "Decode digit bars from left blocks, then repaint compact glyphs on the right panel following continuity heuristics."
  dsl: |
    let blocks = segment_rows(left_panel, predicate=nonzero)
    let digits_left = [majority_color(block ∩ cols(0..2)) for block in blocks if any]
    let digits_right = [majority_color(block ∩ cols(4..6)) for block in blocks if any]
    let digits = digits_left ++ digits_right
    let anchor = first_nonzero(right_panel.top_row)
    let placements = plan_chain(digits, anchor, width=7, continuity=right_panel)
    let row_cursor = 1
    foreach (digit, start) in zip(digits, placements):
      let glyph = template_lookup(digit)
      overlay(glyph, canvas=right_panel, row=row_cursor, col=start)
      row_cursor += glyph.height
    return right_panel
  gaps: "Needed primitives for segmenting contiguous row blocks, majority-color voting, template lookup, and overlay."
  actions: "Added segment_rows, majority_color, template_lookup, and overlay primitives."
- task: 13e47133
  summary: "Detect colored anchors for glyphs and overlay prelearned templates using color- and size-specific offsets."
  dsl: |
    let bg = background_color(grid)
    let comps = components(grid, exclude=bg)
    let canvas = copy(grid)
    foreach comp in comps:
      let key = (comp.color, grid.height, comp.size)
      let offset = choose_offset(comp, templates[key])
      branch(offset is not None,
             overlay(template_lookup(key, offset), canvas, start=comp.min + offset),
             skip)
    return canvas
  gaps: "Needed a primitive to enumerate connected components; other logic handled via existing branch/overlay/template lookup."
  actions: "Added components primitive."
- task: 142ca369
  summary: "Identity placeholder; no abstraction applied."
  dsl: |
    return copy(grid)
  gaps: "None — baseline identity fits within core language features."
  actions: "None."
- task: 16b78196
  summary: "Keep the dominant strip in place, then stack wide and narrow components around it following width-ordered towers."
  dsl: |
    let comps = components(grid, exclude=0)
    let dominant = max(comps, key=size)
    let wide = sort([c for c in comps if c != dominant and c.width >= 5], key=(top, -left))
    let narrow = order_narrow([c for c in comps if c != dominant and c.width < 5])
    let canvas = zeros_like(grid)
    overlay(dominant, canvas, offset=(0,0))
    stack_components(wide, anchor=dominant, above=True, column≈4)
    stack_components(narrow, anchor=dominant, above=False, column≈mean_left(narrow))
    return canvas
  gaps: "Needed a primitive to express controlled stacking of components relative to an anchor."
  actions: "Added stack_components primitive (overlay already covers component placement)."
- task: 16de56c4
  summary: "First extend row-wise progressions, then propagate column-wise strides using the original as reference."
  dsl: |
    let after_rows = propagate_stride(grid, axis="row", reference=grid)
    let after_cols = propagate_stride(after_rows, axis="column", reference=grid)
    return after_cols
  gaps: "Needed a primitive capturing gcd-based stride propagation along rows/columns."
  actions: "Added propagate_stride primitive."
- task: 1818057f
  summary: "Recolor every 4-colored plus motif into color 8 without interference between updates."
  dsl: |
    foreach center in match_kernel(pattern="plus", color=4):
      recolor(center, 8)
      foreach arm in neighbors(center, von_neumann=True):
        recolor(arm, 8)
    return grid
  gaps: "Needed a kernel-matching primitive for plus detection."
  actions: "Added match_kernel primitive."
- task: 195c6913
  summary: "Read a legend palette, rebuild the row pattern, and propagate it through fill regions with capped boundaries."
  dsl: |
    let comps = components(grid)
    let palette = sort([c for c in comps if c.size == 4 and near_top(c)], key=left_edge)
    let pattern = [c.color for c in palette]
    let fill_color = max_color(not in pattern, by_area=comps)
    let cap_color = next_color(not in {pattern, fill_color})
    clear_cells(palette + smallest_component(cap_color))
    let anchors = detect_anchor_rows(grid, pattern, fill_color)
    foreach anchor in anchors:
      tile_row(anchor, pattern, fill_color, cap_color)
    propagate_pattern(pattern, anchors, fill_color, cap_color, directions={"up","down"})
    return grid
  gaps: "Needed a primitive abstracting the legend-driven propagation once anchors and colors are known."
  actions: "Added propagate_pattern primitive."
- task: 1ae2feb7
  summary: "For each row, reflect non-zero segments across the barrier of 2s, repeating them with their intrinsic spacing."
  dsl: |
    foreach row in grid:
      repeat_segments(row, barrier_color=2)
    return grid
  gaps: "Needed an explicit primitive capturing barrier-based segment repetition."
  actions: "Added repeat_segments primitive."
- task: 20270e3b
  summary: "Try folding across a background column, otherwise remove the special band horizontally, else recolor specials."
  dsl: |
    first_success([
      fold_overlay(grid, axis="vertical", separator_color=BG, special=SPECIAL, fill=FILL),
      band_glue(grid, axis="horizontal", special=SPECIAL, fill=FILL),
      recolor(grid, {SPECIAL: FILL})
    ])
  gaps: "Required primitives for fold overlay and band gluing, plus a combinator to pick the first succeeding pipeline."
  actions: "Added fold_overlay, band_glue, recolor primitives and first_success combinator."
- task: 20a9e565
  summary: "Group non-zero columns, classify the pattern, and render the corresponding layout template."
  dsl: |
    let groups = segment_columns(grid, ignore=0)
    dispatch(classify_column_pattern(groups),
             {
               "S": render_column_pattern("S", groups, grid),
               "C": render_column_pattern("C", groups, grid),
               "B": render_column_pattern("B", groups, grid)
             })
  gaps: "Needed primitives for column grouping, pattern classification, and rendering; plus a dispatch combinator."
  actions: "Added segment_columns, classify_column_pattern, render_column_pattern primitives and dispatch combinator."
- task: 21897d95
  summary: "Identity baseline; no abstraction beyond copying input."
  dsl: |
    return copy(grid)
  gaps: "None."
  actions: "None."
- task: 221dfab4
  summary: "Color 4 stripes follow a 6-row period; add 3 overlays on mod-0 rows where objects appear."
  dsl: |
    stripe_projection(grid, stripe_color=4, period=6, palette={0:3, 2:4, 4:4, _:background})
    overlay_object_rows(grid, period=6, phase=0, overlay_color=3, ignore_color=4)
    return grid
  gaps: "Needed primitives for stripe projection and row overlays keyed to modular indices."
  actions: "Added stripe_projection and overlay_object_rows primitives."
- task: 247ef758
  summary: "Use the constant-axis column to split glyphs, then place each color onto every row/column beacon combination."
  dsl: |
    let axis = detect_axis_column(grid)
    let row_markers = extract_markers(grid, side="right_column")
    let col_markers = extract_markers(grid, side="top_row", start=axis+1)
    cartesian_project(grid, axis=axis, row_markers=row_markers, col_markers=col_markers, order="bottom_first")
    return grid
  gaps: "Needed primitives to detect the axis column, gather border markers, and execute the cartesian placement."
  actions: "Added detect_axis_column, extract_markers, and cartesian_project primitives."
- task: 269e22fb
  summary: "Align the input inside the canonical 20×20 template with dihedral transforms and optional color swap, then invert back."
  dsl: |
    let align = align_template(grid, template=BASE_PATTERN, allow_color_swap=True)
    let filled = template_fill(BASE_PATTERN, align)
    let unaligned = apply_transform(filled, align.inverse_transform)
    return remap_colors(unaligned, align.reverse_mapping)
  gaps: "Needed alignment, template embedding, transform application, and color remapping primitives."
  actions: "Added align_template, template_fill, apply_transform, and remap_colors primitives."
- task: 271d71e2
  summary: "Identity baseline; no abstraction applied."
  dsl: |
    return copy(grid)
  gaps: "None."
  actions: "None."
- task: 28a6681f
  summary: "Collect color-1 supply, identify bounded zero gaps, and greedily relocate supply into bottom-right candidates."
  dsl: |
    let candidates = bounded_gap_candidates(grid, order="bottom_right")
    relocate_supply(grid, supply_color=1, supply_order="top_left", candidates=candidates, color=1)
    return grid
  gaps: "Needed primitives to enumerate bounded gaps and perform the greedy relocation."
  actions: "Added bounded_gap_candidates and relocate_supply primitives."
- task: 291dc1e1
  summary: "Normalize orientation, strip headers, extract row segments, then weave them in column-first order with edge-aware reversal."
  dsl: |
    let oriented, transposed = normalize_orientation(grid, prefer="wide")
    let segments = extract_row_segments(oriented, background=8, header_colors={0,1,2})
    let groups = group_contiguous_rows(segments)
    let woven = weave_segments(groups, segments, transposed=transposed, reverse_on_right_edge=True)
    return woven
  gaps: "Needed primitives for orientation normalization, segment extraction, grouping, and weaving."
  actions: "Added normalize_orientation, extract_row_segments, group_contiguous_rows, and weave_segments primitives."
- task: 2b83f449
  summary: "Convert every horizontal run of three 7s into a cross of 6s and recolor boundary 8s to 3 based on zero-distance heuristics."
  dsl: |
    let cross_base = paint_cross_runs(grid, source_color=7, arm_color=6, filler_color=8, length=3)
    return boundary_recolor(grid, base=cross_base, zero_metrics=True, boundary_color=3)
  gaps: "Needed primitives that encapsulate the cross painting and the nuanced boundary recolor logic."
  actions: "Added paint_cross_runs and boundary_recolor primitives."
- task: 2ba387bc
  summary: "Split components into hollow/solid, pair them, resample to 4×4 blocks, and concatenate each pair side by side."
  dsl: |
    let comps = components(grid)
    let hollows, solids = split_components_by_hollowness(comps)
    let pairs = pair_components(hollows, solids)
    return concat_blocks(pairs, block_size=4)
  gaps: "Needed primitives to partition by hollowness, pair components, resample to canonical blocks, and concatenate results."
  actions: "Added split_components_by_hollowness, pair_components, canonical_block, and concat_blocks primitives."
- task: 2c181942
  summary: "Detect the axis, choose vertical colors, normalize rows, and paint cross arms with the special top-row flare."
  dsl: |
    return axis_cross_reconstruction(grid, background=8)
  gaps: "Encapsulated the full axis-cross reasoning in a dedicated primitive."
  actions: "Added axis_cross_reconstruction primitive."
- task: 2d0172a1
  summary: "Derive accent bbox, choose the matching template family, and optionally extend alternating rows into the right margin."
  dsl: |
    return template_reconstruction(grid)
  gaps: "Captured the template selection and continuation rule inside a single primitive."
  actions: "Added template_reconstruction primitive."
- task: 31f7f899
  summary: "Find the dense center row, measure stripe heights, sort them, and repaint columns to increase monotonically."
  dsl: |
    return sorted_stripes(grid)
  gaps: "Encapsulated the stripe measurement and redistribution logic in a primitive."
  actions: "Added sorted_stripes primitive."
- task: 332f06d7
  summary: "Use colour-2 adjacency cues to decide where the zero block should move, promoting it only when the center distance improves."
  dsl: |
    return relocate_zero_block(grid, threshold=5)
  gaps: "Needed a primitive capturing the adjacency-based relocation heuristic."
  actions: "Added relocate_zero_block primitive."
- task: 35ab12c3
  summary: "Build hulls for multi-point colors and shift them to cover singleton colors without overlapping the base."
  dsl: |
    return hull_shift(grid)
  gaps: "Encapsulated hull building and singleton shifts inside a dedicated primitive."
  actions: "Added hull_shift primitive."
- task: 36a08778
  summary: "Extend top scaffolds and wrap only those 2-runs touched by the scaffold with a one-cell halo."
  dsl: |
    return scaffold_wrap(grid, scaffold_color=6, run_color=2, halo_color=6, filler_color=7)
  gaps: "Needed a primitive summarising the scaffold extension and selective halo logic."
  actions: "Added scaffold_wrap primitive."
- task: 38007db0
  summary: "Segment the interior into border-delimited blocks and keep the unique block in each block-row."
  dsl: |
    return unique_block_column(grid)
  gaps: "Captured the block segmentation and uniqueness test in a dedicated primitive."
  actions: "Added unique_block_column primitive."
- task: 3a25b0d8
  summary: "Crop to interesting bands, adjust row patterns (7/4/3/6 tweaks), and synthesize duplicated rows."
  dsl: |
    return band_synthesis(grid)
  gaps: "Encapsulated the band-specific heuristics and row duplication into a single primitive."
  actions: "Added band_synthesis primitive."
- task: 3dc255db
  summary: "Identify intruder components inside hosts and push them to the edge opposite their drift vector."
  dsl: |
    return intruder_edge_push(grid)
  gaps: "Added a primitive for centroid-based edge relocation."
  actions: "Introduced intruder_edge_push primitive."
- task: 3e6067c3
  summary: "Read the hint row ordering and paint straight corridors between successive nodes."
  dsl: |
    return hint_path(grid)
  gaps: "Captured the path-following corridor painting in a dedicated primitive."
  actions: "Added hint_path primitive."
- task: 409aa875
  summary: "Lift components upward by fixed rows, normalize their columns, and drop centroid markers with recoloring."
  dsl: |
    return centroid_projection(grid, shift_rows=5)
  gaps: "Needed a primitive for centroid-driven projection and recoloring."
  actions: "Added centroid_projection primitive."
- task: 446ef5d2
  summary: "Compact each color's components into a near-square grid and center the assembled rectangle with borders."
  dsl: |
    return grid_compactor(grid)
  gaps: "Added a primitive for component compaction and border centering."
  actions: "Introduced grid_compactor primitive."
- task: 45a5af55
  summary: "Drop the trailing axis stripe and map the remaining colors to concentric rings."
  dsl: |
    return stripe_rings(grid)
  gaps: "Needed a primitive to translate stripes into square rings."
  actions: "Added stripe_rings primitive."
- task: 4a21e3da
  summary: "Use border sentinels to decide which parts of the 7-component to project into each corner and lay connecting rays."
  dsl: |
    return corner_projection(grid)
  gaps: "Captured the sentinel-guided corner mirroring into a single primitive."
  actions: "Added corner_projection primitive."
- task: 4c3d4a41
  summary: "Shift right blocks upward where left wedge 5s persist, then mirror the wedge onto the right." 
  dsl: |
    return wedge_mirror_shift(grid)
  gaps: "Needed a primitive combining conditional vertical copy with mirrored wedge stamping."
  actions: "Added wedge_mirror_shift primitive."
- task: 4c416de3
  summary: "Detect zero-framed blocks, classify corner markers, and paint the corresponding hook patterns." 
  dsl: |
    return corner_hooks(grid)
  gaps: "Required a primitive for marker-based corner hook selection."
  actions: "Added corner_hooks primitive."
- task: 4c7dc4dd
  summary: "Detect large zero components and compress them into a coarse glyph with highlighted axes and rare color anchor."
  dsl: |
    return zero_component_glyph(grid)
  gaps: "Added a primitive for zero-based glyph reconstruction."
  actions: "Introduced zero_component_glyph primitive."
- task: 4e34c42c
  summary: "Classify components by size/type, normalize them, and concatenate using priority ordering while dropping redundant snippets."
  dsl: |
    return type_priority_compactor(grid)
  gaps: "Needed a primitive for type-aware component compaction with redundancy filtering."
  actions: "Added type_priority_compactor primitive."
- task: 53fb4810
  summary: "Identify mixed {2,4} components and tile their pattern upward to the top." 
  dsl: |
    return mixed_component_tiling(grid)
  gaps: "Introduced a primitive for mixed-color component tiling." 
  actions: "Added mixed_component_tiling primitive."
- task: 5545f144
  summary: "Compute consensus highlight columns across repeated segments and align exceptional rows with special two-segment rules." 
  dsl: |
    return segment_consensus(grid)
  gaps: "Needed a primitive encapsulating consensus-based segment aggregation." 
  actions: "Added segment_consensus primitive."
- task: 581f7754
  summary: "Align components to shared anchor columns/rows and refine row targets with drift-aware adjustments." 
  dsl: |
    return full_alignment(grid)
  gaps: "Captured the column anchoring plus row compression in one primitive." 
  actions: "Added full_alignment primitive."
- task: 58490d8a
  summary: "Count 8-connected components outside the zero scoreboard and write the totals across the rows." 
  dsl: |
    return scoreboard_count8(grid)
  gaps: "Added a primitive for scoreboard component counting." 
  actions: "Introduced scoreboard_count8 primitive."
- task: 58f5dbd5
  summary: "Cluster salient colors, choose a grid arrangement, and render per-slot 5×5 glyphs." 
  dsl: |
    return color_scoreboard(grid)
  gaps: "Needed a primitive to drive layout and glyph rendering." 
  actions: "Added color_scoreboard primitive."
- task: 5961cc34
  summary: "Filter motifs with paired guides, cast rays, and flood-fill the sentinel-connected scaffold." 
  dsl: |
    return filtered_scaffold(grid)
  gaps: "Required a primitive for sentinel-led scaffold construction." 
  actions: "Added filtered_scaffold primitive."
- task: 5dbc8537
  summary: "Detect the instruction block orientation and apply the corresponding palette to recolour runs." 
  dsl: |
    return hybrid_palette(grid)
  gaps: "Needed a primitive that dispatches between horizontal and vertical palettes." 
  actions: "Added hybrid_palette primitive."
- task: 62593bfd
  summary: "Aggregate column overlaps to decide which colors move to top or bottom, then translate components accordingly." 
  dsl: |
    return aggregated_overlap(grid)
  gaps: "Required a primitive for overlap-driven vertical reassignment." 
  actions: "Added aggregated_overlap primitive."
- task: 64efde09
  summary: "Cast alternating vertical and horizontal shadows based on component bounding boxes." 
  dsl: |
    return shadow_projection(grid)
  gaps: "Needed a primitive for combined shadow casting passes." 
  actions: "Added shadow_projection primitive."
- task: 65b59efc
  summary: "Segment the board by 5-separators and fill each cell via template lookup with fallback dominant tiles." 
  dsl: |
    return mapped_tiles(grid)
  gaps: "Introduced a primitive for separator-based template mosaics." 
  actions: "Added mapped_tiles primitive."
- task: d8e07eb2
  summary: "Highlight digit blocks via header classification, column fingerprints, and priority fallbacks." 
  dsl: |
    return priority_digit_highlight(grid)
  gaps: "Needed a primitive orchestrating header analysis, fingerprint matching, and fallback block painting." 
  actions: "Added priority_digit_highlight primitive."
- task: da515329
  summary: "Identity placeholder used while no abstraction was discovered." 
  dsl: |
    return grid
  gaps: "None — identity baseline covers the current solver." 
  actions: "None."
- task: db0c5428
  summary: "Lift 3×3 digit blocks into a 5×5 macro layout using dual ring colours and centre inference." 
  dsl: |
    return macro_dual_ring_tiling(grid)
  gaps: "Needed a primitive for macro tiling with corner/edge colour reconciliation." 
  actions: "Added macro_dual_ring_tiling primitive."
- task: db695cfb
  summary: "Bridge matching 1-components along diagonals and extend embedded 6s perpendicularly." 
  dsl: |
    return diagonal_connect_extend(grid, primary=1, extender=6)
  gaps: "Required a primitive to connect diagonal anchors and propagate extender colours across orthogonal diagonals." 
  actions: "Added diagonal_connect_extend primitive."
- task: dbff022c
  summary: "Fill zero cavities with partner colours based on boundary colour, size, and adjacency rules." 
  dsl: |
    return partner_cavity_fill(grid)
  gaps: "Needed a primitive encapsulating zero-component analysis with colour-partner heuristics." 
  actions: "Added partner_cavity_fill primitive."
- task: dd6b8c4b
  summary: "Rebalance colour-9 tiles by promoting ring positions and retiring scattered ones via scoring." 
  dsl: |
    return balanced_ring_relocation(grid, color=9)
  gaps: "Required a primitive that scores scattered tiles and moves them into the ring to match imbalance counts." 
  actions: "Added balanced_ring_relocation primitive."
- task: de809cff
  summary: "Expand halos around strong zero pockets, realign secondary pixels, and prune stragglers." 
  dsl: |
    return halo_realign_prune(grid)
  gaps: "Needed a primitive combining halo expansion, majority realignment, and pruning of isolated pixels." 
  actions: "Added halo_realign_prune primitive."
- task: dfadab01
  summary: "Apply colour-conditioned 4×4 patch motifs learned from training examples." 
  dsl: |
    return patch_dictionary_lookup(grid, library=PATCH_LIBRARY)
  gaps: "Required a primitive for colour-aware patch lookup and overlay." 
  actions: "Added patch_dictionary_lookup primitive."
- task: e12f9a14
  summary: "Expand 2×2 seeds into digit glyphs using collision-aware variant templates." 
  dsl: |
    return seeded_digit_expand(grid, variants=DIGIT_TEMPLATE_VARIANTS)
  gaps: "Needed a primitive to apply colour-specific template variants while respecting collisions." 
  actions: "Added seeded_digit_expand primitive."
- task: e3721c99
  summary: "Classify each colour-5 component by internal holes and recolour accordingly." 
  dsl: |
    return hole_classify_recolor(grid, target=5)
  gaps: "Required a primitive for hole counting and rule-based recolouring of components." 
  actions: "Added hole_classify_recolor primitive."
- task: e376de54
  summary: "Align coloured line families to the median footprint across rows, columns, or diagonals." 
  dsl: |
    return median_line_alignment(grid)
  gaps: "Needed a primitive to score orientations, choose the median line, and rebuild each line to match its pattern." 
  actions: "Added median_line_alignment primitive."
- task: e8686506
  summary: "Derive row colour signatures inside the bounding box and emit the mapped miniature template." 
  dsl: |
    return signature_sequence_lookup(grid, patterns=PATTERN_TO_OUTPUT)
  gaps: "Required a primitive for signature extraction and template lookup with fallback." 
  actions: "Added signature_sequence_lookup primitive."
- task: e87109e9
  summary: "Match each digit block to the nearest training mask and overlay the stored diff pattern." 
  dsl: |
    return digit_nn_overlay(grid, samples=_SAMPLE_DATA)
  gaps: "Needed a primitive for block extraction, mask comparison, and diff overlay." 
  actions: "Added digit_nn_overlay primitive."
- task: edb79dae
  summary: "Detect the legend, infer digit templates, and refill the framed region accordingly." 
  dsl: |
    return legend_template_fill(grid, frame_color=5)
  gaps: "Required a primitive wrapping block-size inference, legend decoding, and template rendering." 
  actions: "Added legend_template_fill primitive."
- task: eee78d87
  summary: "Classify the centre neighbourhood and pick the matching 16×16 template (plus/H/X)." 
  dsl: |
    return neighbor_template_dispatch(grid, templates=TEMPLATES)
  gaps: "Needed a primitive for neighbourhood counting and template selection." 
  actions: "Added neighbor_template_dispatch primitive."
- task: f560132c
  summary: "Relocate the four components by quadrant-aware offsets and orientation-specific rotations." 
  dsl: |
    return offset_oriented_remap(grid)
  gaps: "Required a primitive to rank components, compute offsets, rotate masks, and reassemble the canvas." 
  actions: "Added offset_oriented_remap primitive."
- task: f931b4a8
  summary: "Cycle row/column patterns with fallback borrowing when zero-signature rows appear." 
  dsl: |
    return borrow_cycle_tiling(grid)
  gaps: "Needed a primitive encapsulating signature grouping, borrow logic, and tiling reconstruction." 
  actions: "Added borrow_cycle_tiling primitive."
- task: faa9f03d
  summary: "Clean noise then apply closures, flanked infill, row extensions, and six-tail propagation." 
  dsl: |
    return composite_bridge_repair(grid)
  gaps: "Required a primitive orchestrating the staged clean-up and bridge propagation pipeline." 
  actions: "Added composite_bridge_repair primitive."
- task: fc7cae8d
  summary: "Crop the main component, rotate 90° CCW, and optionally mirror based on edge dominance." 
  dsl: |
    return conditional_rotate_flip(grid)
  gaps: "Needed a primitive for component extraction, rotation, and conditional mirroring." 
  actions: "Added conditional_rotate_flip primitive."
- task: aa4ec2a5
  summary: "Annotate each colour-1 component with segment-aware framing that preserves internal holes." 
  dsl: |
    let comps = components(grid, color=1)
    foreach comp in comps:
      segment_frame(grid, comp, frame_color=2, hole_color=6, interior_color=8)
    return grid
  gaps: "Needed a primitive capturing per-row framing with hole detection around components." 
  actions: "Added segment_frame primitive."
- task: abc82100
  summary: "Classify every cell via a hand-crafted feature vector and 1-NN over the provided training grids." 
  dsl: |
    return cell_knn_classifier(grid, training_examples=TRAIN_DATA, categorical_idx=CATEGORICAL_IDX)
  gaps: "Required a primitive to train/apply a per-cell kNN classifier driven by engineered features." 
  actions: "Added cell_knn_classifier primitive."
- task: b0039139
  summary: "Extract the colour-4 stencil and replicate it across counted colour-3 segments with orientation-aware spacing." 
  dsl: |
    return segment_tiling(grid, separator_color=1, template_color=4, repeat_color=3)
  gaps: "Needed a primitive that segments by all-1 dividers and rebuilds the tiled pattern." 
  actions: "Added segment_tiling primitive."
- task: b10624e5
  summary: "Infer ornament colours around each 2-component and expand them with centre-aware horizontal/vertical halos." 
  dsl: |
    let comps = components(grid, color=2)
    return ornament_template_expand(grid, comps)
  gaps: "Needed a primitive that captures the ornament replication with centre guards and colour de-duplication." 
  actions: "Added ornament_template_expand primitive."
- task: b5ca7ac4
  summary: "Detect 5×5 rings, split them by outer colour, and lane-pack them toward opposing borders without overlap." 
  dsl: |
    return ring_lane_pack(grid, ring_size=5)
  gaps: "Required a primitive for colour-aware lane packing of ring components." 
  actions: "Added ring_lane_pack primitive."
- task: b6f77b65
  summary: "Decode vertical segment strings and emit the matching digit templates with corrected alignment." 
  dsl: |
    return segment_digit_lookup(grid, mapping=MAPPING)
  gaps: "Needed a primitive that performs segment-code lookup into pre-learned templates." 
  actions: "Added segment_digit_lookup primitive."
- task: b99e7126
  summary: "Recover the minority macro tile and repaint every masked position with its 3×3 pattern." 
  dsl: |
    return macro_mask_completion(grid)
  gaps: "Needed a primitive for mask-guided macro tile completion." 
  actions: "Added macro_mask_completion primitive."
- task: b9e38dc0
  summary: "Grow the wedge component toward the barrier while respecting orientation and barrier clamping." 
  dsl: |
    return segmented_wedge_fill(grid)
  gaps: "Required a primitive for orientation-aware wedge propagation with barrier guards." 
  actions: "Added segmented_wedge_fill primitive."
- task: bf45cf4b
  summary: "Tile the multicolour component wherever the mask component is active, replicating its bounding box." 
  dsl: |
    return mask_pattern_tiling(grid)
  gaps: "Needed a primitive for mask-driven pattern tiling." 
  actions: "Added mask_pattern_tiling primitive."
- task: c4d067a0
  summary: "Bottom-align block columns and stack them per instruction columns with learned spacing." 
  dsl: |
    return column_instruction_stack(grid)
  gaps: "Required a primitive orchestrating column alignment and instruction-guided stacking." 
  actions: "Added column_instruction_stack primitive."
- task: 67e490f4
  summary: "Scan two-colour squares, pick the motif, and recolour components using matched shapes elsewhere." 
  dsl: |
    return two_colour_scan(grid)
  gaps: "Added a primitive for two-colour motif scanning with shape-based recolouring." 
  actions: "Introduced two_colour_scan primitive."
- task: 6e453dd6
  summary: "Slide zero components against the 5-column and tag rows when a background gap precedes the zero block." 
  dsl: |
    return slide_gap(grid)
  gaps: "Needed a primitive combining sliding with gap-based highlighting." 
  actions: "Added slide_gap primitive."
- task: 6e4f6532
  summary: "Map dual-color objects to markers using prelearned templates keyed by component signatures." 
  dsl: |
    return canonical_template(grid)
  gaps: "Added a primitive for marker-based template placement." 
  actions: "Introduced canonical_template primitive."
- task: 6ffbe589
  summary: "Crop the active block, inspect its color triad, and apply the matching rotation recipe." 
  dsl: |
    return color_dispatch_rotate(grid)
  gaps: "Needed a primitive for color-aware rotation dispatch." 
  actions: "Added color_dispatch_rotate primitive."
- task: 71e489b6
  summary: "Identify zero tips and apply guarded halos while pruning stray ones." 
  dsl: |
    return tip_halo(grid)
  gaps: "Added a primitive for tip detection plus halo drawing." 
  actions: "Introduced tip_halo primitive."
- task: 7491f3cf
  summary: "Inspect the left/centre panel shapes and apply either the cross overlay or block template before copying right." 
  dsl: |
    return panel_dispatch(grid)
  gaps: "Needed a primitive to dispatch between cross and block overlays based on panel shapes." 
  actions: "Added panel_dispatch primitive."
- task: 7666fa5d
  summary: "Fill corridor cells when both diagonally adjacent components bracket the position." 
  dsl: |
    return component_corridor(grid)
  gaps: "Added a primitive for diagonal corridor filling." 
  actions: "Introduced component_corridor primitive."
- task: 78332cb0
  summary: "Rotate separator-delimited blocks clockwise, cycle the start tile, and reassemble vertically/horizontally." 
  dsl: |
    return rotated_cycle(grid)
  gaps: "Needed a primitive for rotating and cycling block sequences." 
  actions: "Added rotated_cycle primitive."
- task: 7b0280bc
  summary: "Gather monochrome components of the two dominant colors, classify them with a learnt decision tree, and recolor matches." 
  dsl: |
    return component_tree_classify(grid)
  gaps: "Introduced a primitive for component-level decision trees." 
  actions: "Added component_tree_classify primitive."
- task: 7b3084d4
  summary: "Enumerate component placements with orientation variants to maximise the resulting perimeter/score." 
  dsl: |
    return perimeter_tiling(grid)
  gaps: "Needed a primitive for search-based component tiling." 
  actions: "Added perimeter_tiling primitive."
- task: 7b5033c1
  summary: "Order colours by their first occurrence and emit a vertical histogram of counts." 
  dsl: |
    return top_row_histogram(grid)
  gaps: "Added a primitive for top-row ordering histograms." 
  actions: "Introduced top_row_histogram primitive."
- task: 7b80bb43
  summary: "Regularise column/row masks with support-aware bridges to rebuild linework." 
  dsl: |
    return column_snap(grid)
  gaps: "Needed a primitive capturing the column-first cleanup with bridging heuristics." 
  actions: "Added column_snap primitive."
- task: 7c66cb00
  summary: "Extract legend prototypes and stamp them onto each target band from the bottom up." 
  dsl: |
    return stamp_bottom(grid)
  gaps: "Introduced a primitive for bottom-aligned stamping from prototype sections." 
  actions: "Added stamp_bottom primitive."
- task: 7ed72f31
  summary: "Reflect non-axis components across the nearest applicable symmetry axis marked by color 2." 
  dsl: |
    return nearest_axis_reflection(grid)
  gaps: "Needed a primitive for axis-based reflections with applicability checks." 
  actions: "Added nearest_axis_reflection primitive."
- task: 800d221b
  summary: "Combine heuristic thresholds with a kNN on geometric features to recolor transition regions between fringe colours." 
  dsl: |
    return hybrid_knn(grid)
  gaps: "Introduced a primitive for feature-based kNN recolouring." 
  actions: "Added hybrid_knn primitive."
- task: 80a900e0
  summary: "Extend diagonal handles into perpendicular stripes while guarding existing structure." 
  dsl: |
    return handle_extension(grid)
  gaps: "Captured the guarded handle extension in a dedicated primitive." 
  actions: "Added handle_extension primitive."
- task: 8698868d
  summary: "Match background tiles to shapes using column-weighted assignment and re-render the tiled grid." 
  dsl: |
    return column_priority_assignment(grid)
  gaps: "Needed a primitive for column-prioritised tile assignment." 
  actions: "Added column_priority_assignment primitive."
- task: 88bcf3b4
  summary: "Trace an accent path from the anchor column to the target component with heuristic corridor planning." 
  dsl: |
    return path_projection(grid)
  gaps: "Introduced a primitive for guided path projection." 
  actions: "Added path_projection primitive."
- task: 88e364bc
  summary: "Use a 5x5 template lookup to reposition colour-4 cells within digit blocks." 
  dsl: |
    return block_template_lookup(grid)
  gaps: "Needed a primitive for template-driven recolouring inside blocks." 
  actions: "Added block_template_lookup primitive."
- task: 89565ca0
  summary: "Rank stripes via dominance and fallback rules to build prefix histograms per colour." 
  dsl: |
    return refined_stripe(grid)
  gaps: "Added a primitive for dominance-based stripe summarisation." 
  actions: "Introduced refined_stripe primitive."
- task: 898e7135
  summary: "Infer the upscale factor from component areas and refill zero cavities before scaling." 
  dsl: |
    return dynamic_scale_fill(grid)
  gaps: "Needed a primitive for dynamic scaling with zero-fill." 
  actions: "Added dynamic_scale_fill primitive." 
- task: 8b7bacbf
  summary: "Fill enclosed zero cavities when boundary colours are within distance thresholds of key colours." 
  dsl: |
    return distance_filtered_fill(grid)
  gaps: "Introduced a primitive for distance-filtered cavity filling." 
  actions: "Added distance_filtered_fill primitive." 
- task: 8b9c3697
  summary: "Slide `2` components along scored corridors toward matched structures." 
  dsl: |
    return matched_corridors(grid)
  gaps: "Needed a primitive for corridor-based component matching." 
  actions: "Added matched_corridors primitive." 
- task: 8e5c0c38
  summary: "Remove asymmetric pixels so each colour is symmetric around its best horizontal axis." 
  dsl: |
    return global_color_symmetry(grid)
  gaps: "Added a primitive for global colour symmetry pruning." 
  actions: "Introduced global_color_symmetry primitive." 
- task: 8f215267
  summary: "Clear frame interiors, infer stripe counts from motifs, and repaint centred stripes." 
  dsl: |
    return striped_frames(grid)
  gaps: "Needed a primitive for frame stripe reconstruction." 
  actions: "Added striped_frames primitive." 
- task: 8f3a5a89
  summary: "Colour the accessible frontier and diagonal halo after pruning irrelevant `1` components." 
  dsl: |
    return accessible_halo(grid)
  gaps: "Introduced a primitive for guarded halo colouring of accessible regions." 
  actions: "Added accessible_halo primitive." 
- task: 9385bd28
  summary: "Apply legend-guided bounding-box recolouring with zero-pair handling and protection." 
  dsl: |
    return legend_guided_fill(grid)
  gaps: "Needed a primitive for legend-driven fills with guards." 
  actions: "Added legend_guided_fill primitive." 
- task: 97d7923e
  summary: "Fill sandwich columns only when matching caps and support heuristics agree." 
  dsl: |
    return selective_cap_fill(grid)
  gaps: "Introduced a primitive for selective column filling between matching caps." 
  actions: "Added selective_cap_fill primitive." 
- task: 981571dc
  summary: "Iteratively complete rows and columns from matching counterparts until the matrix is symmetric." 
  dsl: |
    return row_col_match(grid)
  gaps: "Needed a primitive for row/column completion with symmetry enforcement." 
  actions: "Added row_col_match primitive." 
- task: 9aaea919
  summary: "Interpret scoreboard instructions to recolor columns and extend plus counts." 
  dsl: |
    return instruction_board(grid)
  gaps: "Introduced a primitive for instruction-driven column recolouring." 
  actions: "Added instruction_board primitive." 
- task: 9bbf930d
  summary: "Adjust separator rows and sparse columns based on dominant-row comparisons." 
  dsl: |
    return separator_adjust(grid)
  gaps: "Needed a primitive for separator row/column adjustments." 
  actions: "Added separator_adjust primitive." 
- task: a251c730
  summary: "Dispatch by colour-frequency signature with a frame-projection fallback." 
  dsl: |
    return signature_dispatch(grid)
  gaps: "Added a primitive for signature-based output dispatch." 
  actions: "Introduced signature_dispatch primitive." 
- task: a25697e4
  summary: "Compact components by relocating the third colour into anchor holes with orientation heuristics." 
  dsl: |
    return compact_components(grid)
  gaps: "Needed a primitive for orientation-aware component compaction." 
  actions: "Added compact_components primitive." 
- task: a32d8b75
  summary: "Map instruction strips to sprite blocks with tail templates." 
  dsl: |
    return block_map_full(grid)
  gaps: "Introduced a primitive for instruction-driven block mapping." 
  actions: "Added block_map_full primitive." 
- task: a395ee82
  summary: "Replicate the template component across the marker lattice with colour swapping." 
  dsl: |
    return template_transfer(grid)
  gaps: "Needed a primitive for template transfer across marker lattices." 
  actions: "Added template_transfer primitive." 
- task: a47bf94d
  summary: "Place plus and X motifs on shared axes derived from square detections." 
  dsl: |
    return paired_plus_x(grid)
  gaps: "Added a primitive for paired plus/X motif placement." 
  actions: "Introduced paired_plus_x primitive." 
- task: a6f40cea
  summary: "Project frame borders with alternating stripe heuristics and gap closing." 
  dsl: |
    return augmented_projection(grid)
  gaps: "Needed a primitive for augmented border projection." 
  actions: "Added augmented_projection primitive." 
- task: 65b59efc
  summary: "Segment the board by 5-separators and fill each cell via template lookup with fallback dominant tiles." 
  dsl: |
    return mapped_tiles(grid)
  gaps: "Introduced a primitive for separator-based template mosaics." 
  actions: "Added mapped_tiles primitive."
