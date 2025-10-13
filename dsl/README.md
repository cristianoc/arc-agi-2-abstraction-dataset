# DSL Overview

This directory tracks the evolving abstraction DSL used while surveying the ARC‑AGI‑2 evaluation tasks.  The current DSL snapshot is described in `dsl_state.yaml` (version `66`, timestamp `2025-10-13T11:05:00Z`).  Two additional companion files capture the running analysis:

- `task_log.md` – narrative entries for every processed task, including the DSL sketch, gaps, and new primitive/combinator notes.
- `task_progress.yaml` – bookkeeping for processed versus yet-to-be-reviewed tasks.

The sections below summarise the structure recorded in `dsl_state.yaml`; consult that file for the authoritative list of primitive descriptions.

## Primitives at a Glance

Primitives fall broadly into the following families:

1. **Geometry & Masking** – low-level grid manipulation (`bbox`, `crop`, `components`, `normalize_orientation`, `align_template`, `apply_transform`).
2. **Template & Pattern Utilities** – reusable pattern logic for specific motifs (`template_lookup`, `segment_digit_lookup`, `macro_dual_ring_tiling`, `legend_template_fill`, `neighbor_template_dispatch`).
3. **Projection & Propagation** – operations that extend colours or structures across the grid (`propagate_stride`, `stripe_projection`, `halo_realign_prune`, `priority_digit_highlight`, `median_line_alignment`).
4. **Component Reassembly** – primitives that reposition, rotate, and recombine components (`stack_components`, `offset_oriented_remap`, `borrow_cycle_tiling`, `conditional_rotate_flip`).
5. **Heuristic Refinements** – task-specific scoring or clean-up pipelines (`composite_bridge_repair`, `partner_cavity_fill`, `balanced_ring_relocation`, `signature_sequence_lookup`, `digit_nn_overlay`).

Each primitive entry in `dsl_state.yaml` stores a `name` and short `description`.  When the log notes "Added `<primitive>`", that exact string is reflected in the YAML to keep nomenclature consistent.

## Combinators

Four combinators are currently defined:

- `branch` – conditional pipeline selection.
- `foreach` – apply a sub-pipeline to every element in a collection (rows, components, etc.).
- `first_success` – evaluate candidate pipelines until one returns a non-null result.
- `dispatch` – route to a pipeline keyed by a discrete classification.

No other control flow is in use; complex behaviour is implemented by composing primitives with these combinators.

## Updating the DSL

1. **Log the task** – append a new entry to `task_log.md` describing the solver behaviour, DSL sketch, gaps, and actions.
2. **Record state changes** – update `dsl_state.yaml` with any new primitives or combinators (bump the `version` and `updated` timestamp).
3. **Maintain progress** – mark the task as processed in `task_progress.yaml`.
4. **Commit** – capture the changes on the working branch (see existing commit messages for convention).

The expectation is that every new primitive/combinator mentioned in the log has a matching definition in the YAML file.  When deleting or renaming primitives, update historical log entries for clarity.

## Future Work

- **Categorisation** – consider auto-generating a grouped summary from `dsl_state.yaml` to keep this overview in sync.
- **Validation tooling** – a small checker could ensure `task_log.md` actions correspond to entries in `dsl_state.yaml`.
- **Reference snippets** – optionally link to canonical usage examples per primitive for easier reuse in future tasks.

For more context on the dataset and methodology, see the repository root `README.md`.  Questions or improvements can follow the contribution process outlined in `CONTRIBUTING.md`.
