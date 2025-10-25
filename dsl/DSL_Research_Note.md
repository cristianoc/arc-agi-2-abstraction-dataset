# CompDSL: A Compositional DSL for Grid Programs
## Design Principles, Properties, Examples, and Uses

### Abstract

**CompDSL** is a purely functional, simply-typed DSL for grid transformation programs (ARC tasks) embedded in disciplined Python. Every program is guaranteed to terminate with polynomial complexity—no mutation, recursion, or unbounded loops—while remaining analyzable through equational reasoning and static IterDepth metrics that bound runtime as O(n^d).

The DSL standardizes how ARC-AGI-2 task abstractions describe operations and control flow. Core components: (i) **typed operations** with precise signatures; (ii) **Lambda Representations** that capture control flow in a restricted pure subset of Python; (iii) a machine-readable registry (`dsl_state.yaml`) inventorying operations across tasks; and (iv) automated validation tooling. The result is a human-legible, tool-checkable substrate for comparing abstractions, mining patterns, supervising synthesis, and composing reusable abstraction pipelines.

---

## 1. Motivation: Why CompDSL?

### The Composition Problem

ARC-AGI tasks are solved by *composing* domain operations—extracting components, computing transformations, repainting grids. Whether a solution involves a linear pipeline `f₁ ∘ f₂ ∘ ... ∘ fₙ`, conditional branches, iteration over collections, or folds that accumulate state, the common thread is **composition**: building complex transformations from simpler, reusable operations. To understand, compare, and reuse these solutions, we need a **standard language for composition**.

### Why These Design Choices?

**Predictable** — Termination and polynomial complexity guaranteed by design.  
**Analyzable** — Equational laws, IterDepth metrics, and static checks enable formal reasoning.  
**Practical** — Uses standard Python syntax, leverages existing tools (AST, mypy), applies validator-enforced discipline for maintainable code.  
**Debuggable** — No hidden state, no action-at-a-distance.

**Why lambda calculus?**  
Lambda calculus is *the* canonical formalism for describing composition and function application. It gives us:
- **Function composition** as first‑class: `(f ∘ g)(x) = f(g(x))`
- **Higher‑order functions**: operations can take or return other operations
- **Abstraction and substitution**: binding variables to sub‑expressions
- **Referential transparency**: no hidden state or side effects

By grounding our DSL in lambda calculus, we inherit a mature theory of composition, equational reasoning, and a natural fit for both human reasoning and automated analysis.

**FAQ: Isn't lambda calculus universal?**  
The untyped lambda calculus is Turing-complete. CompDSL deliberately adopts a **simply-typed**, terminating subset: no general recursion or fixpoint combinators, no mutation, and no side effects. As a result, it is **not Turing-complete** (by design). This ensures:
- **Guaranteed termination**: All well-typed programs terminate
- **Polynomial complexity**: Static O(n^d) bounds via IterDepth metric
- **Strong normalization by construction**: No unbounded loops or stateful interaction

Iterative "state threading" that appears in ARC solvers is captured explicitly via the domain combinator `fold_repaint`, and domain operations (e.g., `extractComponents`, `paintComponent`) are treated as typed primitives rather than encoded in pure lambda terms.

**Python syntax for lambda calculus.**  
Rather than inventing new notation, we use **Python syntax** for familiarity and readability—researchers already know Python, and the solver implementations are written in Python. However, the *intent* is to capture **pure composition**, not arbitrary imperative Python. We achieve this by restricting to a small subset: only pure expressions, function calls, comprehensions, and guard-style conditionals. No loops, no mutation, no side effects. The result is Python that *looks* familiar but has the semantics of typed lambda calculus: every program is a composition of pure functions, and every expression denotes a value, not a sequence of state changes.

**Why add types?**  
While we could use untyped lambda calculus, ARC operations have *semantic constraints* that make types essential:
- `bbox : Grid -> BBox` extracts bounding boxes from grids
- `mirrorH : Grid × BBox -> Candidate` produces mirrored candidates
- Type mismatches (e.g., passing a `Segment` to `mirrorH`) are meaningless

