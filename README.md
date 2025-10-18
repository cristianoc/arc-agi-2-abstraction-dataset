# ARC-AGI-2 Abstraction Dataset

A dataset containing 120 ARC-AGI-2 evaluation tasks, each with the final solver, abstraction implementation, and analysis report bundled together. In total, **120 tasks** are currently bundled.

## Overview

This dataset contains solvers for all 120 ARC-AGI-2 **evaluation tasks**, generated using an automated approach combining coding agents with abstraction-refinement techniques.
Most solvers (116 out of 120) pass **interpolation** (i.e., they correctly solve all training examples) and include full abstraction analysis. For tasks where stable interpolating programs could not be found (142ca369, 21897d95, 271d71e2, and da515329), identity function baselines are provided as placeholders. This dataset continues to be expanded over time, and future tasks may not all pass interpolation.  
The solvers were refined starting from identity functions, and identity functions are left when no solution is found. For details on the refinement pipeline, see the companion [compositional-program-synthesis](https://github.com/cristianoc/compositional-program-synthesis) repository. Each task solver includes:

- **Task Solution**: The final working Python implementation
- **Abstraction Code**: Reusable abstraction functions and pipelines
- **Analysis Report**: Detailed report of the abstraction process and performance


## Directory Structure

```
arc-agi-2-abstraction-dataset/
├── tasks/               # Self-contained task bundles
│   ├── 195c6913/
│   │   ├── solution.py
│   │   ├── abstractions.py
│   │   └── abstractions.md
│   ├── 1ae2feb7/
│   │   ├── solution.py
│   │   ├── abstractions.py
│   │   └── abstractions.md
│   └── ...
├── dsl/                 # Typed DSL: docs, registry, validators
├── check_consistency.py # Dataset integrity checker
├── CHANGELOG.md
└── README.md            # This file
```

## DSL (Typed Abstractions)

The `dsl/` folder contains a typed DSL used to write and validate the per-task abstraction notes. It captures solver control flow as a restricted, pure subset of simply-typed lambda calculus:

- Not the full untyped lambda calculus (therefore not Turing-complete)
- No general recursion (no fixpoint/Y); all well-typed programs terminate
- Iteration over state is expressed with the domain combinator `fold_repaint`
- Domain operations (e.g., component extraction, repaint) are recorded as typed primitives in `dsl/dsl_state.yaml`

Documents:

- `dsl/README.md` – directory index and quick commands
- `dsl/DSL.md` – syntax/specification and contributor guide
- `dsl/DSL_Research_Note.md` – design rationale and theory background

Validation commands:

```bash
# Type-check all lambda representations against declared operations
python3 dsl/check_lambda_types.py tasks/**/abstractions.md

# Validate the global DSL registry structure
python3 dsl/validate_dsl.py
```

## Task Solutions

Each bundle in `tasks/<task-id>/` contains:

- `solution.py`: the final solver implementation. Most solvers (116 of 120) pass every training example; the remaining bundles ship identity baselines while better programs are in progress. Generalization to unseen test cases remains the key open challenge.
- `abstractions.py`: reusable abstraction pipelines (optional when only an identity baseline is available).
- `abstractions.md`: a markdown report describing the abstraction process (also optional for identity baselines).

## Abstraction Files

Each bundle ships its own abstraction artefacts:

- `abstractions.py` — reusable abstraction routines (component analysis, symmetry detection, morphological operations, etc.).
- `abstractions.md` — a human-readable report summarising experiments, performance, and failure analysis.

All `abstractions.md` files that include a DSL section follow the typed DSL specification described in `dsl/DSL.md` and are validated using the commands shown above.

Identity baselines omit these files; you can treat the bundle as an invitation to contribute a stronger abstraction in the future.

## Key Abstraction Patterns

The solutions employ various abstraction techniques:

1. **Component Analysis**: 4-connected component detection and analysis
2. **Symmetry Detection**: Axis-aligned and rotational symmetry identification
3. **Morphological Operations**: Dilation, erosion, and closing operations
4. **Geometric Reasoning**: Bounding box analysis and spatial relationships
5. **Color Analysis**: Dominant color detection and color-based segmentation
6. **Local Rules**: Neighborhood-based pattern matching and transformation

## Usage

### Running a Task Solution

```python
# Example: Running task 1ae2feb7 from its bundle
from importlib import import_module

solve_module = import_module("tasks.1ae2feb7.solution")
result = solve_module.solve_1ae2feb7(input_grid)
```

### Using Abstractions

```python
# Example: Using abstraction helpers
abstractions = import_module("tasks.1ae2feb7.abstractions")
result = abstractions.repeat_last_nonzero_block(grid)
```

### Checking Repository Consistency

A consistency checker script is included to verify the dataset integrity:

```bash
# Check consistency (basic)
python check_consistency.py

# Check consistency with verbose output
python check_consistency.py --verbose
```

The script verifies:
- Every bundle contains a solver implementation
- Abstraction code/report files are present when expected
- Identity baselines are correctly recognised
- Documentation reflects the actual task count

## Methodology

The solutions were generated using an automated approach that:

1. **Initial Analysis**: Examines the task structure and patterns
2. **Abstraction Design**: Creates reusable abstraction functions
3. **Iterative Refinement**: Tests and refines abstractions based on failures
4. **Evaluation**: Tests solutions against validation cases to determine which ones work


## Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{arc_agi_2_abstraction_2025,
  title={ARC-AGI-2 Abstraction Dataset},
  description={Generated solutions and abstractions for ARC-AGI-2 tasks},
  year={2025},
  url={https://github.com/cristianoc/arc-agi-2-abstraction-dataset}
}
```

## License

This dataset is released under the MIT License. See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Adding new tasks and abstractions
- Repository structure and naming conventions
- Running consistency checks
- Code quality guidelines
- Pull request process

Please feel free to submit issues, feature requests, or pull requests following the guidelines in CONTRIBUTING.md.

## Acknowledgments

We are grateful to:

- The ARC-AGI-2 challenge organizers for creating and stewarding the benchmark
- [François Chollet](https://github.com/fchollet) for encouraging deeper exploration of abstraction-refinement approaches
- [Michael Hodel](https://github.com/michaelhodel) for introducing the author to ARC, sparking formative discussions, and publishing the original ARC solver corpus ([arc-dsl](https://github.com/michaelhodel/arc-dsl))
- [Eric Pang](https://github.com/epang080516) for feedback on the abstraction refinement work and sharing DreamCoder-inspired ARC-AGI program synthesis ([arc_agi](https://github.com/epang080516/arc_agi), [blog post](https://ctpang.substack.com/p/arc-agi-2-sota-efficient-evolutionary))
- [Peter O'Hearn](http://www0.cs.ucl.ac.uk/staff/p.ohearn/) for ongoing conversations about ARC and reasoning in AI
- The broader ARC research community for continually sharing ideas, analyses, and solver techniques
