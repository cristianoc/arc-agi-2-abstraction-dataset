# Task 64efde09 – Abstraction Notes

- `identity`: simple copy-through baseline; scores 0/2 on train (fails immediately because the task requires adding shadows).
- `vertical_only`: casts accent colors horizontally from each tall motif; captures major structure but still 0/2 on train because horizontal motifs remain untreated.
- `full_shadow`: combines vertical and orientation-aware horizontal shadows, alternating directions across columns and handling near-top motifs; matches 2/2 train cases and runs cleanly on test inputs.

Final solver uses the `full_shadow` abstraction, with the vertical and horizontal passes mirroring the two-stage reasoning above.