Types provide:
1. **Documentation**: signatures communicate intent at a glance
2. **Safety**: static type checking catches composition errors before runtime
3. **Tooling**: type‑aware editors, autocomplete, and validation become possible
4. **Cross‑task analysis**: the registry of type tokens reveals patterns (e.g., "which tasks use `Component`?")

Thus we adopt **simply‑typed lambda calculus** as our foundation.

**Domain specificity: imperative paint operations.**  
ARC solutions commonly follow an imperative pattern:
```python
canvas = initialize_grid(...)
for item in items:
    canvas = paint(canvas, item)  # mutate or rewrite
return canvas
```
This "iterate and repaint" pattern is procedural and stateful in typical Python code. To express it *declaratively* in our pure lambda calculus, we introduce a **standard combinator**:

```text
fold_repaint : Grid × List Item × (Grid × Item -> Grid) -> Grid
```

**Semantics**: Given an initial grid (canvas), a list of items, and an update function `f : Grid × Item -> Grid`, `fold_repaint` iterates the items and threads the grid through successive applications: `f(...f(f(canvas, item₁), item₂)..., itemₙ)`.

This captures the ubiquitous "walk a list and rewrite the grid" pattern in a purely functional style—no explicit loops, no mutation. It's the *only* domain‑specific combinator in the DSL; everything else is standard typed lambda calculus.

---

## 2. Language overview

CompDSL consists of three interconnected artifacts that work together to create a verifiable, composable specification system.

### Key Language Properties

**Type System & Semantics**:
- Based on simply-typed lambda calculus (products, lists, `Optional[T]`, first-class functions)
- Strong normalization by construction: no general recursion or unbounded loops
- Call-by-value evaluation on pure expressions
- Supports equational reasoning: beta-reduction, fold laws, deforestation

**Complexity Guarantee**:
Every program runs in **O(n^d)** time where n = input cells and d = IterDepth—a primitive-agnostic measure of iteration nesting:
- +1 per comprehension generator
- +1 for `fold_repaint` + depth of its update function
- max(branch depths) for conditionals
- Propagates through helper calls

**Empirical distribution** (120 tasks): d=0 (4%), d=1 (39%), d=2 (53%), d=3 (3%)

This static metric provides **polynomial time bounds** without analyzing primitive implementations—treating all primitives as unit cost, the IterDepth alone bounds worst-case complexity.

### 2.1 DSL Structure (per task)

Each task's `abstractions.md` file contains a **DSL Structure** section: a bullet list of *typed operations* with signatures of the form `name : Domain -> Codomain`. Multiple input types are combined with `×` (Cartesian product), and operation names align with helper functions in the solver code. 

Example operations:
- `bbox : Grid -> BBox`  
- `mirrorH : Grid × BBox -> Candidate`  
- `fold_repaint : Grid × List Item × (Grid × Item -> Grid) -> Grid`

### 2.2 Lambda Representation (per task)

The **Lambda Representation** is a short, Python-syntax code snippet that captures the solver's control flow within a restricted pure subset. It uses familiar Python syntax but enforces lambda calculus semantics: no loops, no mutation, no side effects.

**Key restrictions**:
- Immutable bindings only (no reassignment)
- Comprehensions instead of `for` loops
- Guard-style conditionals (each branch must `return`)
- No stateful constructs (`try`, `with`, `class`)

A dedicated checker extracts these snippets, generates type stubs for all operations, and runs `mypy` to verify type consistency. This ensures the lambda representation correctly uses the declared operations—catching errors like calling a function with the wrong number or types of arguments, or composing operations whose types don't align.

**For complete syntax specification**, see `DSL.md` (Section: Lambda Representation).

### 2.3 Global Registry

The canonical, machine-readable state lives in `dsl_state.yaml` and serves as the single source of truth across all tasks. It contains:

1. **`operations:`** – inventory of all typed operations, each listing its signature and the tasks where it appears
2. **`types:`** – derived index of all type tokens used across signatures, enabling cross-task queries like "which tasks use type `Component`?"

This registry makes abstractions globally comparable and enables systematic analysis across the entire puzzle corpus.

---

## 3. Design principles

CompDSL follows five core principles that ensure both theoretical soundness and practical utility:

