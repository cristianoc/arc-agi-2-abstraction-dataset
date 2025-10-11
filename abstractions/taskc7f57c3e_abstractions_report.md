# c7f57c3e Abstraction Notes

- **variant_a** – promotes the `mid` color to the highlight when it touches the pivot layer and only leaves `pivot` cells that border `c1`; matches 1/2 train cases (fails on train[1]).
- **variant_b** – mirrors `mid` blocks across the pivot layer and swaps them with highlight blocks; matches 1/2 train cases (fails on train[0]).
- **hybrid** – choose variant based on whether `mid` and pivot are adjacent; this refinement solves both train cases and is the solver shipped in `arc2_samples/c7f57c3e.py`.
