# CompDSL Syntax Reference

Authoritative specification for writing CompDSL programs in `tasks/**/abstractions.md`.

CompDSL is a purely functional, simply-typed DSL for grid programs. Every program terminates in O(n^d) time with no mutation, recursion, or loops. Enforced via AST validation and type checking.

**See also**: `DSL_Research_Note.md` (theory), `README.md` (overview)

## Structure Requirements

Every abstraction note must provide:

1. **DSL Structure** — Typed operations with signatures (domain primitives)
2. **Lambda Representation** — Python-syntax code using only approved pure constructs

The machine-readable registry (`dsl_state.yaml`) aggregates all operations across tasks. This reference ensures your programs remain valid and consistent.

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

Python syntax restricted to pure functional composition. Based on simply-typed lambda calculus with call-by-value evaluation. Not Turing-complete by design—no recursion, guaranteed termination, O(n^d) complexity.

### Allowed

- Pure function definitions: `def solve_<task>(grid: Grid) -> ...`
- Immutable bindings: `x = expr` (no reassignment)
- Comprehensions: `[f(x) for x in items]`
- Lambdas: `lambda x: expr`
- Guard if/return: Each branch must return immediately
- Pure expressions: arithmetic, comparisons, tuples

### Forbidden

- Loops: `for`, `while`
- Mutation: `x[i] = ...`, `obj.attr = ...`
- Recursion: self/mutual recursion, fixpoint combinators
- Stateful: `try`, `with`, `class`, `global`, decorators
- Side effects: I/O, randomness

**Note**: Variable reassignment not currently enforced but should be avoided.

## Validation

```bash
python3 dsl/check_lambda_types.py tasks/**/abstractions.md
python3 dsl/validate_dsl.py
```

**`check_lambda_types.py`**: Syntax constraints, type consistency (mypy), operation existence  
**`validate_dsl.py`**: Registry completeness, uniqueness, task list integrity

Both must pass before committing.

## Standard Combinator: `fold_repaint`

```
fold_repaint : Grid × List Item × (Grid × Item -> Grid) -> Grid
```

Threads a grid through successive applications of an update function. Use when iteratively updating a canvas.

Example:
```python
def solve(grid):
    anchors = findAnchors(grid)
    pattern = extractPattern(grid)
    return fold_repaint(grid, anchors, lambda g, a: placePattern(g, pattern, a))
```

See `DSL_Research_Note.md` for more examples.

## Contributor Checklist

- [ ] DSL Structure: correct signatures (`×` for products, `->` for functions)
- [ ] Operation names match `solution.py` exactly (case-sensitive)
- [ ] Lambda representation uses only allowed constructs
- [ ] Registry updated in `dsl_state.yaml` (bump version)
- [ ] Both validators pass: `check_lambda_types.py` and `validate_dsl.py`

**Extending the DSL**: Modify `check_lambda_types.py`, update this doc, justify why it preserves purity.
