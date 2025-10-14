# Abstractions for ARC task b99e7126

- `identity`: direct copy of the input; fails every split (0/3 train) and serves as the control.
- `square_fill`: paint the minority tile into the entire 3x3 macro window that contains the observed tiles; fills the target window indiscriminately; every train case ends up over-painted (0/3).
- `mask_completion`: place the minority tile only where the tile’s majority colour appears, which matches all train/test/arc-gen pairs.

The final solver reuses the `mask_completion` abstraction: detect the minority tile, read its majority-colour mask to recover the intended 3×3 letter, align the mask with the observed tiles, and repaint every required cell with the original tile pattern.

## DSL Structure
- **Typed operations**
  - `splitMacroTiles : Grid -> MacroGrid` — partition the board into 3×3 tiles aligned on 4-cell strides and gather their frequencies.
  - `chooseMinorityTile : MacroGrid -> Tile` — select the least frequent non-background tile to use as the motif.
  - `alignMask : MacroGrid × Tile -> MotifAlignment` — detect where the minority tile already appears and infer the macro mask positions from its majority-colour layout.
  - `paintMotifTiles : Grid × Tile × MotifAlignment -> Grid` — copy the minority tile into every mask position within the macro grid.
- **Solver summary**: "Split the grid into macro tiles, choose the minority motif tile, align its majority-colour mask to the observed placements, and paint the motif tile at each masked position."

## Lambda Representation

```python
def solve_b99e7126(grid: Grid) -> Grid:
    macro_grid = splitMacroTiles(grid)
    motif = chooseMinorityTile(macro_grid)
    alignment = alignMask(macro_grid, motif)
    return paintMotifTiles(grid, motif, alignment)
```
