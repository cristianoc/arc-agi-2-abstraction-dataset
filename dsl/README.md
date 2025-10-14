# DSL Overview

This directory tracks the evolving abstraction DSL used while surveying the ARC‑AGI‑2 evaluation tasks. The current snapshot is encoded in `dsl_state.yaml` (version `68`, timestamp `2025-10-14T16:15:00Z`). Companion files:

- `DSL.md` – canonical description of the DSL conventions (typed operations, lambda syntax, validation tools).
- `check_lambda_types.py` – extracts typed-operation declarations and lambda snippets from every `abstractions.md`, emits typed stubs, runs `mypy`, and enforces the DSL/purity rules from the reference.
- `validate_dsl.py` – sanity-checks `dsl_state.yaml`, ensuring every typed operation lists a name/signature/tasks trio, forbids duplicate task ids, and prevents name/signature collisions.

`dsl_state.yaml` now records the *typed operations* that appear verbatim in abstraction notes (previously these were curated as “primitives”). Each entry is automatically scraped from the per-task documentation, so the YAML is the authoritative inventory of the operations in use.

## Typed Operations at a Glance

Typed operations are the task-level helpers declared inside each `## DSL Structure` section. They largely retain the CamelCase naming found in the abstractions—for example:

- `findAlignment : Grid -> Alignment` (template embedding pipelines),
- `extractComponents : Grid -> List Component` (reused across multiple component-focused tasks), and
- `paintComponent : Grid × Component × Color -> Grid` (component recolouring).

Because the list is auto-generated, no manual categorisation is maintained here. Use ad-hoc tooling (e.g. a quick grep) to group operations by prefix or usage when needed. `dsl_state.yaml` includes the task ids where each operation currently appears so you can trace definitions back to source.

## Types Inventory

To aid cross-task comparisons, `dsl_state.yaml` also lists every type token discovered inside the operation signatures, together with the tasks where each type appears. This inventory (under the new `types:` section) is generated automatically from the signatures, so high-level aliases such as `Grid`, `Component`, `TemplateId`, as well as container labels (`List`, `Dict`, `Optional`, …) will show up. Use it as a quick index when hunting for reusable data structures.

## Combinators

Only one combinator is currently standardised:

- `fold_repaint` – iterates over an ordered collection and applies an update callback to accumulate the repainted grid. See `DSL.md` for its signature and usage guidance.

No other control flow helpers are enforced by the DSL checker; task notes frequently document bespoke control logic inline.

## Updating the DSL

1. Update the task’s `abstractions.md` with the correct `## DSL Structure` entry (typed operations plus solver summary) and lambda snippet.
2. Regenerate or edit `dsl_state.yaml` so the new typed operations appear with accurate signatures, task ids, and an incremented `version`/`updated` timestamp.
3. Run the validation tools:
   - `python3 dsl/check_lambda_types.py tasks/**/abstractions.md`
   - `python3 dsl/validate_dsl.py`
4. Commit the changes once the validators succeed.

## Type-Checking Lambda Blocks

Every abstraction file now ends with a `## Lambda Representation` snippet.  To verify that those lambdas remain consistent with the DSL signatures, run:

```bash
python3 dsl/check_lambda_types.py tasks/**/abstractions.md
```

The script builds lightweight stubs for each abstraction, calls `mypy`, and reports undefined helpers, arity mismatches, or other drift.  It also enforces the lambda-style constraints documented in `DSL.md`.  Run the checker whenever the DSL summaries change to track both signature drift and lambda compliance.

## Validating the Registry

`python3 dsl/validate_dsl.py` verifies the structural integrity of `dsl_state.yaml`, specifically:

- every entry defines `name`, `signature`, and a non-empty `tasks` list,
- task lists do not contain duplicates, and
- no two entries share the same `(name, signature)` pair.

Use this script after regenerating the registry to catch copy/paste mistakes before committing.

## Future Work

- **Categorisation** – consider auto-generating grouped summaries or dashboards from `dsl_state.yaml` to make the large operation list easier to navigate.
- **Equivalence detection** – cluster operations that share identical signatures/semantics but diverge in naming across tasks.
- **Reference snippets** – link to canonical usage examples per high-value operation for quicker onboarding.

For more context on the dataset and methodology, see the repository root `README.md`.  Questions or improvements can follow the contribution process outlined in `CONTRIBUTING.md`.