1. **Human-first, code-adjacent.** Keep names and signatures aligned with the solver's helpers so the specification maps directly to code while remaining readable to humans.  

2. **Purity and small core.** Forbid general loops and state mutation; use declarative combinators (`fold_repaint`) and pure expressions. This ensures every program terminates and enables equational reasoning.  

3. **Typed by construction.** Type signatures ("Grid", "Component", "List Segment", etc.) are specified explicitly and type-checked automatically against generated stubs. Catches composition errors at validation time.  

4. **Single registry, global comparability.** The YAML registry serves as an authoritative index of operations and type tokens used across tasks, enabling cross-task queries and pattern mining.  

5. **Automated validation.** Validators enforce purity constraints (AST checks), type consistency (`mypy`), and structural invariants (registry completeness, uniqueness). No manual verification needed.

These principles translate into concrete guarantees enforced by automated tooling, described next.

---

## 4. Formalized properties and guarantees

CompDSL enforces three classes of invariants through automated validation, ensuring correctness and consistency across the corpus.

### 4.1 Purity & Termination Discipline

The lambda checker enforces a restricted syntax that provides strong guarantees:

**Allowed constructs**:
- Pure function definitions with type signatures
- Guard-style `if/return` (all branches must return)
- Comprehensions (map/filter over finite collections)
- Tuples and pure expressions
- Positional-only lambdas
- Single combinator: `fold_repaint`

**Forbidden constructs**:
- `for`/`while` loops
- Mutation: `x[i] = v`, `obj.attr = v`
- Decorators, global state
- `try`/`except` for control flow
- Recursive function calls

**Guarantees provided**:
- **Referential transparency**: Every expression denotes a value, not a sequence of state changes
- **Guaranteed termination**: No unbounded loops or general recursion
- **Polynomial complexity**: Static IterDepth metric bounds runtime as O(n^d)
- **Equational reasoning**: Beta-reduction, fold laws, and deforestation apply

**For the complete list of allowed/forbidden constructs**, see `DSL.md` (Section: Lambda Representation).

### 4.2 Registry invariants

The registry validator (`validate_dsl.py`) enforces structural consistency:

- **Completeness**: every operation has a `name`, `signature`, and non-empty `tasks` list
- **Uniqueness**: no duplicate `(name, signature)` pairs across the registry
- **No redundancy**: task lists contain no duplicates
- **Type index integrity**: the `types:` section is derived correctly and checked for consistency

Any violation causes validation to fail with a non-zero exit status, acting as a quality gate.

### 4.3 Versioned, reproducible state

The DSL README documents:
- Current registry version and timestamp
- Workflow for regenerating `dsl_state.yaml`
- Procedures for running validators

This ensures the documentation stays synchronized with the solver implementations and supports reproducible analysis across registry snapshots.

Together, these guarantees make the DSL a trustworthy substrate for analysis, synthesis, and communication. The following examples demonstrate how these abstractions work in practice.

---

## 5. Worked examples

These examples illustrate how the DSL captures different compositional patterns found in ARC solvers.

### 5.1 Mirror-selection puzzle

**Task pattern**: Extract a region, generate mirrored candidates, select one, and transform the output.

**Typed operations**:
- `bbox : Grid -> BBox` — compute bounding box of non-background pixels
- `mirrorH : Grid × BBox -> Candidate` — horizontal mirror within bbox
- `mirrorV : Grid × BBox -> Candidate` — vertical mirror within bbox  
- `selectCandidate : Candidate × Candidate -> Candidate` — choose by distance metric
- `flipOutput : Candidate -> Block` — final transformation

**Lambda composition**:
```python
def solve(grid):
    box = bbox(grid)
    h_cand = mirrorH(grid, box)
    v_cand = mirrorV(grid, box)
    selected = selectCandidate(h_cand, v_cand)
    return flipOutput(selected)
```

This is pure function composition: `flipOutput ∘ selectCandidate ∘ (mirrorH, mirrorV) ∘ bbox`. No loops, no mutation—just a pipeline.

### 5.2 Repeating segments across a barrier

**Task pattern**: Process each row independently, collecting and repeating patterns.

**Typed operations**:
- `collectSegments : Row -> List Segment` — identify pattern segments in a row
- `repeatSegments : Row × List Segment -> Row` — replicate segments across the row

