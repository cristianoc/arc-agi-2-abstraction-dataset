# ARC task 97d7923e abstractions

- **identity** – left grids untouched; matches 0/3 train examples (first fail at train[0]) so unusable as a solver.
- **naive_column_fill** – fills every sandwiched column; fixes the missing column at train[0] but over-fills others (first fail train[0]) showing the need for contextual checks.
- **selective_cap_fill** – keeps the naive fill machinery but adds guards for upstream caps, tall mid runs at row 3, and right-edge thin towers; matches 3/3 train examples and is used for the final solver and test prediction.
