# Abstraction Summary — Task 36a08778

- **Identity baseline** – leaves the grid unchanged; 0/6 train matches.
- **Seed extension** – extends top-row 6 scaffolds downward without wrapping runs; 0/6 train matches (helps diagnose vertical structure only).
- **Scaffold unfiltered** – wraps every 2-run with the halo irrespective of connectivity; 2/6 train matches but over-paints unrelated regions.
- **Scaffold filtered (final)** – wraps only the 2-runs touched by the propagated scaffolds; 6/6 train matches and is used in the submitted solver.

Final refinement: scaffold filtered abstraction composed with the original grid reproduction (i.e., the solver) passes every available train case and produces plausible outputs for the test split.

