# Contributing to ARC-AGI-2 Abstraction Dataset

Thank you for your interest in contributing to the ARC-AGI-2 Abstraction Dataset! This document provides guidelines for contributing new tasks, abstractions, and improvements to the dataset.

## Repository Structure

The repository follows a consistent structure:

```
arc-agi-2-abstraction-dataset/
├── solutions/           # Task solution implementations
│   ├── <task_id>.py    # Individual task solvers
│   └── ...
├── abstractions/        # Abstraction implementations and reports
│   ├── task<task_id>_abstractions.py      # Abstraction functions
│   ├── task<task_id>_abstractions_report.md  # Analysis reports
│   └── ...
├── check_consistency.py # Repository consistency checker
└── README.md           # Main documentation
```

## Adding New Tasks

When adding new ARC-AGI-2 tasks to the dataset, ensure you include:

### Required Files

1. **Solution File**: `solutions/<task_id>.py`
   - Contains the main solver function `solve_<task_id>(grid)`

2. **Abstraction Code**: `abstractions/task<task_id>_abstractions.py`
   - Contains reusable abstraction functions
   - Modular design for easy composition
   - Common patterns: component detection, symmetry analysis, morphological operations

3. **Analysis Report**: `abstractions/task<task_id>_abstractions_report.md`
   - Summary of abstraction approaches tried

### Naming Conventions

- Solution files: `<task_id>.py`
- Abstraction files: `task<task_id>_abstractions.py`
- Report files: `task<task_id>_abstractions_report.md`
- Function names: `solve_<task_id>(grid)` and descriptive abstraction function names

## Consistency Checks

### Automated Verification

Before submitting contributions, run the consistency checker:

```bash
# Check repository consistency
python check_consistency.py
```

The consistency checker verifies:
- ✅ All solution files have corresponding abstraction files
- ✅ All abstraction files have corresponding solution files
- ✅ File counts match between directories
- ✅ Task IDs are consistent across directories
- ✅ Documentation reflects actual file counts
- ✅ No placeholder dates in CHANGELOG.md (e.g., "2025-01-XX")
- ✅ No placeholder text in documentation files

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
python -c "from solutions.<task_id> import solve_<task_id>; print('Import successful')"
```

## License

By contributing to this project, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to the ARC-AGI-2 Abstraction Dataset! Your contributions help advance research in program synthesis and abstraction learning.
