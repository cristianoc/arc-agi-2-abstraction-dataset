# Contributing to ARC-AGI-2 Abstraction Dataset

Thank you for your interest in contributing to the ARC-AGI-2 Abstraction Dataset! This document provides guidelines for contributing new tasks, abstractions, and improvements to the dataset.

## Repository Structure

The repository follows a consistent structure:

```
arc-agi-2-abstraction-dataset/
├── tasks/               # Self-contained task bundles
│   ├── <task_id>/
│   │   ├── solution.py          # Solver entry point (required)
│   │   ├── abstractions.py      # Reusable abstractions (optional for identity baselines)
│   │   ├── abstractions.md      # Abstraction report (optional for identity baselines)
│   │   └── task.json            # ARC task specification (optional helper file)
│   └── ...
├── check_consistency.py # Repository consistency checker
├── dsl/                # Typed DSL: docs, registry, validators
└── README.md           # Main documentation
```

## Adding New Tasks

When adding new ARC-AGI-2 tasks to the dataset, ensure you include:

### Required Files

1. **Task Bundle Directory**: `tasks/<task_id>/`
   - Create a new directory named with the ARC task ID.

2. **Solution File**: `tasks/<task_id>/solution.py`
   - Contains the main solver function `solve_<task_id>(grid)`
   - Should import cleanly (no side-effects on import)

3. **Optional Artefacts** (include any that strengthen your submission):
   - `tasks/<task_id>/task.json`: copy of the ARC task grids for convenience
   - `tasks/<task_id>/abstractions.py`: reusable abstraction helpers (component detection, symmetry analysis, morphological ops, etc.)
   - `tasks/<task_id>/abstractions.md`: short report describing the abstraction experiments and findings
   - Identity baselines may omit the optional files; stronger submissions should include them.

### Naming Conventions

- Bundle directory: `<task_id>`
- Solution file: `solution.py`
- Function name: `solve_<task_id>(grid)` and descriptive abstraction helper names

## Consistency Checks

### Automated Verification

Before submitting contributions, run the consistency checker:

```bash
# Check repository consistency
python check_consistency.py
```

The consistency checker verifies:
- ✅ Every bundle has a solver
- ✅ Optional artefacts are present when expected
- ✅ Task counts align with documentation
- ✅ No placeholder dates in CHANGELOG.md (e.g., "2025-01-XX")
- ✅ No placeholder text in documentation files

### DSL Validation (when editing abstractions.md)

If your PR adds or modifies any `tasks/**/abstractions.md` files, you must run the DSL validators and ensure they pass. The DSL captures solver control flow in a restricted, simply‑typed lambda subset (not Turing‑complete; no recursion). See `dsl/DSL.md` for the full spec.

```bash
# Type-check all lambda representations against declared operations
python3 dsl/check_lambda_types.py tasks/**/abstractions.md

# Validate the global DSL registry structure
python3 dsl/validate_dsl.py
```

PRs that touch DSL notes should include a brief note in the description stating that these checks passed.

## Documentation Updates

When adding new tasks:

1. **Update CHANGELOG.md**:
   - Add new version entry
   - List all new task IDs
   - Update file counts

2. **Update README.md** (if needed):
   - Update total task count
   - Add any new abstraction patterns discovered

3. **Update this CONTRIBUTING.md** (if needed):
   - Add new guidelines based on lessons learned
   - Update examples if patterns change

## Testing

### Local Testing

Before submitting:
```bash
# Run consistency check
python check_consistency.py

# Test individual solution (if you have test data)
python -c "from tasks.<task_id>.solution import solve_<task_id>; print('Import successful')"
```

## License

By contributing to this project, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to the ARC-AGI-2 Abstraction Dataset! Your contributions help advance research in program synthesis and abstraction learning.
