# Composing ARC Abstractions: Typed DSL Research Notes
## Design Principles, Properties, Examples, and Uses

### Abstract
A lightweight domain‑specific language (DSL) standardizes how ARC‑AGI‑2 task abstractions can describe operations and control flow used by solvers. The core ideas are: (i) list **typed operations** with precise signatures; (ii) capture the solver’s control flow as a restricted, **pure** “Lambda Representation”; (iii) keep a machine‑readable registry (`dsl_state.yaml`) that inventories the operations and type tokens appearing across tasks; and (iv) validate everything automatically with dedicated tooling. The result is a human‑legible, tool‑checkable substrate for comparing abstractions across puzzles, mining patterns, supervising symbolic or LLM‑assisted synthesis, and—most importantly—composing reusable abstraction pipelines.

---

## 1. Language overview

**Artifacts per task note**  
1. **DSL Structure** – a bullet list of *typed operations* of the form `name : Domain -> Codomain` (use `×` for Cartesian products), with names aligned to helper functions in the solver.  
2. **Lambda Representation** – a short, Python‑flavored snippet that mirrors solver control flow but remains within a small, pure subset (no mutation; no `for/while/try/with/class`; guard‑style `if` branches must return immediately; pure comprehensions allowed). Compliance is enforced by a checker that extracts the snippet and type‑checks it against generated stubs.

**Standard combinator.**
```text
fold_repaint : Grid × List Item × (Grid × Item -> Grid) -> Grid
```
Semantics: iterate items, repeatedly repainting a canvas via the provided update function (a fold). This captures the ubiquitous “walk a list and rewrite the grid” pattern without open‑coded loops.

**Registry.**  
The canonical, machine‑readable state lives in `dsl_state.yaml` and includes (a) the inventory of typed operations with the tasks where they appear and (b) a derived `types:` index collecting all type tokens used across signatures.

---

## 2. Design principles

1. **Human‑first, code‑adjacent.** Keep names and signatures aligned with the solver’s helpers so the prose maps directly to code while remaining readable to humans.  
2. **Purity and small core.** For the lambda sketch, forbid general loops and state mutation; prefer declarative combinators (`fold_repaint`) and pure expressions to avoid pseudo‑code drifting into full programming.  
3. **Typed by construction.** Type signatures (“Grid”, “Component”, “List Segment”, etc.) are part of the note itself and are type‑checked automatically against stubs generated from the note.  
4. **Single registry, global comparability.** The YAML registry serves as an authoritative index of operations and type tokens used across tasks, enabling cross‑task queries and statistics.  
5. **Automated validation.** A validator enforces structural invariants over the registry, including non‑empty task lists and uniqueness of `(name, signature)`.

---

## 3. Formalized properties and guarantees

**Syntactic & semantic discipline (Lambda Representation).**  
The checker enforces: single top‑level `def`, guard‑style `if` with immediate `return`, no mutation or loops, limited expression forms, and optional pure helper `def`s. This effectively approximates a simply‑typed, pure calculus embedded in Python syntax.

**Registry invariants.**  
Every typed operation must have a `name`, a `signature`, and at least one `task`; duplicates inside task lists are rejected; duplicate `(name, signature)` pairs are disallowed; and the `types:` section is checked for analogous issues. Exit status is non‑zero on any violation.

**Versioned, reproducible state.**  
The DSL README documents the current snapshot (version and timestamp) and the workflow for regenerating the registry and rerunning validators, supporting reproducible documentation that stays in lockstep with the code.

---

## 4. Worked examples

**Example A – mirror‑selection puzzle**  
Typed operations include:
- `bbox : Grid -> BBox`  
- `mirrorH : Grid × BBox -> Candidate`  
- `mirrorV : Grid × BBox -> Candidate`  
- `selectCandidate : Candidate × Candidate -> Candidate`  
- `flipOutput : Candidate -> Block`

The Lambda Representation composes these to compute a bounding box, form mirrored candidates, select by distance/ties, then flip to produce the block.

**Example B – repeating segments across a barrier**  
Operations:
- `collectSegments : Row -> List Segment`  
- `repeatSegments : Row × List Segment -> Row`

The Lambda Representation maps a pure `processRow` over all rows via a comprehension—illustrating pure, loop‑free structure.

**Example C – legend‑driven propagation using a fold**  
Operations:
- `iterComponents : Grid -> List Component`  
- `extractPalette : List Component -> Pattern`  
- `stripPalette : Grid × Pattern -> Grid`  
- `locateAnchors : Grid × Pattern -> List Anchor`  
- `propagatePattern : Grid × Pattern × Anchor -> Grid`

The Lambda Representation uses `fold_repaint` to iterate anchors and repaint the canvas—an idiomatic use of the standard combinator.

---

## 5. Tooling

- **`dsl/check_lambda_types.py`**: extracts typed‑operation bullets + lambda code blocks from `tasks/**/abstractions.md`, synthesizes type stubs (including a typed `fold_repaint`), and runs `mypy`.  
- **`dsl/validate_dsl.py`**: validates the global registry’s structure and uniqueness constraints.  
- **`dsl_state.yaml`**: the authoritative, regenerable inventory of typed operations, combinators, and types.

---

## 6. Uses

1. **Comparable, analyzable abstractions.** The global registry enables cross‑puzzle mining (e.g., which type tokens recur, which operation signatures cluster by task family).  
2. **Type‑safe documentation.** Notes become “executable specifications” in the sense that type‑checking will fail if a note’s operations or lambda sketch drift from the code base.  
3. **LLM supervision & synthesis.** Typed operation inventories and canonical combinators provide scaffolding for prompt‑ or retrieval‑augmented generation, and for ranking/screening candidate programs.  
4. **Ablations & pedagogy.** The pure lambda subset and explicit operation signatures make it straightforward to communicate solver logic, run ablation studies, and teach common patterns.  
5. **Regression/consistency checks.** The validators act as CI gates: if a solver changes, the corresponding note must be updated (or vice versa), helping the corpus remain trustworthy.

---

## 7. Limitations & open questions

- **Expressiveness vs. discipline.** The lambda subset forbids loops and mutation; this is great for clarity but may require factoring additional general combinators as the corpus grows.  
- **Naming divergence.** Because names mirror solver helpers, consistency depends on code hygiene; the registry’s uniqueness checks mitigate, but aliasing/equivalence detection across tasks remains future work.  
- **Executable vs. descriptive.** The DSL is intentionally *descriptive* (validated, not interpreted). Connecting it to a small evaluator (or a search engine over the typed operations) could further close the loop with program synthesis.

---

## 8. Minimal “how‑to”

- Write or update the **DSL Structure** and **Lambda Representation** in `tasks/<id>/abstractions.md`.  
- Regenerate/adjust `dsl_state.yaml` and bump its version/timestamp.  
- Run:
```bash
python3 dsl/check_lambda_types.py tasks/**/abstractions.md
python3 dsl/validate_dsl.py
```
Commit only if both pass.
