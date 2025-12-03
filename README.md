# ARC-AGI-2 Abstraction Dataset

A dataset containing 120 ARC-AGI-2 evaluation tasks with solvers written in **CompDSL**—a purely functional, simply-typed DSL for grid transformation programs. Each solver is guaranteed to terminate with polynomial complexity bounds and maintains equational reasoning properties.

## How to run solvers and check output correctness

```
./test.py
```

This also produces `out/*.json` files containing the output, which can be plotted for visual inspection with:

```
virtualenv -p python3 .venv
. .venv/bin/activate
pip install -r requirements.txt
./plot.py out/0934a4d8.json
```

## What is CompDSL?

CompDSL is a purely functional, simply-typed DSL for grid programs embedded in disciplined Python. Every solver is guaranteed to terminate in O(n^d) time with no mutation, recursion, or unbounded loops.

**Core idea**: Write programs using only pure functions, comprehensions, and the single combinator `fold_repaint`—enforced via AST validators and type checking.

## Dataset Overview

This dataset contains solvers for all 120 ARC-AGI-2 **evaluation tasks**, generated using an automated approach combining coding agents with abstraction-refinement techniques.

**Status**: 116 of 120 solvers pass **interpolation** (correctly solve all training examples). Identity baselines are provided for the remaining 4 tasks (142ca369, 21897d95, 271d71e2, da515329) as placeholders for future improvements.

Each task bundle includes:

- **Task Solution** (`solution.py`): Final working Python implementation in CompDSL
- **Abstraction Code** (`abstractions.py`): Reusable abstraction functions and pipelines  
- **Analysis Report** (`abstractions.md`): Detailed abstraction process and DSL specification

For details on the refinement pipeline, see the companion [compositional-program-synthesis](https://github.com/cristianoc/compositional-program-synthesis) repository.


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

## CompDSL Specification

The `dsl/` directory contains the full specification, validators, and operation registry.

**Documentation**:
- `dsl/README.md` — Quick reference with syntax cheat sheet
- `dsl/DSL.md` — Authoritative specification for contributors
- `dsl/DSL_Research_Note.md` — Design rationale and theoretical foundations

**Validation**: Run `check_lambda_types.py` and `validate_dsl.py` in the `dsl/` directory. See `dsl/DSL.md` for details.

## Task Bundles

Each `tasks/<task-id>/` directory contains:

- **`solution.py`** (required): Solver function. 116 of 120 pass all training examples; 4 are identity baselines.
- **`abstractions.py`** (optional): Reusable helper functions (component analysis, symmetry detection, morphological ops).
- **`abstractions.md`** (optional): Report with DSL specification validated by `check_lambda_types.py`.

Identity baselines omit the optional files.

## Common Patterns

**Per-item local reasoning**: `fold_repaint` over objects, applying local masks  
**Global infer → local render**: First pass builds structure, second pass paints  
**Search/evaluation** (rare): Generate candidates, score, select best

**Domain abstractions**: Component analysis, symmetry detection, morphological ops, geometric/color reasoning, neighborhood rules.

## Usage

```python
# Run a solver
from tasks.1ae2feb7.solution import solve_1ae2feb7
result = solve_1ae2feb7(input_grid)

# Use abstraction helpers
from tasks.1ae2feb7.abstractions import repeat_last_nonzero_block
result = repeat_last_nonzero_block(grid)
```

Check repository consistency: `python check_consistency.py`


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
