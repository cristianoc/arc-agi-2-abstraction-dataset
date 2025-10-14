# 269e22fb Abstractions

- `identity`: baseline copy of the input; fails immediately (train 0/5) despite keeping the test shapes embedded (2/2) because it never generates the 20×20 template.
- `align_no_swap`: aligns the grid to the canonical 20×20 template using dihedral transforms but keeps the color ordering fixed; succeeds on 4/5 train cases, misses the color-swapped scenario (test embeddings 1/2).
- `align_with_swap`: full alignment with optional color swap and complete dihedral coverage (including anti-diagonal reflection); passes all train cases 5/5 and embeds both test inputs 2/2.

**Final pipeline:** `align_with_swap` — detect the unique placement inside the canonical template, overwrite the slot, then invert the discovered transform and color mapping to recover the 20×20 output.

## DSL Structure
- **Typed operations**
  - `findAlignment : Grid -> Alignment` — search the canonical template for a dihedral transform and colour mapping that embeds the input (returns transform, mapping, position, pattern).
  - `writeTemplate : Alignment -> TemplateGrid` — copy the base template and write the transformed pattern into the detected slot.
  - `invertTransform : Alignment × TemplateGrid -> Grid` — apply the inverse dihedral transform to map the template back to input orientation.
  - `remapColors : Grid × Mapping -> Grid` — restore original colours via the reverse mapping.
- **Solver summary**: "Find the alignment of the input within the canonical template, write it into the base pattern, invert the transform, and remap colours to obtain the 20×20 output."
