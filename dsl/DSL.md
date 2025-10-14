# DSL Reference

This document captures the conventions used in `tasks/**/abstractions.md`.  Every abstraction note should provide:

1. **DSL Structure** – a bullet list of typed operations.
2. **Lambda Representation** – a Python-flavoured snippet that mirrors the solver’s control flow while staying within a small set of approved constructs.

The latest machine-readable state lives in `dsl_state.yaml`; this reference explains how to keep the prose summaries consistent.

## Typed Operations

Each entry under “DSL Structure” follows the shape:

```
- `name : Domain -> Codomain` — short description.
```

Guidelines:

- Use the cartesian product symbol `×` for multi-argument domains, e.g. `Grid × Set Column`.
- Keep names exactly aligned with the helpers exposed in the solver code (case-sensitive).
- Describe the effect in one sentence; focus on semantics, not implementation.
- Avoid introducing new types ad hoc—reuse existing aliases (`Grid`, `Component`, `Anchors`, …) or add them to `dsl_state.yaml` before use.

## Lambda Representation

The lambda block is meant to resemble a simply typed lambda calculus while remaining readable to humans.  The `dsl/check_lambda_types.py` script enforces a restricted subset of Python syntax; every snippet must stay within these constructs:

- **Top-level function**: a single `def solve_<task>(grid: Grid) -> …` with no decorators.
- **Helper functions**: optional local `def` definitions are allowed, provided their bodies use only the constructs listed below.
- **Assignments**: `name = expression` or tuple-unpacking variants (`a, b = …`).  Right-hand sides must be expressions built from the allowed nodes.
- **Guard-style `if`**: short-circuit branches such as
  ```python
  result = attempt()
  if result is not None:
      return result
  ```
  Chained `elif` branches are permitted; every branch must end in an immediate `return`.
- **Loops**: *currently disallowed*.  `for`/`while` statements will trigger the purity checker—prefer comprehensions or helper combinators.  (Future relaxations may revisit this.)
- **Comprehensions**: list/generator comprehensions are permitted when they merely map/filter without side effects.
- **Anonymous functions**: zero-argument lambdas are allowed (e.g. for `max(..., key=lambda x: …)`), provided both the parameters and the body respect these rules.
- **Return**: the final statement must be `return <expression>`; expressions can consist of function calls, tuples, simple arithmetic/comparisons, comprehension literals, and nested conditionals.

Disallowed constructs include:

- `while`, `for`, `try`, `with`, `class`, and comprehensions containing disallowed expressions.
- Mutation of input data structures (e.g., `grid[r][c] = …`).
- Use of global or nonlocal statements.
- Assignments to attributes or subscripts (e.g., `result.attr = …`).
- Decorators on helper functions.

If the narrow subset feels too strict, update the checker and document the change here before relying on new constructs.

## Validation Workflow

Run the combined checker after editing any abstraction note:

```bash
python3 dsl/check_lambda_types.py tasks/**/abstractions.md
```

The tool:

1. Extracts typed operations and lambda snippets from every `abstractions.md`.
2. Emits Python stubs and runs `mypy` to verify the typed operations align with the solver helpers.
3. Verifies that each lambda snippet uses only the constructs enumerated above (flagging “purity violations” otherwise).

Fix reported errors before committing documentation updates.

## Combinators

Some recurring patterns are expressed through higher-order helpers.  These live alongside the primitives and can be referenced directly inside lambda snippets.

### `fold_repaint`

```
fold_repaint : Grid × List Item × (Grid × Item -> Grid) -> Grid
```

Parameters:

1. Initial grid (often the input grid or a copy).
2. Ordered collection of items to visit (components, anchors, glyph entries, …).
3. Update function that consumes the current grid and one item, returning the repainted grid.

Semantics:

```
acc = initial_grid
for item in items:
    acc = update(acc, item)
return acc
```

Use this combinator whenever the solver “walks a list of things and rewrites the canvas,” instead of open-coding loops in the lambda representation.

## Contributor Checklist

- [ ] Update `DSL Structure` entries alongside any solver change.
- [ ] Keep lambda snippets consistent with the solver’s control flow and the allowed syntax.
- [ ] Run the checker command above and ensure it passes.
- [ ] When broadening the allowed syntax, adjust `dsl/check_lambda_types.py` and this reference together.

For questions or adjustments, open a discussion or PR referencing this file so the guidelines remain consistent.
