# ARC 9bbf930d Abstraction Report

- **identity_solver** – baseline copy-through; fails immediately (0/3 train).
- **row_separator_solver** – moves the leading 6 for duplicated row bands; fixes separator edges but still misses column cues (2/3 train, first miss at train[2]).
- **full_solver** – extends with sparse-column heuristics (top/bottom capping + asymmetric boundary marking); passes all training examples and matches the production solver used in `arc2_samples/9bbf930d.py`.
