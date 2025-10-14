# Composing ARC Abstractions: Typed DSL Research Notes
## Design Principles, Properties, Examples, and Uses

### Abstract
A lightweight domain‑specific language (DSL) standardizes how ARC‑AGI‑2 task abstractions can describe operations and control flow used by solvers. The core ideas are: (i) list **typed operations** with precise signatures; (ii) capture the solver's control flow as a restricted, **pure** "Lambda Representation"; (iii) keep a machine‑readable registry (`dsl_state.yaml`) that inventories the operations and type tokens appearing across tasks; and (iv) validate everything automatically with dedicated tooling. The result is a human‑legible, tool‑checkable substrate for comparing abstractions across puzzles, mining patterns, supervising symbolic or LLM‑assisted synthesis, and—most importantly—composing reusable abstraction pipelines.

---

## 1. Motivation: Why a DSL for ARC abstractions?

**The composition problem.**  
ARC‑AGI tasks are solved by *composing* domain operations—extracting components, computing transformations, repainting grids. Whether a solution involves a linear pipeline `f₁ ∘ f₂ ∘ ... ∘ fₙ`, conditional branches, iteration over collections, or folds that accumulate state, the common thread is **composition**: building complex transformations from simpler, reusable operations. To understand, compare, and reuse these solutions, we need a **standard language for composition**.

**Why lambda calculus?**  
Lambda calculus is *the* canonical formalism for describing composition and function application. It gives us:
- **Function composition** as first‑class: `(f ∘ g)(x) = f(g(x))`
- **Higher‑order functions**: operations can take or return other operations
- **Abstraction and substitution**: binding variables to sub‑expressions
- **Referential transparency**: no hidden state or side effects

By grounding our DSL in lambda calculus, we inherit a mature theory of composition, equational reasoning, and a natural fit for both human reasoning and automated analysis.

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

The DSL consists of three interconnected artifacts that work together to create a verifiable, composable specification system.

### 2.1 DSL Structure (per task)

Each task's `abstractions.md` file contains a **DSL Structure** section: a bullet list of *typed operations* with signatures of the form `name : Domain -> Codomain`. Multiple input types are combined with `×` (Cartesian product), and operation names align with helper functions in the solver code. 

Example operations:
- `bbox : Grid -> BBox`  
- `mirrorH : Grid × BBox -> Candidate`  
- `fold_repaint : Grid × List Item × (Grid × Item -> Grid) -> Grid`

### 2.2 Lambda Representation (per task)

The **Lambda Representation** is a short, Python-flavored code snippet that captures the solver's control flow within a restricted pure subset:

**Allowed**: 
- Single top-level function definition
- Pure expressions and function calls
- List/dict comprehensions (pure)
- Guard-style `if` with immediate `return`
- Optional pure helper functions

**Forbidden**:
- Mutation (assignment to existing variables)
- Loops (`for`, `while`)
- Stateful constructs (`try`, `with`, `class`)

A dedicated checker extracts these snippets, generates type stubs for all operations, and runs `mypy` to verify type consistency. This ensures the lambda representation correctly uses the declared operations—catching errors like calling a function with the wrong number or types of arguments, or composing operations whose types don't align.

### 2.3 Global Registry

The canonical, machine-readable state lives in `dsl_state.yaml` and serves as the single source of truth across all tasks. It contains:

1. **`operations:`** – inventory of all typed operations, each listing its signature and the tasks where it appears
2. **`types:`** – derived index of all type tokens used across signatures, enabling cross-task queries like "which tasks use type `Component`?"

This registry makes abstractions globally comparable and enables systematic analysis across the entire puzzle corpus.

---

## 3. Design principles

1. **Human‑first, code‑adjacent.** Keep names and signatures aligned with the solver's helpers so the prose maps directly to code while remaining readable to humans.  
2. **Purity and small core.** For the lambda sketch, forbid general loops and state mutation; prefer declarative combinators (`fold_repaint`) and pure expressions to avoid pseudo‑code drifting into full programming.  
3. **Typed by construction.** Type signatures ("Grid", "Component", "List Segment", etc.) are part of the note itself and are type‑checked automatically against stubs generated from the note.  
4. **Single registry, global comparability.** The YAML registry serves as an authoritative index of operations and type tokens used across tasks, enabling cross‑task queries and statistics.  
5. **Automated validation.** A validator enforces structural invariants over the registry, including non‑empty task lists and uniqueness of `(name, signature)`.

These principles translate into concrete guarantees enforced by automated tooling, described next.

---

## 4. Formalized properties and guarantees

The DSL enforces three classes of invariants through automated validation, ensuring correctness and consistency across the corpus.

### 4.1 Lambda Representation discipline

The lambda checker enforces a restricted syntax that approximates simply-typed, pure lambda calculus embedded in Python:

- **Single entry point**: exactly one top-level `def` (the main transformation)
- **Pure expressions**: function calls, comprehensions, conditionals—no side effects
- **Guard-style conditionals**: `if` conditions must `return` immediately (no imperative branches)
- **No mutation**: variables are immutable after binding
- **No loops**: iteration only through comprehensions or higher-order functions like `fold_repaint`
- **Optional helpers**: additional pure `def`s are allowed for factoring sub-expressions

These restrictions guarantee referential transparency and enable equational reasoning about solver behavior.

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

The DSL is supported by automated tooling that enforces correctness and maintains synchronization between documentation and code.

### 6.1 Type checker: `check_lambda_types.py`

**Purpose**: Ensure lambda representations are type-safe and match declared operations.

**How it works**:
1. Extracts typed-operation bullets from `tasks/**/abstractions.md`
2. Synthesizes Python type stubs for each operation (including `fold_repaint`)
3. Extracts lambda representation code blocks
4. Runs `mypy` to verify type consistency

**Why it matters**: Catches drift between abstract specifications and actual solver implementations. If a helper function signature changes in the code but not in the documentation (or vice versa), `mypy` will flag the mismatch. This makes the DSL "executable documentation" rather than prose that can go stale.

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

## 8. Limitations & open questions

- **Expressiveness vs. discipline.** The lambda subset forbids loops and mutation; this is great for clarity but may require factoring additional general combinators as the corpus grows.  
- **Naming divergence.** Because names mirror solver helpers, consistency depends on code hygiene; the registry’s uniqueness checks mitigate, but aliasing/equivalence detection across tasks remains future work.  
- **Executable vs. descriptive.** The DSL is intentionally *descriptive* (validated, not interpreted). Connecting it to a small evaluator (or a search engine over the typed operations) could further close the loop with program synthesis.

---

## 9. Minimal "how‑to"

### Adding or updating a task's DSL specification

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
- [ ] Lambda representation is pure (no loops, no mutation)
- [ ] All operation names match helper functions in `solution.py`
- [ ] Type checker passes (`mypy` succeeds)
- [ ] Registry validator passes (no structural errors)

This workflow ensures every change maintains the corpus's integrity and keeps documentation synchronized with code.
