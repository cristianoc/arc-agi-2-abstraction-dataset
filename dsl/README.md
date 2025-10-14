# DSL Directory Index

This directory contains the typed DSL for ARC-AGI-2 task abstractions. 

**Current snapshot**: `dsl_state.yaml` version `68` (updated `2025-10-14T16:15:00Z`)

## Documents

- **`DSL_Research_Note.md`** – *Design rationale and motivation.* Read this to understand **why** the DSL exists, its theoretical foundations (typed lambda calculus), design principles, and practical applications. For researchers and evaluators.

- **`DSL.md`** – *Syntax reference and contributor guide.* Read this to learn **how** to write valid abstraction notes. Authoritative specification of allowed/forbidden constructs, operation format, and validation workflow. For active contributors.

- **`dsl_state.yaml`** – *Machine-readable registry.* Authoritative inventory of all typed operations and type tokens across the corpus, with task mappings.

## Validation Tools

- **`check_lambda_types.py`** – Type-checks lambda representations against declared operations. Extracts DSL structures, generates type stubs, runs `mypy`, enforces purity constraints.
- **`validate_dsl.py`** – Validates registry structure: required fields, uniqueness constraints, no duplicates.

`dsl_state.yaml` now records the *typed operations* that appear verbatim in abstraction notes (previously these were curated as “primitives”). Each entry is automatically scraped from the per-task documentation, so the YAML is the authoritative inventory of the operations in use.

## Quick Reference

### Typed Operations
Each task declares operations like:
- `extractComponents : Grid -> List Component`
- `paintComponent : Grid × Component × Color -> Grid`

`dsl_state.yaml` auto-generates the complete inventory with task mappings. See **`DSL.md`** for format specifications.

### Standard Combinator
- **`fold_repaint`** – iterates over a collection, threading state through an update function

See **`DSL.md`** for detailed signature and usage.

### Type Tokens
`dsl_state.yaml` indexes all types (`Grid`, `Component`, `List`, etc.) with their task occurrences, enabling cross-task queries.

## Contributor Workflow

**Quick version:**
1. Edit `tasks/<task_id>/abstractions.md` (DSL Structure + Lambda Representation)
2. Update `dsl_state.yaml` (bump version/timestamp)
3. Run validators: `check_lambda_types.py` and `validate_dsl.py`
4. Commit if both pass

**See `DSL.md` for detailed syntax rules and the complete contributor checklist.**

## Validation Commands

```bash
# Type-check all abstraction notes
python3 dsl/check_lambda_types.py tasks/**/abstractions.md

# Validate registry structure
python3 dsl/validate_dsl.py
```

Both must pass before committing. See **`DSL.md`** for what these tools check and how to fix common errors.

---

**For design rationale and use cases**, see **`DSL_Research_Note.md`**.  
**For syntax rules and how-to**, see **`DSL.md`**.  
**For general repository context**, see the root `README.md`.