**Lambda composition**:
```python
def solve(grid):
    def processRow(row):
        segments = collectSegments(row)
        return repeatSegments(row, segments)
    return [processRow(row) for row in grid]
```

This demonstrates pure comprehension-based iteration—no explicit `for` loop with mutation. The list comprehension is the functional equivalent of `map(processRow, grid)`.

### 5.3 Legend-driven propagation using fold_repaint

**Task pattern**: Extract a "legend" (pattern library), find anchor points, then iteratively paint the pattern at each anchor.

**Typed operations**:
- `iterComponents : Grid -> List Component` — decompose grid into connected components
- `extractPalette : List Component -> Pattern` — build pattern dictionary from legend
- `stripPalette : Grid × Pattern -> Grid` — remove legend, leaving workspace
- `locateAnchors : Grid × Pattern -> List Anchor` — find where to place patterns
- `propagatePattern : Grid × Pattern × Anchor -> Grid` — paint pattern at anchor

**Lambda composition**:
```python
def solve(grid):
    components = iterComponents(grid)
    palette = extractPalette(components)
    canvas = stripPalette(grid, palette)
    anchors = locateAnchors(canvas, palette)
    
    def paint(g, anchor):
        return propagatePattern(g, palette, anchor)
    
    return fold_repaint(canvas, anchors, paint)
```

Here, `fold_repaint` captures the imperative "for each anchor, update canvas" pattern in a purely functional style. The canvas threads through successive applications: `paint(...paint(paint(canvas, a₁), a₂)..., aₙ)`. This is the DSL's *only* domain-specific construct—everything else is standard typed lambda calculus.

These examples show the *what*—how abstractions are expressed. The next section describes the *how*—the tooling that enforces correctness.

---

## 6. Tooling

CompDSL is supported by automated tooling that enforces correctness and maintains synchronization between documentation and code.

### 6.1 Purity & Type Checker: `check_lambda_types.py`

**Purpose**: Ensure lambda representations are pure, type-safe, and match declared operations.

**What it validates**:
1. **Purity constraints**: No loops, mutation, or recursion (AST-based checks)
2. **Type consistency**: Operation signatures match usage (`mypy` + generated stubs)
3. **Termination guarantee**: Only allowed constructs (guard if/return, comprehensions, `fold_repaint`)
4. **Operation existence**: All called operations declared in DSL Structure

**How it works**:
1. Extracts typed-operation bullets from `tasks/**/abstractions.md`
2. Synthesizes Python type stubs for each operation (including `fold_repaint`)
3. Parses lambda representation AST to enforce purity constraints
4. Runs `mypy` to verify type consistency

**Why it matters**: This makes CompDSL "executable documentation" rather than prose that can go stale. If a helper function signature changes in the code but not in the documentation (or vice versa), `mypy` will flag the mismatch. The purity checker ensures every program maintains the guarantees (termination, polynomial complexity) that make CompDSL analyzable.

### 6.2 Registry validator: `validate_dsl.py`

**Purpose**: Enforce structural invariants across the global registry.

**What it checks**:
- Every operation has required fields (`name`, `signature`, `tasks`)
- No duplicate `(name, signature)` pairs
- Task lists contain no duplicates
- Type index is consistent with operation signatures

**Why it matters**: The registry is the single source of truth for cross-task analysis. Validation ensures data quality, making it safe to write queries like "find all tasks using type `Component`" or "which operations appear in more than 5 tasks?"

### 6.3 Registry: `dsl_state.yaml`

**Role**: Authoritative, machine-readable inventory of all typed operations and type tokens across the corpus.

**Regeneration**: Rebuilt from individual task notes, versioned, and timestamped to support reproducible analysis across snapshots.

With these tools in place, the DSL becomes a practical infrastructure for several research and engineering applications.

---

## 7. Uses

The DSL enables several practical applications for researchers, educators, and AI systems.

### 7.1 Cross-task pattern mining

**Scenario**: A researcher wants to identify recurring abstraction patterns across the corpus.

