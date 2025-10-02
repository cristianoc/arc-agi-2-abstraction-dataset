# edb79dae Abstractions

- **primary_only** – expands each digit block using only the inferred target colour. It reaches 1/2 training cases because the lack of masking smears the digits and fails on the second example.
- **template_fill** – decodes the legend templates (mask + primary colour) and renders each block accordingly. It matches both training puzzles and is used in the final solver. The same pipeline produces a 21×21 answer for the evaluation input that preserves the layered frame structure while recolouring the digits.

The final solution combines automatic block-size detection, legend decoding and template-based rendering to recover both the palette mapping and the positional masks before repainting the region bounded by colour 5.
