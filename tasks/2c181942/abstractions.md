# Task 2c181942 – Abstraction Notes

- **identity** – Baseline copy-through; leaves all artefacts in place so it fails immediately on every train example (0/3).
- **axis-cross-no-shift** – Packs dominant colours around the detected vertical axis but skips the top-row widening tweak; succeeds on 2/3 trains and dies on the sample whose top arm needs to flare outward.
- **axis-cross-final** – Adds the selective top-row shift plus refined left/right arm placement; matches all train cases (3/3) and yields the submitted test prediction above.