**How the DSL helps**: Query the global registry to find:
- Which type tokens appear most frequently? (e.g., "30 tasks use `Component`, 15 use `Segment`")
- Which operations cluster by task family? (e.g., "mirror operations appear in symmetry tasks")
- Which tasks share operation signatures? (suggests similar solver strategies)

This turns a collection of isolated solvers into a queryable knowledge base of abstraction patterns.

### 7.2 Type-safe executable documentation

**Scenario**: A solver implementation changes—a helper function gets refactored or its signature modified.

**How the DSL helps**: The type checker immediately catches drift. If `mirrorH` changes from `Grid × BBox -> Candidate` to `Grid × BBox × Bool -> Candidate` in the code, but the documentation still shows the old signature, `mypy` fails. This enforces bidirectional consistency: documentation must track code, and vice versa.

Result: notes remain trustworthy specifications, not outdated prose.

### 7.3 LLM-assisted synthesis and supervision

**Scenario**: An LLM is prompted to generate a solver for a new ARC task.

**How the DSL helps**: 
- **Scaffolding**: Provide the LLM with typed operation signatures from similar tasks as building blocks
- **Validation**: Check generated lambda representations against the checker—reject syntactically invalid or poorly-typed proposals
- **Ranking**: Score candidates based on signature simplicity, type token reuse, or similarity to known patterns

The DSL provides a formal substrate for retrieval-augmented generation and post-hoc filtering of generated programs.

### 7.4 Pedagogy and communication

**Scenario**: Teaching common ARC solver patterns to humans or explaining solver behavior.

**How the DSL helps**: The pure lambda subset is minimal and readable. Instead of navigating 200 lines of imperative Python with nested loops and state, readers see a concise, declarative specification:

```python
return fold_repaint(canvas, anchors, lambda g, a: paint(g, pattern, a))
```

This clarity also supports ablation studies: swap out one operation, observe the effect—no hunting through stateful code.

### 7.5 Regression and consistency checking

**Scenario**: Continuous integration for a corpus of 100+ tasks.

**How the DSL helps**: The validators act as CI gates:
1. Developer modifies a solver → must update the corresponding `abstractions.md`
2. Run `check_lambda_types.py` → ensures lambda representation matches new code
3. Run `validate_dsl.py` → ensures registry consistency across corpus
4. Both pass → safe to merge

This workflow keeps the entire corpus in a known-good state, preventing documentation rot.

While the DSL provides substantial benefits, some challenges and opportunities for future work remain.

---

## 8. Limitations & future extensions

### Current Limitations

- **Not Turing-complete** (by design)—cannot express unbounded loops or stateful interaction. This is a feature, not a bug: it guarantees termination and polynomial complexity.

- **Assumes primitives are pure, total, and polynomial-time**—domain operations must respect these properties. The validators check composition structure but trust that primitives (e.g., `extractComponents`) themselves meet these requirements.

- **Naming divergence**—because names mirror solver helpers, consistency depends on code hygiene. The registry's uniqueness checks mitigate this, but aliasing/equivalence detection across tasks remains future work.

---

## 9. Contributor Quick Start

### Adding or updating a task's CompDSL specification

1. **Write the specification** in `tasks/<task_id>/abstractions.md`:
   - **DSL Structure** section: list typed operations with signatures
   - **Lambda Representation** section: pure Python snippet showing composition

2. **Update the registry**: Regenerate `dsl_state.yaml` to include the new/modified operations and bump version/timestamp

3. **Validate**:
   ```bash
   python3 dsl/check_lambda_types.py tasks/**/abstractions.md
   python3 dsl/validate_dsl.py
   ```

4. **Commit**: Only proceed if both validators pass with exit code 0

### Quick checklist

- [ ] Operation signatures use `×` for products, `->` for functions
- [ ] Lambda representation follows CompDSL constraints (no loops, no mutation, no recursion)
- [ ] All operation names match helper functions in `solution.py`
- [ ] Purity checker passes (no forbidden constructs)
- [ ] Type checker passes (`mypy` succeeds on generated stubs)
- [ ] Registry validator passes (no structural errors)

**For detailed syntax rules and troubleshooting**, see `DSL.md`.

This workflow ensures every change maintains the corpus's integrity and keeps documentation synchronized with code.
