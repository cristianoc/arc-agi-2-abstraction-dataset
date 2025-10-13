# Task 13e47133 Abstraction Report

- **identity** – left inputs untouched; predictably fails immediately (0/3 train) because the task requires synthesising multi-colour glyphs from single anchor pixels.
- **templates_v1** – first template overlay attempt with missing strokes for colours 4 and 5; recovers one training pair but leaves gaps in the 4- and 5-glyphs (1/3 train, fails on train[0]).
- **templates_final** – fully patched glyph dictionary matching training layouts; overlays all anchors correctly and solves every training example (3/3 train). The induced test output preserves the structured digit mosaic and matches qualitative expectations.

The released solver uses the `templates_final` abstraction, which combines anchor detection with the corrected glyph atlas to reproduce the required multi-colour numerals.
