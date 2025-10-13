# Task 7491f3cf – Abstraction Report

- **copy_left** – Mirrors the left panel into the blank area. Fails on all cases because it never adds the cross/diagonal features required in the target digits.
- **cross_overlay** – Applies the cross-armed overlay using directional heuristics. Solves the diamond/cross layouts (4/5) but breaks on the block-style case where the template differs.
- **block_template** – Stamps a hard-coded block pattern; handles the block example but misses others (2/5).
- **final_solver** – Chooses between cross-overlay and block template based on panel shapes; passes all provided examples (5/5) and is used for submission.
