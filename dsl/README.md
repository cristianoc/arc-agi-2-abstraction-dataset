# CompDSL Directory

This directory contains the **CompDSL** specification, validators, and operation registry for ARC-AGI-2 task abstractions.

## What is CompDSL?

Purely functional, simply-typed DSL for grid programs. Guaranteed termination in O(n^d) time, no mutation/recursion/loops.

✓ Predictable ✓ Analyzable ✓ Practical ✓ Debuggable

## Documents

- **`DSL_Research_Note.md`** — Design rationale and theory (for researchers)
- **`DSL.md`** — Syntax specification (for contributors)
- **`dsl_state.yaml`** — Machine-readable operation registry

## Validation Tools

- **`check_lambda_types.py`** — Type-checks lambdas, enforces purity
- **`validate_dsl.py`** — Validates registry structure

## Quick Reference

### Language Subset (Python)

**✅ Allowed**:
- Pure function definitions with type signatures
- Guard-style `if/return` (all branches must return)
- Comprehensions (map/filter)
- Tuples and pure expressions
- Positional-only lambdas

**❌ Forbidden**:
- `for`/`while` loops
- Mutation: `x[i] = v`, `obj.attr = v`
- Decorators, global state
- `try`/`except` for control flow
- Recursive function calls

### Core Constructs

**`fold_repaint(canvas, items, update)`** — The only higher-order iterator.

```python
# Pattern: thread grid through update function
result = fold_repaint(canvas, cells, lambda g, c: paint_at(g, c, color))
```

**Comprehensions** — Pure map/filter over finite collections.

```python
coords = [(x, y) for x in range(w) for y in range(h) if grid[y][x] == target]
```

**Guard if/return** — All branches return immediately.

```python
def classify(x: int) -> str:
    if x < 0: return "negative"
    if x == 0: return "zero"
    return "positive"
```

### IterDepth Complexity Metric

| Construct | Contribution |
|-----------|--------------|
| Comprehension generator | +1 per generator |
| `fold_repaint` | +1 + depth of update function |
| Branches (`if`) | max(branch depths) |
| Helper calls | propagate callee depth |

**Empirical (120 tasks)**: d=0 (4%), d=1 (39%), d=2 (53%), d=3 (3%)

### Typed Operations

Example: `extractComponents : Grid -> List Component`

See `DSL.md` for format specifications.

## Contributor Workflow

1. Edit `tasks/<task_id>/abstractions.md`
2. Update `dsl_state.yaml` (bump version)
3. Run: `python3 dsl/check_lambda_types.py tasks/**/abstractions.md && python3 dsl/validate_dsl.py`
4. Commit if both pass

See `DSL.md` for detailed checklist.
