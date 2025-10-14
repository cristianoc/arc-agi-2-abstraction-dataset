# DSL Syntax Reference

**Purpose**: This document is the authoritative specification for writing abstraction notes in `tasks/**/abstractions.md`.

**For design motivation and theory**, see `DSL_Research_Note.md`.  
**For directory overview**, see `README.md`.

---

Every abstraction note must provide:

1. **DSL Structure** – typed operations with signatures
2. **Lambda Representation** – Python-syntax code using only approved pure constructs

The machine-readable registry (`dsl_state.yaml`) aggregates all operations across tasks. This reference ensures your notes remain valid and consistent.

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

Lambda representations use **Python syntax** to express **pure functional composition**. While the code looks like Python, it must stay within a restricted subset that has the semantics of simply-typed lambda calculus: no side effects, no mutation, no loops.

### Allowed Constructs

- **Single top-level function**: `def solve_<task>(grid: Grid) -> ...` (no decorators)
- **Pure helper functions**: Additional `def`s allowed if they follow these rules
- **Immutable bindings**: `x = expr` or `a, b = expr` (binding only, not reassignment)
- **Function calls**: Any operation from DSL Structure or standard library pure functions
- **Comprehensions**: `[f(x) for x in items]` for pure mapping/filtering
- **Lambda expressions**: `lambda x: expr` where both parameters and body are pure
- **Guard-style conditionals**:
  ```python
  if condition:
      return value1
  return value2
  ```
  Every `if`/`elif` branch must `return` immediately (no imperative control flow)
- **Pure expressions**: Arithmetic, comparisons, tuples, function composition
- **Final return**: Every function ends with `return <expression>`

### Forbidden Constructs

- **Loops**: No `for` or `while` statements (use comprehensions or `fold_repaint`)
- **Mutation**: No reassignment (`x = ...` after initial binding), no `list[i] = ...`, no `dict[k] = ...`
- **Stateful constructs**: No `try`, `with`, `class`, `global`, `nonlocal`
- **Attribute/subscript mutation**: No `obj.attr = ...`, no `seq[idx] = ...`
- **Decorators**: No `@decorator` on helpers
- **Side effects**: No I/O, no randomness, no mutation

**Rationale**: These restrictions ensure every lambda representation denotes pure composition, enabling equational reasoning and preventing hidden dependencies.

**To extend the allowed set**: Update `check_lambda_types.py` and document the change here first.

## Validation Workflow

After editing any `abstractions.md`:

```bash
# Type-check lambda representations
python3 dsl/check_lambda_types.py tasks/**/abstractions.md

# Validate registry structure  
python3 dsl/validate_dsl.py
```

### What `check_lambda_types.py` validates

1. **Syntax constraints**: Ensures lambda code uses only allowed constructs (no loops, mutation, etc.)
2. **Type consistency**: Generates stubs and runs `mypy` to check operation signatures match usage
3. **Operation existence**: Flags calls to undeclared operations

### What `validate_dsl.py` validates

1. **Registry completeness**: Every operation has `name`, `signature`, and non-empty `tasks`
2. **Uniqueness**: No duplicate `(name, signature)` pairs
3. **Task list integrity**: No duplicate task IDs within an operation's task list

**Both must pass** before committing. Fix errors by adjusting either the abstraction note or the registry.

## Standard Combinator: `fold_repaint`

The DSL includes one domain-specific higher-order function for the common "iterate and repaint" pattern.

### Signature
```
fold_repaint : Grid × List Item × (Grid × Item -> Grid) -> Grid
```

### Parameters
1. **Initial canvas**: Starting grid (often input or blank grid)
2. **Items to process**: Ordered list (components, anchors, patterns, etc.)
3. **Update function**: `f(grid, item) -> grid` that paints one item onto the canvas

### Semantics
Threads the grid through successive applications of the update function:

```python
# Equivalent imperative code (not allowed in lambda representations):
canvas = initial_grid
for item in items:
    canvas = update_fn(canvas, item)
return canvas
```

Or functionally: `f(...f(f(canvas, item₁), item₂)..., itemₙ)`

### When to Use
Use `fold_repaint` whenever a solver "walks a list and rewrites the canvas." This captures stateful iteration declaratively without explicit loops.

### Example
```python
def solve(grid):
    anchors = findAnchors(grid)
    pattern = extractPattern(grid)
    
    def paint(g, anchor):
        return placePattern(g, pattern, anchor)
    
    return fold_repaint(grid, anchors, paint)
```

See `DSL_Research_Note.md` for detailed motivation and additional examples.

## Contributor Checklist

When adding or modifying an abstraction note:

- [ ] **DSL Structure**: List all typed operations with correct signatures (`×` for products, `->` for functions)
- [ ] **Operation names**: Match helper function names in `solution.py` exactly (case-sensitive)
- [ ] **Lambda representation**: Use only allowed constructs (no loops, no mutation)
- [ ] **Type consistency**: Operations used in lambda code must be declared in DSL Structure
- [ ] **Registry update**: Add/modify entry in `dsl_state.yaml` (bump version/timestamp)
- [ ] **Validation**: Run both `check_lambda_types.py` and `validate_dsl.py` — both must pass
- [ ] **Commit**: Only proceed if validators succeed

### Extending the DSL

To add new allowed constructs:
1. Modify `check_lambda_types.py` to recognize the new syntax
2. Update this document's "Allowed Constructs" section
3. Add rationale for why the extension preserves purity
4. Get review before merging

---

**Questions or issues?** Open a discussion or PR. This document is the single source of truth for DSL syntax—keep it consistent with the checker implementation.
