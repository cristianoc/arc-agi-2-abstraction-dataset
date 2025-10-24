# Changelog

All notable changes to the ARC-AGI-2 Abstraction Dataset will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet


## [1.6.1] - 2025-10-24

### Added
- Abstraction reports (abstractions.md) for identity baseline bundles: 142ca369, 21897d95, 271d71e2, da515329

### Changed
- Synchronized all 120 per-task bundles from ArcGolf/arc2 into `tasks/<id>/`
- Normalized solver mains to match the DSL Lambda Representation exactly where applicable
- Ensured all `tasks/**/abstractions.md` pass the DSL lambda type-checker (`dsl/check_lambda_types.py`)

### Fixed
- a32d8b75: corrected Lambda Representation to conform to DSL purity rules and match the solver

### Repository status
- Total bundles: 120 (116 full + 4 identity baselines); documentation already reflected this count
- Known consistency exceptions: missing `abstractions.py` in 2 bundles (21897d95, 271d71e2)

## [1.6.0] - 2025-10-12

### Changed
- Restructured the repository into per-task bundles under `tasks/<id>/`
- Updated documentation and consistency checker to describe the new layout

### Removed
- Legacy `solutions/` and `abstractions/` directories (content now lives inside bundles)

## [1.5.0] - 2025-10-11

### Added
- Identity function baselines for 4 tasks where stable interpolating solutions are not yet available (142ca369, 21897d95, 271d71e2, da515329)
- Enhanced consistency checker to detect identity function baselines and distinguish them from full solutions

### Changed
- Task faa9f03d: Complete solver rewrite from nearest-neighbor classifier to rule-based approach with noise removal and selective closures (100% train accuracy)
- Dataset now contains 120 total solutions: 116 with full abstraction analysis + 4 identity baselines
- Updated documentation to reflect complete task coverage

### Removed
- Previous solutions for tasks 271d71e2 and da515329 (were encoding training examples; replaced with identity baselines)

## [1.4.0] - 2025-10-10

### Added
- 40 new ARC tasks for expanded dataset coverage (bringing total to 119, then 118 after removal)
- Complete abstraction analysis for 40 new tasks
- Abstraction reports for all 40 new tasks
- Working solutions approaching comprehensive coverage of ARC-AGI-2 evaluation set

### Changed
- Dataset expanded from 99 to 118 tasks (after one removal)
- Total abstractions: 118 Python files + 118 Markdown reports
- Total solutions: 118 Python files
- Updated 2 solutions (faa9f03d, and one other) to remove local JSON file dependencies

### Removed
- Task 21897d95 (removed from dataset)

## [1.3.0] - 2025-10-09

### Added
- 20 new ARC tasks for expanded dataset coverage
- Complete abstraction analysis for tasks: 7b80bb43, 800d221b, 8698868d, 88e364bc, 89565ca0, 8b9c3697, 981571dc, 9aaea919, 9bbf930d, a32d8b75, a47bf94d, abc82100, b5ca7ac4, b9e38dc0, c7f57c3e, cb2d8a2c, d59b0160, da515329, dbff022c, eee78d87, f560132c
- Abstraction reports for all 20 new tasks
- Working solutions for all 20 new tasks (all pass interpolation)
- Continued expansion of abstraction pattern coverage

### Changed
- Dataset expanded from 79 to 99 tasks
- Total abstractions: 99 Python files + 99 Markdown reports
- Total solutions: 99 Python files

### Removed
- Task 21897d95 (removed from dataset)

## [1.2.0] - 2025-10-06

### Added
- 16 new ARC tasks for expanded dataset coverage
- Complete abstraction analysis for tasks: 135a2760, 20270e3b, 2b83f449, 38007db0, 409aa875, 45a5af55, 7b5033c1, 7c66cb00, b99e7126, cbebaa4b, d35bdbdc, d8e07eb2, db0c5428, de809cff, dfadab01, e8686506
- Abstraction reports for all 16 new tasks
- Working solutions for all 16 new tasks (all pass interpolation)
- Continued expansion of abstraction pattern coverage
- Repository consistency checker script (`check_consistency.py`) for automated verification
- Contributing guidelines (`CONTRIBUTING.md`) with detailed contribution process

### Changed
- Dataset expanded from 63 to 79 tasks
- Total abstractions: 79 Python files + 79 Markdown reports
- Total solutions: 79 Python files

## [1.1.0] - 2025-10-05

### Added
- 13 new ARC tasks for comparison with grover-arc project
- Complete abstraction analysis for tasks: 136b0064, 1818057f, 247ef758, 291dc1e1, 2ba387bc, 36a08778, 7ed72f31, 8f215267, 8f3a5a89, aa4ec2a5, b0039139, b6f77b65, db695cfb
- Abstraction reports for all 13 new tasks
- Working solutions for all 13 new tasks (all pass interpolation)
- Strategic selection of tasks for benchmarking against existing ARC research

### Changed
- Dataset expanded from 50 to 63 tasks
- Total abstractions: 63 Python files + 63 Markdown reports
- Total solutions: 63 Python files

## [1.0.0] - 2025-10-02

### Added
- Initial release of ARC-AGI-2 Abstraction Dataset
- 50 ARC tasks with complete abstraction analysis
- 50 abstraction reports documenting the analysis process
- 50 working solutions (all pass interpolation)
- README with dataset overview and usage instructions
- MIT License

### Technical Details
- All 50 solvers pass interpolation (correctly solve all training examples)
- Initial batch focused on establishing baseline abstraction patterns
- Foundation for future dataset expansion

---

## Version History Summary

| Version | Date | Tasks | Description |
|---------|------|-------|-------------|
| 1.5.0 | 2025-10-11 | 120 | Complete ARC-AGI-2 coverage (116 full + 4 identity baselines) |
| 1.4.0 | 2025-10-10 | 118 | Added 40 tasks approaching full ARC-AGI-2 coverage |
| 1.3.0 | 2025-10-09 | 99 | Added 20 tasks for expanded coverage |
| 1.2.0 | 2025-10-06 | 79 | Added 16 tasks for expanded coverage |
| 1.1.0 | 2025-10-05 | 63 | Added 13 tasks for grover-arc comparison |
| 1.0.0 | 2025-10-02 | 50 | Initial release with baseline tasks |

## Future Plans

- [ ] Expand dataset with additional ARC tasks
- [ ] Add tasks that may not pass interpolation (for generalization testing)
- [ ] Include more diverse abstraction patterns
- [ ] Add performance benchmarks and evaluation metrics
